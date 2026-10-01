import os
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import KnowledgeBaseItem, ErrorAnalysisLog, SystemSettings
from .rag_engine import retrieve_rag_context, seed_knowledge_base_if_empty
from .ai_service import analyze_error_with_rag, get_active_api_keys

SAMPLE_ERRORS = [
    {
        "name": "Django OperationalError: no such table",
        "framework": "Django",
        "raw_error": "django.db.utils.OperationalError: no such table: main.auth_user\nTraceback (most recent call last):\n  File 'manage.py', line 22, in <module>\n    main()\n  File 'manage.py', line 18, in main\n    execute_from_command_line(sys.argv)",
        "code_context": "# views.py\ndef user_list(request):\n    users = User.objects.all()\n    return render(request, 'users.html', {'users': users})"
    },
    {
        "name": "Python IndentationError",
        "framework": "Python",
        "raw_error": "IndentationError: expected an indented block after 'for' statement on line 14\n  File 'app.py', line 14\n    for item in items:\n    print(item)",
        "code_context": "def process_data(items):\n    for item in items:\n    print(item.name)"
    },
    {
        "name": "JS TypeError: Cannot read properties of undefined",
        "framework": "JavaScript",
        "raw_error": "Uncaught TypeError: Cannot read properties of undefined (reading 'map')\n    at UserList (UserList.js:18:24)\n    at renderWithHooks (react-dom.development.js:16305)",
        "code_context": "const UserList = ({ data }) => {\n    return (\n        <div>\n            {data.users.map(u => <p key={u.id}>{u.name}</p>)}\n        </div>\n    );\n};"
    },
    {
        "name": "CORS Policy Blocked Request",
        "framework": "API",
        "raw_error": "Access to fetch at 'http://localhost:8000/api/users/' from origin 'http://localhost:3000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.",
        "code_context": "fetch('http://localhost:8000/api/users/')\n  .then(res => res.json())\n  .then(data => console.log(data));"
    },
    {
        "name": "Docker Port 8080 Already Allocated",
        "framework": "DevOps",
        "raw_error": "Error response from daemon: driver failed programming external connectivity on endpoint web_app: Bind for 0.0.0.0:8080 failed: port is already allocated",
        "code_context": "# docker-compose.yml\nservices:\n  web:\n    image: nginx\n    ports:\n      - '8080:80'"
    }
]

def dashboard_view(request):
    seed_knowledge_base_if_empty()
    settings = SystemSettings.get_settings()
    keys = get_active_api_keys()

    kb_count = KnowledgeBaseItem.objects.count()
    analysis_count = ErrorAnalysisLog.objects.count()
    recent_logs = ErrorAnalysisLog.objects.all()[:5]

    has_api_key = bool(keys['gemini_key'] or keys['groq_key'])

    context = {
        'page_title': 'Dashboard - AI Technical Error Analyzer',
        'kb_count': kb_count,
        'analysis_count': analysis_count,
        'recent_logs': recent_logs,
        'sample_errors': SAMPLE_ERRORS,
        'has_api_key': has_api_key,
        'settings': settings,
    }
    return render(request, 'dashboard.html', context)

@csrf_exempt
def analyze_error_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    raw_error = request.POST.get('raw_error', '').strip()
    code_context = request.POST.get('code_context', '').strip()
    framework = request.POST.get('framework', 'Auto-Detect').strip()

    # File upload handling
    uploaded_file = request.FILES.get('error_file')
    if uploaded_file and not raw_error:
        try:
            content = uploaded_file.read().decode('utf-8', errors='ignore')
            raw_error = content
        except Exception as e:
            raw_error = f"[File Upload Read Error: {e}]"

    # Screenshot handling
    screenshot_file = request.FILES.get('screenshot_file')

    if not raw_error and not screenshot_file:
        return JsonResponse({'error': 'Please provide an error message or upload an error file/screenshot.'}, status=400)

    file_type = "text"
    if screenshot_file:
        file_type = "image"
    elif uploaded_file:
        file_type = "log_file"

    try:
        analysis_result = analyze_error_with_rag(
            raw_error=raw_error if raw_error else "[Screenshot Image Uploaded]",
            code_context=code_context,
            framework=framework,
            image_file=screenshot_file
        )

        # Save analysis log to database
        log_entry = ErrorAnalysisLog.objects.create(
            title=analysis_result.get('title', 'Error Analysis'),
            raw_error=raw_error if raw_error else '[Image Upload]',
            code_context=code_context,
            file_type=file_type,
            framework=framework,
            summary=analysis_result.get('summary', ''),
            explanation=analysis_result.get('explanation', ''),
            root_cause=analysis_result.get('root_cause', ''),
            solution_steps=analysis_result.get('solution_steps', []),
            code_suggestion=analysis_result.get('code_suggestion', ''),
            matched_kb_items=analysis_result.get('matched_kb_items', []),
            ai_model_used=analysis_result.get('ai_model_used', 'Smart RAG')
        )

        analysis_result['log_id'] = log_entry.id
        analysis_result['created_at'] = log_entry.created_at.strftime('%Y-%m-%d %H:%M:%S')

        return JsonResponse({'success': True, 'data': analysis_result})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def knowledge_base_view(request):
    seed_knowledge_base_if_empty()
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    items = KnowledgeBaseItem.objects.all()
    if query:
        items = items.filter(title__icontains=query) | items.filter(error_pattern__icontains=query) | items.filter(tags__icontains=query)
    if category and category != 'All':
        items = items.filter(category=category)

    context = {
        'page_title': 'RAG Knowledge Base - AI Technical Error Analyzer',
        'items': items,
        'categories': [c[0] for c in KnowledgeBaseItem.CATEGORY_CHOICES],
        'current_query': query,
        'current_category': category,
        'total_count': KnowledgeBaseItem.objects.count()
    }
    return render(request, 'knowledge_base.html', context)

@csrf_exempt
def add_knowledge_base_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    title = request.POST.get('title', '').strip()
    category = request.POST.get('category', 'General').strip()
    error_pattern = request.POST.get('error_pattern', '').strip()
    explanation = request.POST.get('explanation', '').strip()
    solution_steps = request.POST.get('solution_steps', '').strip()
    code_example = request.POST.get('code_example', '').strip()
    tags = request.POST.get('tags', '').strip()

    if not title or not error_pattern or not explanation or not solution_steps:
        return JsonResponse({'error': 'Title, error pattern, explanation, and solution steps are required.'}, status=400)

    item = KnowledgeBaseItem.objects.create(
        title=title,
        category=category,
        error_pattern=error_pattern,
        explanation=explanation,
        solution_steps=solution_steps,
        code_example=code_example,
        tags=tags,
        source="User Added"
    )

    return JsonResponse({
        'success': True,
        'message': 'Knowledge Base item added successfully!',
        'item': {
            'id': item.id,
            'title': item.title,
            'category': item.category
        }
    })

@csrf_exempt
def delete_knowledge_base_api(request, item_id):
    if request.method != 'DELETE' and request.method != 'POST':
        return JsonResponse({'error': 'DELETE or POST required'}, status=405)

    item = get_object_or_404(KnowledgeBaseItem, id=item_id)
    item.delete()
    return JsonResponse({'success': True, 'message': 'KB item deleted successfully.'})

def history_view(request):
    logs = ErrorAnalysisLog.objects.all()
    framework_filter = request.GET.get('framework', '')
    query = request.GET.get('q', '')

    if framework_filter and framework_filter != 'All':
        logs = logs.filter(framework=framework_filter)
    if query:
        logs = logs.filter(title__icontains=query) | logs.filter(raw_error__icontains=query)

    context = {
        'page_title': 'Analysis History - AI Technical Error Analyzer',
        'logs': logs,
        'framework_filter': framework_filter,
        'query': query,
    }
    return render(request, 'history.html', context)

def history_detail_api(request, log_id):
    log = get_object_or_404(ErrorAnalysisLog, id=log_id)
    data = {
        'id': log.id,
        'title': log.title,
        'raw_error': log.raw_error,
        'code_context': log.code_context,
        'file_type': log.file_type,
        'framework': log.framework,
        'summary': log.summary,
        'explanation': log.explanation,
        'root_cause': log.root_cause,
        'solution_steps': log.solution_steps,
        'code_suggestion': log.code_suggestion,
        'matched_kb_items': log.matched_kb_items,
        'ai_model_used': log.ai_model_used,
        'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    return JsonResponse({'success': True, 'data': data})

def export_analysis_api(request, log_id):
    format_type = request.GET.get('format', 'md')
    log = get_object_or_404(ErrorAnalysisLog, id=log_id)

    if format_type == 'json':
        data = {
            'title': log.title,
            'framework': log.framework,
            'raw_error': log.raw_error,
            'code_context': log.code_context,
            'explanation': log.explanation,
            'root_cause': log.root_cause,
            'solution_steps': log.solution_steps,
            'code_suggestion': log.code_suggestion,
            'ai_model': log.ai_model_used,
            'created_at': str(log.created_at)
        }
        response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="error_analysis_{log.id}.json"'
        return response
    else:
        steps_md = "\n".join([f"{i+1}. {step}" for i, step in enumerate(log.solution_steps)])
        md_content = f"""# {log.title}
**Framework:** {log.framework} | **Date:** {log.created_at.strftime('%Y-%m-%d %H:%M:%S')} | **AI Engine:** {log.ai_model_used}

## 1. Raw Error Message
```
{log.raw_error}
```

## 2. Explanation (ELI5)
{log.explanation}

## 3. Root Cause Analysis
{log.root_cause}

## 4. Step-by-Step Solution
{steps_md}

## 5. Code Suggestion
```
{log.code_suggestion}
```

---
*Generated by AI Technical Error Analysis System (RAG Augmented)*
"""
        response = HttpResponse(md_content, content_type='text/markdown')
        response['Content-Disposition'] = f'attachment; filename="error_analysis_{log.id}.md"'
        return response

def settings_view(request):
    settings = SystemSettings.get_settings()
    keys = get_active_api_keys()

    context = {
        'page_title': 'Settings & API Keys - AI Technical Error Analyzer',
        'settings': settings,
        'active_keys': keys,
    }
    return render(request, 'settings.html', context)

@csrf_exempt
def save_settings_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    settings = SystemSettings.get_settings()
    gemini_key = request.POST.get('gemini_api_key', '').strip()
    groq_key = request.POST.get('groq_api_key', '').strip()
    provider = request.POST.get('preferred_provider', 'auto').strip()
    top_k = request.POST.get('rag_top_k', '3').strip()

    settings.gemini_api_key = gemini_key
    settings.groq_api_key = groq_key
    settings.preferred_provider = provider
    try:
        settings.rag_top_k = int(top_k)
    except ValueError:
        settings.rag_top_k = 3

    settings.save()

    return JsonResponse({
        'success': True,
        'message': 'System settings and API keys updated successfully!'
    })

@csrf_exempt
def seed_kb_api(request):
    seed_knowledge_base_if_empty()
    return JsonResponse({'success': True, 'message': 'Knowledge Base verified & seeded.'})
