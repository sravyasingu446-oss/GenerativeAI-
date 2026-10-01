# 🚀 AI Technical Error Resolution & Analysis System

An intelligent, full-stack **RAG-Augmented AI Technical Error Analysis Platform** built with **Django**, **Google Gemini API**, **Groq LLM API**, and a custom **Vector Knowledge Base RAG Engine**.

The system ingests raw stack traces, code context, log files, or error screenshots, matches them against a domain-specific RAG Knowledge Base, and generates structured ELI5 explanations, root cause diagnostics, step-by-step resolution plans, and corrected code fixes.

---

## 🌟 Key Features

- 🧠 **Hybrid RAG Engine**: Performs tf-idf/cosine similarity vector retrieval over a seeded knowledge base to ground AI model responses with verified solutions.
- ⚡ **Multi-Provider AI Fallback**:
  1. **Google Gemini API** (`google-genai` SDK with multimodal image/screenshot support)
  2. **Groq LLM API** (`llama-3.3-70b-versatile` high-speed inference)
  3. **Built-in Hybrid RAG Synthesizer** (offline zero-dependency fallback engine)
- 📸 **Multimodal Error Analysis**: Upload stack trace `.log` / `.txt` files or error screenshots (`.png`, `.jpg`) for direct OCR and visual diagnostic processing.
- 📊 **Interactive Dashboard**: Pre-loaded with standard technical error test cases (Django OperationalError, Python IndentationError, React TypeError, CORS policy errors, Docker port binding issues).
- 📚 **Knowledge Base Manager**: Search, filter, add, and manage vector-grounded error resolution articles dynamically.
- 📜 **Historical Logs & Export**: Track historical analysis logs, filter by framework, and export comprehensive reports as **Markdown (`.md`)** or **JSON (`.json`)**.
- ⚙️ **Settings & API Key Management**: Easily switch providers and configure API keys via the web interface or `.env`.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend Framework** | Django 5.x, Python 3.10+ |
| **AI / LLM Integrations** | Google Gemini (`google-genai`), Groq (`groq`), Pillow (`PIL`) |
| **RAG & Search** | Vector Similarity Search (TF-IDF & Cosine Similarity), SQLite |
| **Frontend UI** | HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), JavaScript (ES6) |

---

## 📂 Project Architecture

```
ai-technical-error-application-system/
├── analyzer/
│   ├── ai_service.py        # Gemini & Groq API handlers + Fallback Synthesizer
│   ├── rag_engine.py        # Vector embedding, TF-IDF retriever & KB seeder
│   ├── models.py            # KnowledgeBaseItem, ErrorAnalysisLog & SystemSettings
│   ├── views.py             # Dashboard, REST APIs, KB, History & Settings views
│   ├── urls.py              # Application routing endpoints
│   └── static/
│       ├── css/style.css    # Premium glassmorphism design system
│       └── js/app.js        # Dynamic AJAX analysis runner & UI controller
├── error_analyzer/
│   ├── settings.py          # Django configuration & environment loader
│   └── urls.py              # Root URL router
├── templates/
│   ├── base.html            # Core layout & navigation shell
│   ├── dashboard.html       # Error analyzer interface & preset error cards
│   ├── history.html         # Analysis history modal & export buttons
│   ├── knowledge_base.html  # RAG database list & addition form
│   └── settings.html       # API key management UI
├── .env.example             # Environment configuration template
├── .gitignore                # Git exclusions file
├── manage.py                # Django CLI utility
├── requirements.txt         # Python dependency specification
└── test_app.py              # Standalone verification script
```

---

## ⚡ Quick Start & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sravyasingu446-oss/GenerativeAI-.git
cd GenerativeAI-
```

### 2. Set Up Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to create `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your optional API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
PREFERRED_AI_PROVIDER=auto
RAG_TOP_K=3
DJANGO_SECRET_KEY=django-insecure-ai-error-analyzer-key
DEBUG=True
```

*(Note: If no API key is provided, the platform automatically utilizes its built-in **Smart Hybrid RAG Synthesizer**)*

### 5. Run Migrations & Seed Knowledge Base

```bash
python manage.py makemigrations
python manage.py migrate
python test_app.py
```

### 6. Start Development Server

```bash
python manage.py runserver 127.0.0.1:8000
```

Open your browser and navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

---

## 🧪 Verification & Testing

Run the automated backend test suite to verify RAG vector retrieval and AI service response generation:

```bash
python test_app.py
```

---

## 📄 License

This project is open-source under the MIT License.
