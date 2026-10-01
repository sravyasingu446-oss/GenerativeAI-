import math
import re
from collections import Counter
from .models import KnowledgeBaseItem, SystemSettings

DEFAULT_SEED_ITEMS = [
    {
        "title": "Django OperationalError: no such table",
        "category": "Django",
        "error_pattern": "OperationalError no such table django_session auth_user sqlite3.OperationalError table missing migrations",
        "explanation": "Django is trying to query a database table that does not exist yet. This usually happens when model migrations haven't been created or applied to the database.",
        "solution_steps": "1. Run `python manage.py makemigrations` to generate migration scripts.\n2. Run `python manage.py migrate` to apply the migrations and create the missing database tables.\n3. Verify that your app is added to `INSTALLED_APPS` in settings.py.",
        "code_example": "# Terminal commands:\npython manage.py makemigrations\npython manage.py migrate",
        "tags": "django, sqlite, database, migration, operationalerror"
    },
    {
        "title": "Django TemplateDoesNotExist Error",
        "category": "Django",
        "error_pattern": "TemplateDoesNotExist django.template.exceptions.TemplateDoesNotExist template missing HTML rendering DIRS loader",
        "explanation": "Django cannot locate the HTML template file specified in your view rendering function.",
        "solution_steps": "1. Ensure the template file exists at the correct path (e.g. `templates/index.html` or `myapp/templates/myapp/index.html`).\n2. Check `TEMPLATES` configuration in `settings.py` and ensure `DIRS` includes `BASE_DIR / 'templates'` or `APP_DIRS: True` is enabled.\n3. Verify spellings of template names in your view return statement.",
        "code_example": "# settings.py\nTEMPLATES = [{\n    'BACKEND': 'django.template.backends.django.DjangoTemplates',\n    'DIRS': [BASE_DIR / 'templates'],\n    'APP_DIRS': True,\n}]",
        "tags": "django, templates, html, render, template_loader"
    },
    {
        "title": "Django IntegrityError: UNIQUE Constraint Failed",
        "category": "Django",
        "error_pattern": "IntegrityError UNIQUE constraint failed sqlite3.IntegrityError duplicate key primary key unique field database",
        "explanation": "You are trying to insert or save a database record with a value for a unique field (like username or email) that already exists in the database.",
        "solution_steps": "1. Use `get_or_create()` or `update_or_create()` instead of `create()` or `.save()` when duplicate entries might occur.\n2. Add try-except handling around database save operations.\n3. Check input forms for uniqueness validation before attempting database insertion.",
        "code_example": "# Instead of User.objects.create(username=name)\nuser, created = User.objects.get_or_create(username=name, defaults={'email': email})\nif not created:\n    # Handle existing record\n    pass",
        "tags": "django, database, unique, constraint, integrityerror"
    },
    {
        "title": "Python IndentationError: unexpected indent / expected an indented block",
        "category": "Python",
        "error_pattern": "IndentationError unexpected indent expected an indented block TabError inconsistent use of tabs and spaces",
        "explanation": "Python requires strict and consistent whitespace indentation (spaces or tabs) to define code blocks.",
        "solution_steps": "1. Ensure consistent line indentation (use 4 spaces per indentation level).\n2. Do not mix tabs and spaces in the same Python file.\n3. Use an IDE feature like 'Convert Indentation to Spaces'.",
        "code_example": "# Correct Indentation:\ndef calculate_total(items):\n    total = 0\n    for item in items:\n        total += item\n    return total",
        "tags": "python, indentation, syntax, whitespace"
    },
    {
        "title": "Python ModuleNotFoundError / ImportError",
        "category": "Python",
        "error_pattern": "ModuleNotFoundError No module named ImportError cannot import name package missing virtualenv pip install",
        "explanation": "Python cannot locate the package or module you are attempting to import.",
        "solution_steps": "1. Verify the package is installed in your active virtual environment: `pip install <package_name>`.\n2. Ensure your virtual environment is activated before running your script.\n3. Check for typos in module name and check `requirements.txt`.",
        "code_example": "# Terminal command:\npip install <package-name>\n# Example:\npip install requests django google-genai",
        "tags": "python, pip, import, module, virtualenv"
    },
    {
        "title": "JavaScript TypeError: Cannot read properties of undefined / null",
        "category": "JavaScript",
        "error_pattern": "TypeError Cannot read properties of undefined reading map length filter Cannot read property of null JavaScript React async API response",
        "explanation": "You are attempting to access a property or method on a variable that evaluates to `undefined` or `null`, often caused by asynchronous data fetching that hasn't completed yet.",
        "solution_steps": "1. Use optional chaining (`?.`) when accessing nested properties (e.g. `data?.items?.map(...)`).\n2. Provide default fallbacks (e.g., `const items = data?.items || []`).\n3. Add conditional checks or loading states before rendering components in React.",
        "code_example": "// Safe mapping with optional chaining & default empty array:\nconst userList = data?.users || [];\nuserList.map(user => <UserCard key={user.id} user={user} />);",
        "tags": "javascript, react, typeerror, async, optional_chaining"
    },
    {
        "title": "CORS Error: Access to XMLHttpRequest blocked by CORS policy",
        "category": "API",
        "error_pattern": "CORS policy Access-Control-Allow-Origin header missing fetch blocked XMLHttpRequest cross origin preflight OPTIONS request",
        "explanation": "The web browser blocked an API request because the backend server has not enabled Cross-Origin Resource Sharing (CORS) headers for the requesting domain.",
        "solution_steps": "1. Install and configure CORS headers on the backend server (e.g., `django-cors-headers` for Django or `cors` middleware for Express.js).\n2. Ensure response headers include `Access-Control-Allow-Origin: *` or your specific frontend domain.\n3. Include allowed HTTP methods (GET, POST, OPTIONS) and custom headers.",
        "code_example": "# Django settings.py (using django-cors-headers):\nINSTALLED_APPS += ['corsheaders']\nMIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')\nCORS_ALLOW_ALL_ORIGINS = True",
        "tags": "cors, api, javascript, backend, headers"
    },
    {
        "title": "Docker Port Already Allocated / Connection Refused",
        "category": "DevOps",
        "error_pattern": "Error response from daemon port is already allocated address already in use docker container failed to start port binding",
        "explanation": "Docker cannot bind a container port to the host machine because another service or container is already running on that host port.",
        "solution_steps": "1. Find and stop the process using the target port (e.g. `netstat -ano | findstr :8080` on Windows or `lsof -i :8080` on Linux).\n2. Change the host port mapping in docker-compose or docker run (e.g., `-p 8081:8080` instead of `8080:8080`).\n3. Stop lingering docker containers: `docker stop $(docker ps -q)`.",
        "code_example": "# docker-compose.yml modification:\nports:\n  - \"8081:8000\" # Maps host port 8081 to container port 8000",
        "tags": "docker, devops, ports, networking, container"
    },
    {
        "title": "Django CSRF Token Missing or Incorrect",
        "category": "Security",
        "error_pattern": "Forbidden 403 CSRF verification failed Token missing or incorrect csrf_token POST request form authentication security",
        "explanation": "Django rejected a POST/PUT/DELETE form request because a valid Cross-Site Request Forgery (CSRF) token was not sent with the request.",
        "solution_steps": "1. Add `{% csrf_token %}` inside your HTML `<form>` elements.\n2. For AJAX / Fetch API requests, include the `X-CSRFToken` header fetched from the `csrftoken` cookie or DOM element.\n3. For API views intended for third-party webhooks, use `@csrf_exempt` carefully.",
        "code_example": "<!-- In HTML Form -->\n<form method=\"post\" action=\"/submit/\">\n    {% csrf_token %}\n    <input type=\"text\" name=\"data\">\n    <button type=\"submit\">Submit</button>\n</form>",
        "tags": "django, csrf, security, auth, 403"
    }
]

def seed_knowledge_base_if_empty():
    """Seed initial Knowledge Base entries into DB if DB is empty."""
    if KnowledgeBaseItem.objects.count() == 0:
        for item in DEFAULT_SEED_ITEMS:
            KnowledgeBaseItem.objects.create(
                title=item['title'],
                category=item['category'],
                error_pattern=item['error_pattern'],
                explanation=item['explanation'],
                solution_steps=item['solution_steps'],
                code_example=item['code_example'],
                tags=item['tags'],
                source="System Built-in"
            )
        return True
    return False

def _tokenize(text):
    """Clean & tokenize input text into lowercase word tokens."""
    return re.findall(r'\b[a-zA-Z0-9_]{2,}\b', text.lower())

def retrieve_rag_context(error_query, top_k=None):
    """
    Pure Python TF-IDF Vector & Cosine Similarity RAG Retriever:
    1. Tokenizes documents and error query.
    2. Computes Term Frequency (TF) and Inverse Document Frequency (IDF).
    3. Calculates Cosine Similarity vectors.
    4. Returns top_k KnowledgeBaseItem matches with similarity scores.
    """
    seed_knowledge_base_if_empty()
    settings = SystemSettings.get_settings()
    if top_k is None:
        top_k = settings.rag_top_k or 3

    items = list(KnowledgeBaseItem.objects.all())
    if not items or not error_query.strip():
        return []

    query_tokens = _tokenize(error_query)
    if not query_tokens:
        return []

    # Build corpus of documents
    doc_tokens_list = [
        _tokenize(f"{item.title} {item.category} {item.error_pattern} {item.tags} {item.explanation}")
        for item in items
    ]

    num_docs = len(doc_tokens_list)

    # Compute Document Frequency (DF) for IDF calculation
    df = Counter()
    for doc_tokens in doc_tokens_list:
        unique_tokens = set(doc_tokens)
        for token in unique_tokens:
            df[token] += 1

    # Compute IDF vector
    idf = {}
    for token, count in df.items():
        idf[token] = math.log((1 + num_docs) / (1 + count)) + 1.0

    # Query vector (TF-IDF)
    q_counts = Counter(query_tokens)
    q_vec = {}
    q_norm_sq = 0.0
    for token, count in q_counts.items():
        if token in idf:
            weight = (count / len(query_tokens)) * idf[token]
            q_vec[token] = weight
            q_norm_sq += weight * weight
    q_norm = math.sqrt(q_norm_sq)

    if q_norm == 0:
        return []

    # Calculate similarity score for each document
    similarities = []
    for idx, doc_tokens in enumerate(doc_tokens_list):
        if not doc_tokens:
            similarities.append(0.0)
            continue

        d_counts = Counter(doc_tokens)
        dot_product = 0.0
        d_norm_sq = 0.0

        for token, count in d_counts.items():
            if token in idf:
                weight = (count / len(doc_tokens)) * idf[token]
                d_norm_sq += weight * weight
                if token in q_vec:
                    dot_product += q_vec[token] * weight

        d_norm = math.sqrt(d_norm_sq)

        if d_norm == 0:
            score = 0.0
        else:
            score = dot_product / (q_norm * d_norm)

        similarities.append(score)

    # Rank and select top_k items
    ranked_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)

    results = []
    for idx in ranked_indices[:top_k]:
        score = float(similarities[idx])
        item = items[idx]
        if score > 0.01 or len(results) == 0:
            results.append({
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "explanation": item.explanation,
                "solution_steps": item.solution_steps,
                "code_example": item.code_example,
                "tags": item.tags,
                "similarity_score": round(min(score, 1.0), 3)
            })

    return results
