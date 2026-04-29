# JobCopilot AI 🚀

JobCopilot AI is a powerful, AI-driven career assistant designed to help job seekers land their dream roles. By uploading your CV and providing a target job role, this Streamlit application uses advanced AI agents to analyze your profile, detect skill gaps, suggest CV improvements, and generate tailored interview preparation materials.

## ✨ Features

- **CV Parsing & Analysis:** Extracts structured data (skills, experience, education) directly from PDF resumes.
- **Job Match Scoring:** Compares your CV against your target role (and optional job description) to generate a match score out of 100.
- **Skill Gap Detection:** Identifies missing technical and soft skills and provides actionable recommendations.
- **CV Improvements:** Suggests ATS-optimized bullet points, a tailored professional summary, and formatting tips.
- **Interview Preparation:** Generates likely interview questions, sample answers tailored to your profile, and key Do's and Don'ts.
- **Premium User Interface:** Features a stunning, glassmorphic dark mode design for an optimal user experience.

## 🛠️ Tech Stack

- **Frontend:** Streamlit, Custom CSS (Glassmorphism, Plus Jakarta Sans, Syne)
- **Backend:** Python, `asyncio`, `httpx`
- **AI Engine:** Groq API (Powered by Llama-3.3-70b-versatile)
- **PDF Processing:** `pypdf2` / `pdfplumber` (via custom `cv_parser.py`)

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8+
- A valid [Groq API Key](https://console.groq.com/)

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/UmedAli123/JobCopilot-AI.git
   cd JobCopilot-AI
   ```

2. **Create a virtual environment (Optional but recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## 🎮 Running the Application

To start the JobCopilot AI dashboard, run the following command:

```bash
streamlit run app.py
```

The application will launch in your default web browser at `http://localhost:8501`.

## 🛡️ Privacy & Security

JobCopilot AI is a privacy-first application. It processes your CV in memory during the active session and does not store your personal data or files permanently.