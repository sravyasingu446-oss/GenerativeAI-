from django.db import models

class KnowledgeBaseItem(models.Model):
    CATEGORY_CHOICES = [
        ('Django', 'Django'),
        ('Python', 'Python'),
        ('JavaScript', 'JavaScript / React'),
        ('Database', 'Database / SQL'),
        ('DevOps', 'DevOps / Docker / K8s'),
        ('Security', 'Security & Auth'),
        ('API', 'REST API & Web'),
        ('General', 'General / Other'),
    ]

    title = models.CharField(max_length=255)
    error_pattern = models.TextField(help_text="Key error terms, exceptions, or patterns to match")
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='General')
    explanation = models.TextField(help_text="Simple ELI5 explanation of the error")
    solution_steps = models.TextField(help_text="Practical step-by-step instructions to resolve")
    code_example = models.TextField(blank=True, default="", help_text="Corrected code example or snippet")
    tags = models.CharField(max_length=255, blank=True, default="")
    source = models.CharField(max_length=100, default="System Built-in")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.category}] {self.title}"

class ErrorAnalysisLog(models.Model):
    title = models.CharField(max_length=255, default="Error Analysis")
    raw_error = models.TextField()
    code_context = models.TextField(blank=True, null=True, default="")
    file_type = models.CharField(max_length=50, default="text") # text, image, log
    framework = models.CharField(max_length=100, default="Auto-Detect")
    summary = models.TextField(blank=True, default="")
    explanation = models.TextField(blank=True, default="")
    root_cause = models.TextField(blank=True, default="")
    solution_steps = models.JSONField(default=list, blank=True)
    code_suggestion = models.TextField(blank=True, default="")
    matched_kb_items = models.JSONField(default=list, blank=True)
    ai_model_used = models.CharField(max_length=100, default="Smart RAG + AI")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class SystemSettings(models.Model):
    gemini_api_key = models.CharField(max_length=255, blank=True, default="")
    groq_api_key = models.CharField(max_length=255, blank=True, default="")
    preferred_provider = models.CharField(max_length=50, default="auto") # 'gemini', 'groq', 'auto'
    rag_top_k = models.IntegerField(default=3)
    temperature = models.FloatField(default=0.2)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return "System Settings"
