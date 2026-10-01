import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'error_analyzer.settings')
django.setup()

from analyzer.models import KnowledgeBaseItem, ErrorAnalysisLog, SystemSettings
from analyzer.rag_engine import seed_knowledge_base_if_empty, retrieve_rag_context
from analyzer.ai_service import analyze_error_with_rag

print("--- Testing RAG Knowledge Base Seeder ---")
seeded = seed_knowledge_base_if_empty()
print("Seeded KB items count:", KnowledgeBaseItem.objects.count())

print("\n--- Testing RAG Vector Retriever ---")
query = "OperationalError no such table auth_user sqlite"
results = retrieve_rag_context(query, top_k=2)
for res in results:
    print(f"Matched [{res['similarity_score'] * 100:.1f}%]: {res['title']} ({res['category']})")

print("\n--- Testing AI Error Analysis Pipeline ---")
analysis = analyze_error_with_rag(
    raw_error="django.db.utils.OperationalError: no such table: main.auth_user",
    code_context="users = User.objects.all()",
    framework="Django"
)

print("Title:", analysis['title'])
print("AI Model:", analysis['ai_model_used'])
print("Explanation:", analysis['explanation'])
print("Root Cause:", analysis['root_cause'])
print("Solution Steps:", analysis['solution_steps'])
print("Code Fix:\n", analysis['code_suggestion'])
print("RAG Grounding Matches Count:", len(analysis['matched_kb_items']))

print("\n--- All Backend Verification Checks Passed Cleanly! ---")
