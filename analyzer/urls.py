from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.dashboard_view, name='dashboard'),
    path('knowledge-base/', views.knowledge_base_view, name='knowledge_base'),
    path('history/', views.history_view, name='history'),
    path('settings/', views.settings_view, name='settings'),

    # APIs
    path('api/analyze/', views.analyze_error_api, name='api_analyze'),
    path('api/knowledge-base/add/', views.add_knowledge_base_api, name='api_kb_add'),
    path('api/knowledge-base/delete/<int:item_id>/', views.delete_knowledge_base_api, name='api_kb_delete'),
    path('api/history/<int:log_id>/', views.history_detail_api, name='api_history_detail'),
    path('api/history/<int:log_id>/export/', views.export_analysis_api, name='api_history_export'),
    path('api/settings/save/', views.save_settings_api, name='api_settings_save'),
    path('api/seed-kb/', views.seed_kb_api, name='api_seed_kb'),
]
