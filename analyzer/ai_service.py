import os
import json
import re
from PIL import Image
from dotenv import load_dotenv
from .models import SystemSettings
from .rag_engine import retrieve_rag_context

load_dotenv()

def get_active_api_keys():
    """Retrieve Gemini and Groq API keys from DB settings or environment variables."""
    settings = SystemSettings.get_settings()
    gemini_key = settings.gemini_api_key or os.getenv('GEMINI_API_KEY', '')
    groq_key = settings.groq_api_key or os.getenv('GROQ_API_KEY', '')
    provider = settings.preferred_provider or os.getenv('PREFERRED_AI_PROVIDER', 'auto')
    return {
        'gemini_key': gemini_key.strip(),
        'groq_key': groq_key.strip(),
        'provider': provider
    }

def analyze_error_with_rag(raw_error, code_context="", framework="Auto-Detect", image_file=None):
    """
    Main AI Error Analysis Pipeline:
    1. Retrieve RAG Knowledge Base context matching the error query.
    2. Try Gemini API or Groq API if keys are available.
    3. Fall back to Smart Hybrid RAG Synthesizer if no external API key is configured.
    4. Return structured analysis dictionary.
    """
    keys = get_active_api_keys()
    gemini_key = keys['gemini_key']
    groq_key = keys['groq_key']
    provider = keys['provider']

    # Retrieve relevant RAG entries
    search_text = f"{raw_error}\n{code_context}\n{framework}"
    rag_matches = retrieve_rag_context(search_text, top_k=3)

    # Format RAG context for prompt grounding
    rag_context_str = ""
    if rag_matches:
        rag_context_str = "RAG KNOWLEDGE BASE GROUNDING INFORMATION:\n"
        for i, match in enumerate(rag_matches, 1):
            rag_context_str += (
                f"Reference [{i}] - {match['title']} ({match['category']}):\n"
                f"  Explanation: {match['explanation']}\n"
                f"  Solution Steps: {match['solution_steps']}\n"
                f"  Code Snippet: {match['code_example']}\n\n"
            )

    # Attempt AI Providers
    result = None
    ai_model_name = "Smart RAG Knowledge Engine"

    # Strategy 1: Gemini API
    if (provider in ['auto', 'gemini']) and gemini_key:
        try:
            result = call_gemini_api(gemini_key, raw_error, code_context, framework, rag_context_str, image_file)
            ai_model_name = "Gemini 2.5 Flash + RAG"
        except Exception as e:
            print(f"[AI Service] Gemini API call failed: {e}")

    # Strategy 2: Groq API
    if not result and (provider in ['auto', 'groq']) and groq_key:
        try:
            result = call_groq_api(groq_key, raw_error, code_context, framework, rag_context_str)
            ai_model_name = "Groq Llama 3.3 + RAG"
        except Exception as e:
            print(f"[AI Service] Groq API call failed: {e}")

    # Strategy 3: Hybrid Smart RAG Fallback Engine
    if not result:
        result = generate_fallback_analysis(raw_error, code_context, framework, rag_matches)
        ai_model_name = "Hybrid RAG Synthesizer (Built-in)"

    result['matched_kb_items'] = rag_matches
    result['ai_model_used'] = ai_model_name
    return result

def call_gemini_api(api_key, raw_error, code_context, framework, rag_context_str, image_file=None):
    """Call Google Gemini API using google-genai package."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an expert AI Technical Error & Stack Trace Analyzer.
Analyze the following error message and provide a detailed, accurate, structured JSON analysis.

{rag_context_str}

USER ERROR DETAILS:
Framework / Tech Stack: {framework}
Error Message / Stack Trace:
```
{raw_error}
```

Associated Code Context:
```
{code_context if code_context else "None provided."}
```

REQUIRED JSON RESPONSE FORMAT (Respond strictly with valid JSON without markdown wrapping):
{{
    "title": "Short descriptive title of the error",
    "summary": "Brief 1-2 sentence overview of what went wrong",
    "explanation": "Clear ELI5 explanation of the error in simple language",
    "root_cause": "Detailed technical explanation of the underlying root cause",
    "solution_steps": [
        "Step 1 action...",
        "Step 2 action...",
        "Step 3 action..."
    ],
    "code_suggestion": "// Corrected code snippet or recommended code fix"
}}
"""

    contents = []
    if image_file:
        try:
            img = Image.open(image_file)
            contents.append(img)
        except Exception as e:
            print(f"Error loading screenshot image: {e}")

    contents.append(prompt)

    # Try gemini-2.0-flash or gemini-1.5-flash
    model_name = "gemini-2.0-flash"
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
    except Exception:
        model_name = "gemini-1.5-flash"
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )

    text_resp = response.text.strip()
    return parse_json_response(text_resp)

def call_groq_api(api_key, raw_error, code_context, framework, rag_context_str):
    """Call Groq API using groq package."""
    from groq import Groq

    client = Groq(api_key=api_key)
    prompt = f"""
You are an expert AI Technical Error Analyzer.
Analyze the following technical error using the provided Knowledge Base RAG grounding context.

{rag_context_str}

Framework: {framework}
Error: {raw_error}
Code Context: {code_context}

Output ONLY valid JSON adhering strictly to this schema:
{{
    "title": "Error Title",
    "summary": "Short summary",
    "explanation": "Simple language ELI5 explanation",
    "root_cause": "Root cause technical analysis",
    "solution_steps": ["Step 1", "Step 2", "Step 3"],
    "code_suggestion": "// Corrected code snippet"
}}
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a JSON-only technical error analysis engine."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    text_resp = chat_completion.choices[0].message.content.strip()
    return parse_json_response(text_resp)

def parse_json_response(text_resp):
    """Clean and parse JSON from model output."""
    # Strip markdown codeblocks if present
    cleaned = re.sub(r'^```(json)?', '', text_resp, flags=re.MULTILINE)
    cleaned = re.sub(r'```$', '', cleaned, flags=re.MULTILINE).strip()

    data = json.loads(cleaned)
    return {
        "title": data.get("title", "Technical Error Analysis"),
        "summary": data.get("summary", "Analysis completed."),
        "explanation": data.get("explanation", "The system analyzed the stack trace."),
        "root_cause": data.get("root_cause", "Root cause identified."),
        "solution_steps": data.get("solution_steps", []),
        "code_suggestion": data.get("code_suggestion", "")
    }

def generate_fallback_analysis(raw_error, code_context, framework, rag_matches):
    """
    High-quality Smart Hybrid RAG Synthesizer when no external API key is provided.
    Synthesizes RAG Knowledge Base articles & error patterns into structured response.
    """
    title = "Technical Error Analysis"
    summary = "System analyzed error log using RAG Knowledge Base patterns."
    explanation = "An error occurred during execution of your code or command."
    root_cause = "The system encountered an unexpected state, invalid syntax, or missing dependency."
    steps = [
        "1. Inspect the stack trace line numbers to pinpoint the failing line of code.",
        "2. Check recent code modifications and environment configuration files.",
        "3. Verify that all required packages and dependencies are installed."
    ]
    code_fix = "# Example check code\nprint('Debugging error details:', error)"

    if rag_matches and len(rag_matches) > 0:
        best_match = rag_matches[0]
        title = best_match['title']
        summary = f"Matched Knowledge Base pattern: {best_match['title']} ({best_match['category']})"
        explanation = best_match['explanation']
        root_cause = f"Based on RAG analysis of '{best_match['title']}', the issue stems from an unhandled exception or missing resource in {best_match['category']}."
        
        # Parse solution steps
        raw_steps = best_match['solution_steps'].split('\n')
        parsed_steps = [s.strip() for s in raw_steps if s.strip()]
        if parsed_steps:
            steps = parsed_steps
        
        if best_match.get('code_example'):
            code_fix = best_match['code_example']
    else:
        # Heuristic rules based on common error patterns
        err_lower = raw_error.lower()
        if 'no such table' in err_lower or 'operationalerror' in err_lower:
            title = "Database Migration / Table Missing Error"
            explanation = "Your application is attempting to query a database table that has not been created yet."
            root_cause = "Database schema is out of sync with application models."
            steps = [
                "Run `python manage.py makemigrations` to generate migration files.",
                "Run `python manage.py migrate` to apply schema updates to SQLite/PostgreSQL.",
                "Check that the app name is listed in `INSTALLED_APPS` in settings.py."
            ]
            code_fix = "python manage.py makemigrations\npython manage.py migrate"
        elif 'syntaxerror' in err_lower or 'indentationerror' in err_lower:
            title = "Syntax or Indentation Error"
            explanation = "Python encountered code syntax or whitespace indentation that violates language rules."
            root_cause = "Mismatched quotes, unclosed parentheses, or inconsistent tab/space indentation."
            steps = [
                "Locate the line number indicated in the traceback.",
                "Verify all opening brackets `(`, `[`, `{` have matching closing pairs.",
                "Ensure standard 4-space indentation per nesting level."
            ]
            code_fix = "# Check line indentation & closing parentheses\ndef fix_indentation():\n    return True"
        elif 'typeerror' in err_lower or 'undefined' in err_lower:
            title = "TypeError / Undefined Property Access"
            explanation = "Code attempted to invoke a method or access a property on an undefined or null variable."
            root_cause = "Variable was not initialized or asynchronous API fetch returned null/empty data."
            steps = [
                "Add defensive optional chaining `?.` before property access.",
                "Check if API request completed before accessing response fields.",
                "Set default initial state values (e.g. `const data = response || []`)."
            ]
            code_fix = "// Optional chaining example:\nconst title = data?.response?.title || 'Default Title';"

    return {
        "title": title,
        "summary": summary,
        "explanation": explanation,
        "root_cause": root_cause,
        "solution_steps": steps,
        "code_suggestion": code_fix
    }
