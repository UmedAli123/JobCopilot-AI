import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from cv_parser import extract_text_from_pdf
from agents import run_career_analysis

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JobCopilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Main background */
.stApp {
    background: radial-gradient(circle at 50% -20%, #1a233a 0%, #080b12 80%);
    color: #e8eaf0;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }

/* Hero section */
.hero-container {
    text-align: center;
    padding: 4rem 1rem 3rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(107, 138, 255, 0.1);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(107, 138, 255, 0.3);
    border-radius: 50px;
    padding: 8px 24px;
    font-size: 0.8rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #a5b4fc;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(3rem, 6vw, 4.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 1.2rem;
    background: linear-gradient(135deg, #ffffff 0%, #c7d2fe 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 10px 30px rgba(129, 140, 248, 0.2);
}
.hero-sub {
    font-size: 1.15rem;
    color: #94a3b8;
    max-width: 600px;
    margin: 0 auto 3rem;
    font-weight: 400;
    line-height: 1.8;
}

/* Score ring */
.score-ring-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
}
.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
}
.score-label {
    font-size: 0.85rem;
    color: #94a3b8;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* Cards */
.card {
    background: rgba(17, 24, 39, 0.6);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.3s ease;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4);
    border-color: rgba(129, 140, 248, 0.3);
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #818cf8;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Skill tags */
.tag-container { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 0.5rem; }
.tag {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: all 0.2s ease;
}
.tag:hover { transform: scale(1.05); }
.tag-green  { background: rgba(74, 222, 128, 0.1); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.2); }
.tag-red    { background: rgba(248, 113, 113, 0.1); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.2); }
.tag-blue   { background: rgba(96, 165, 250, 0.1); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.2); }
.tag-orange { background: rgba(251, 146, 60, 0.1); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.2); }
.tag-purple { background: rgba(167, 139, 250, 0.1); color: #a78bfa; border: 1px solid rgba(167, 139, 250, 0.2); }

/* Phase cards */
.phase-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}
.phase-card:hover { border-color: rgba(129, 140, 248, 0.4); }
.phase-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.4rem;
}
.phase-focus {
    font-size: 0.85rem;
    color: #a5b4fc;
    margin-bottom: 1rem;
    font-style: italic;
}
.phase-task {
    font-size: 0.9rem;
    color: #cbd5e1;
    padding: 6px 0;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    transition: color 0.2s ease;
}
.phase-task:hover { color: #ffffff; }

/* Interview Q card */
.q-card {
    background: rgba(15, 23, 42, 0.6);
    border-left: 4px solid #6366f1;
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    transition: transform 0.2s ease;
}
.q-card:hover { transform: translateX(4px); }
.q-text { font-size: 0.95rem; font-weight: 600; color: #f1f5f9; margin-bottom: 0.5rem; }
.q-tip  { font-size: 0.85rem; color: #94a3b8; font-style: italic; }

/* Improvement card */
.improve-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
}
.original-text { font-size: 0.85rem; color: #f87171; background: rgba(248, 113, 113, 0.05); padding: 10px 12px; border-radius: 8px; margin-bottom: 10px; border: 1px dashed rgba(248, 113, 113, 0.2); }
.improved-text { font-size: 0.85rem; color: #4ade80; background: rgba(74, 222, 128, 0.05); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(74, 222, 128, 0.2); }

/* Verdict box */
.verdict-box {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(30, 41, 59, 0.5) 100%);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 16px;
    padding: 1.5rem;
    font-size: 0.95rem;
    color: #e2e8f0;
    line-height: 1.8;
    box-shadow: inset 0 2px 15px rgba(99, 102, 241, 0.05);
}

/* Section divider */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: #ffffff;
    margin: 2.5rem 0 1.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
}

/* Streamlit overrides */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2.5rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.03em !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100%;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(79, 70, 229, 0.5) !important;
    background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
}
.stFileUploader {
    background: rgba(30, 41, 59, 0.5) !important;
    border: 2px dashed rgba(99, 102, 241, 0.3) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    transition: border-color 0.3s ease !important;
}
.stFileUploader:hover { border-color: rgba(99, 102, 241, 0.6) !important; }
.stTextInput input, .stTextArea textarea {
    background: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: #e8eaf0 !important;
    padding: 12px 16px !important;
    transition: all 0.2s ease !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.2) !important;
    background: rgba(30, 41, 59, 0.8) !important;
}
label { color: #94a3b8 !important; font-size: 0.9rem !important; font-weight: 500 !important; }
.stSpinner > div { border-color: #818cf8 transparent transparent transparent !important; }

/* Progress bar */
.score-bar-wrap { background: rgba(255, 255, 255, 0.05); border-radius: 50px; height: 12px; margin: 0.8rem 0 1.2rem; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.2); }
.score-bar-fill { height: 12px; border-radius: 50px; transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 0 10px currentColor; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: rgba(30, 41, 59, 0.4); border-radius: 14px; padding: 6px; gap: 6px; backdrop-filter: blur(10px); }
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #94a3b8 !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #ffffff !important; background: rgba(255, 255, 255, 0.05) !important; }
.stTabs [aria-selected="true"] {
    background: rgba(99, 102, 241, 0.2) !important;
    color: #ffffff !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1) !important;
}
</style>

""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def score_color(score: int) -> str:
    if score >= 75: return "#4ade80"
    if score >= 50: return "#fbbf24"
    return "#f87171"

def score_label(score: int) -> str:
    if score >= 80: return "Excellent Match 🎯"
    if score >= 65: return "Good Match ✅"
    if score >= 45: return "Moderate Match ⚡"
    return "Needs Improvement 📈"

def render_tags(items: list, tag_class: str):
    if not items:
        st.markdown('<p style="color:#8892b0;font-size:0.85rem;">None identified</p>', unsafe_allow_html=True)
        return
    tags_html = '<div class="tag-container">' + "".join(
        f'<span class="tag {tag_class}">{item}</span>' for item in items
    ) + '</div>'
    st.markdown(tags_html, unsafe_allow_html=True)

def render_list(items: list, icon: str = "→"):
    for item in items:
        st.markdown(f'<div class="phase-task"><span>{icon}</span><span>{item}</span></div>', unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">🇵🇰 Built for Pakistani Job Seekers</div>
    <div class="hero-title">JobCopilot AI</div>
    <div class="hero-sub">Upload your CV, pick a target role — get an instant AI career report with match score, skill gaps, roadmap & interview prep.</div>
</div>
""", unsafe_allow_html=True)

# ── Input Section ─────────────────────────────────────────────────────────────
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📄 Upload Your CV</div>', unsafe_allow_html=True)
        cv_file = st.file_uploader("PDF format only", type=["pdf"], label_visibility="collapsed")

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🎯 Target Job Role</div>', unsafe_allow_html=True)
        job_role = st.text_input("e.g. Full Stack Developer, Data Analyst, Marketing Manager", label_visibility="collapsed")

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 Job Description <span style="font-weight:400;color:#555e7a">(optional)</span></div>', unsafe_allow_html=True)
        job_desc = st.text_area("Paste the job description for a more accurate analysis", height=120, label_visibility="collapsed")

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        analyze_btn = st.button("⚡ Analyze My Career Profile")
        st.markdown('</div>', unsafe_allow_html=True)

# ── Analysis ──────────────────────────────────────────────────────────────────
if analyze_btn:
    if not cv_file:
        st.error("Please upload your CV (PDF).")
    elif not job_role.strip():
        st.error("Please enter a target job role.")
    else:
        with st.spinner("🤖 AI agents are analyzing your profile — this takes 30–60 seconds..."):
            try:
                cv_text = extract_text_from_pdf(cv_file)
                result = asyncio.run(run_career_analysis(cv_text, job_role.strip(), job_desc.strip()))
                st.session_state["result"] = result
                st.session_state["job_role"] = job_role.strip()
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

# ── Results ───────────────────────────────────────────────────────────────────
if "result" in st.session_state:
    r = st.session_state["result"]
    target_role = st.session_state["job_role"]

    cv     = r.get("cv_analysis", {})
    match  = r.get("job_match", {})
    gaps   = r.get("skill_gaps", {})
    improv = r.get("cv_improvements", {})
    prep   = r.get("interview_prep", {})

    score  = match.get("match_score", 0)
    color  = score_color(score)

    st.markdown("---")

    # ── Score Banner ──────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.markdown(f"""
        <div class="card" style="text-align:center;padding:2rem;">
            <div class="card-title">JOB MATCH SCORE</div>
            <div class="score-number" style="color:{color};">{score}</div>
            <div style="font-size:0.7rem;color:#8892b0;letter-spacing:0.1em;text-transform:uppercase;">out of 100</div>
            <div class="score-bar-wrap" style="margin:1rem auto;max-width:220px;">
                <div class="score-bar-fill" style="width:{score}%;background:{color};"></div>
            </div>
            <div style="font-size:1rem;font-weight:600;color:{color};">{score_label(score)}</div>
            <div style="font-size:0.82rem;color:#8892b0;margin-top:0.3rem;">for <strong style="color:#c8d4f0">{target_role}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    # ── Candidate Info ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">👤 Candidate Profile</div>', unsafe_allow_html=True)
    i1, i2, i3 = st.columns(3)
    with i1:
        st.markdown(f'<div class="card"><div class="card-title">Name</div><div style="font-size:1.1rem;font-weight:600;">{cv.get("name","—")}</div></div>', unsafe_allow_html=True)
    with i2:
        st.markdown(f'<div class="card"><div class="card-title">Experience</div><div style="font-size:1.1rem;font-weight:600;">{cv.get("years_of_experience","—")}</div></div>', unsafe_allow_html=True)
    with i3:
        st.markdown(f'<div class="card"><div class="card-title">Contact</div><div style="font-size:1.1rem;font-weight:600;">{cv.get("contact","—")}</div></div>', unsafe_allow_html=True)

    if cv.get("summary"):
        st.markdown(f'<div class="verdict-box">💬 {cv["summary"]}</div>', unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Skills & Match", "🕳️ Skill Gaps", "📝 CV Improvements", "🎤 Interview Prep", "📋 Full CV Analysis"
    ])

    # ── Tab 1: Skills & Match ─────────────────────────────────────────────────
    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="card"><div class="card-title">✅ Matched Skills</div>', unsafe_allow_html=True)
            render_tags(match.get("matched_skills", []), "tag-green")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">💪 Strengths</div>', unsafe_allow_html=True)
            render_list(match.get("strengths", []), "✦")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="card"><div class="card-title">⚠️ Weaknesses</div>', unsafe_allow_html=True)
            render_list(match.get("weaknesses", []), "✗")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">🧠 Technical Skills in CV</div>', unsafe_allow_html=True)
            render_tags(cv.get("technical_skills", []), "tag-blue")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card-title" style="margin-top:0.5rem;">🔍 Overall Verdict</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="verdict-box">{match.get("overall_verdict","—")}</div>', unsafe_allow_html=True)

    # ── Tab 2: Skill Gaps ─────────────────────────────────────────────────────
    with tab2:
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="card"><div class="card-title">🔴 Missing Technical Skills</div>', unsafe_allow_html=True)
            render_tags(gaps.get("missing_technical_skills", []), "tag-red")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">🎓 Recommended Certifications</div>', unsafe_allow_html=True)
            render_tags(gaps.get("recommended_certifications", []), "tag-purple")
            st.markdown('</div>', unsafe_allow_html=True)

        with g2:
            st.markdown('<div class="card"><div class="card-title">💬 Missing Soft Skills</div>', unsafe_allow_html=True)
            render_tags(gaps.get("missing_soft_skills", []), "tag-orange")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">⚡ Priority Skills (Learn First)</div>', unsafe_allow_html=True)
            priority = gaps.get("priority_skills", [])
            for i, skill in enumerate(priority, 1):
                st.markdown(f'<div class="phase-task"><span style="color:#fbbf24;font-weight:700;">#{i}</span><span style="color:#e2e8f0">{skill}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Tab 3: CV Improvements ────────────────────────────────────────────────
    with tab3:
        if improv.get("improved_summary"):
            st.markdown('<div class="card"><div class="card-title">✍️ Improved Professional Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.9rem;color:#c8d4f0;line-height:1.7;">{improv["improved_summary"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        bullets = improv.get("bullet_improvements", [])
        if bullets:
            st.markdown('<div class="card-title" style="margin-top:1rem;">🔄 Bullet Point Rewrites</div>', unsafe_allow_html=True)
            for b in bullets:
                st.markdown(f"""
                <div class="improve-card">
                    <div style="font-size:0.72rem;color:#f87171;letter-spacing:0.08em;margin-bottom:4px;">BEFORE</div>
                    <div class="original-text">{b.get("original","")}</div>
                    <div style="font-size:0.72rem;color:#4ade80;letter-spacing:0.08em;margin-bottom:4px;">AFTER</div>
                    <div class="improved-text">{b.get("improved","")}</div>
                </div>
                """, unsafe_allow_html=True)

        kw = improv.get("ats_keywords", [])
        tips = improv.get("cv_tips", [])
        k1, k2 = st.columns(2)
        with k1:
            st.markdown('<div class="card"><div class="card-title">🔑 ATS Keywords to Add</div>', unsafe_allow_html=True)
            render_tags(kw, "tag-blue")
            st.markdown('</div>', unsafe_allow_html=True)
        with k2:
            st.markdown('<div class="card"><div class="card-title">💡 CV Tips</div>', unsafe_allow_html=True)
            render_list(tips, "✓")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Tab 4: Interview Prep ─────────────────────────────────────────────────
    with tab4:
        sample = prep.get("sample_answer", {})
        if sample:
            st.markdown(f'<div class="card"><div class="card-title">🎤 Sample Answer: "{sample.get("question","")}"</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.88rem;color:#c8d4f0;line-height:1.7;">{sample.get("answer","")}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        qs = prep.get("likely_questions", [])
        if qs:
            st.markdown('<div class="card-title" style="margin-top:1rem;">❓ Likely Interview Questions</div>', unsafe_allow_html=True)
            for q in qs:
                st.markdown(f"""
                <div class="q-card">
                    <div class="q-text">Q: {q.get("question","")}</div>
                    <div class="q-tip">💡 {q.get("tip","")}</div>
                </div>
                """, unsafe_allow_html=True)

        tqs = prep.get("technical_questions", [])
        d1, d2 = st.columns(2)
        with d1:
            st.markdown('<div class="card"><div class="card-title">💻 Technical Questions</div>', unsafe_allow_html=True)
            render_list(tqs, "?")
            st.markdown('</div>', unsafe_allow_html=True)
        with d2:
            dos = prep.get("dos", [])
            donts = prep.get("donts", [])
            st.markdown('<div class="card"><div class="card-title">✅ DOs</div>', unsafe_allow_html=True)
            render_list(dos, "✓")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="card"><div class="card-title">❌ DON\'Ts</div>', unsafe_allow_html=True)
            render_list(donts, "✗")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Tab 5: Full CV Analysis ───────────────────────────────────────────────
    with tab5:
        cols = st.columns(2)
        sections = [
            ("🎓 Education", cv.get("education", []), "tag-blue"),
            ("💼 Experience", cv.get("experience", []), "tag-purple"),
            ("🛠️ Technical Skills", cv.get("technical_skills", []), "tag-green"),
            ("🤝 Soft Skills", cv.get("soft_skills", []), "tag-orange"),
            ("📜 Certifications", cv.get("certifications", []), "tag-blue"),
            ("🚀 Projects", cv.get("projects", []), "tag-purple"),
        ]
        for i, (title, items, tag) in enumerate(sections):
            with cols[i % 2]:
                st.markdown(f'<div class="card"><div class="card-title">{title}</div>', unsafe_allow_html=True)
                if title in ["🎓 Education", "💼 Experience", "🚀 Projects"]:
                    render_list(items)
                else:
                    render_tags(items, tag)
                st.markdown('</div>', unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem 1rem;color:#3d4d6a;font-size:0.78rem;">
        JobCopilot AI · Privacy-friendly · No data stored · Powered by Gemini
    </div>
    """, unsafe_allow_html=True)
