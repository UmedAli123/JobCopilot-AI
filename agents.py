import os
import json
import asyncio
import httpx

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def get_api_key():
    key = os.getenv("GROQ_API_KEY", "")
    if not key or key == "your_groq_api_key_here":
        raise ValueError("❌ GROQ_API_KEY is not set. Please add it to your .env file.")
    return key


async def call_groq(prompt: str, temperature: float = 0.3) -> str:
    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 4096,
        "response_format": {"type": "json_object"}
    }
    
    max_retries = 8
    base_delay = 2.0

    async with httpx.AsyncClient(timeout=90.0) as client:
        for attempt in range(max_retries):
            response = await client.post(
                GROQ_URL, headers=headers, json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
            # If rate limited or service unavailable, wait and retry
            if response.status_code in [429, 503] and attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)
                if response.status_code == 429:
                    try:
                        err_msg = response.json().get("error", {}).get("message", "")
                        import re
                        match = re.search(r'try again in (\d+\.?\d*)s', err_msg)
                        if match:
                            wait_time = float(match.group(1)) + 1.0  # add 1s safety buffer
                    except Exception:
                        pass
                print(f"Rate limited (429). Waiting {wait_time:.1f}s before retry {attempt+1}/{max_retries}...")
                await asyncio.sleep(wait_time)
                continue
                
            raise ValueError(f"Groq API error {response.status_code}: {response.text}")


def safe_json_parse(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    return json.loads(text)


# ── Agent 1: CV Analyzer ──────────────────────────────────────────────────────
async def agent_analyze_cv(cv_text: str) -> dict:
    prompt = f"""You are a professional CV analyst. Analyze the following CV and extract structured information.

CV TEXT:
{cv_text}

Return ONLY a valid JSON object (no markdown, no explanation):
{{
  "name": "candidate full name or Unknown",
  "contact": "email or phone if found, else empty string",
  "education": ["list of education entries"],
  "experience": ["list of job experience entries"],
  "technical_skills": ["list of technical skills"],
  "soft_skills": ["list of soft skills"],
  "certifications": ["list of certifications"],
  "projects": ["list of notable projects"],
  "years_of_experience": "estimated total years as string",
  "summary": "2-sentence profile summary"
}}"""
    return safe_json_parse(await call_groq(prompt))


# ── Agent 2: Job Matcher ──────────────────────────────────────────────────────
async def agent_match_job(cv_data: dict, job_role: str, job_description: str) -> dict:
    prompt = f"""You are a job matching expert. Compare the candidate with the target role.

CANDIDATE PROFILE:
{json.dumps(cv_data, indent=2)}

TARGET JOB ROLE: {job_role}
JOB DESCRIPTION: {job_description or "Not provided – use general industry requirements."}

Return ONLY a valid JSON object:
{{
  "match_score": <integer 0-100>,
  "matched_skills": ["skills the candidate has that match the job"],
  "strengths": ["3-5 strengths relevant to this role"],
  "weaknesses": ["3-5 gaps for this role"],
  "overall_verdict": "one paragraph hiring likelihood summary"
}}"""
    return safe_json_parse(await call_groq(prompt))


# ── Agent 3: Skill Gap Detector ───────────────────────────────────────────────
async def agent_detect_skill_gaps(cv_data: dict, job_role: str, job_description: str) -> dict:
    prompt = f"""You are a skills gap analyst for the Pakistani job market.

CANDIDATE SKILLS:
Technical: {cv_data.get('technical_skills', [])}
Soft: {cv_data.get('soft_skills', [])}
Certifications: {cv_data.get('certifications', [])}

TARGET JOB ROLE: {job_role}
JOB DESCRIPTION: {job_description or "Use standard industry requirements."}

Return ONLY a valid JSON object:
{{
  "missing_technical_skills": ["missing technical skills critical for the role"],
  "missing_soft_skills": ["missing soft skills"],
  "recommended_certifications": ["certifications that would boost employability"],
  "priority_skills": ["top 3 skills to learn first, by impact"]
}}"""
    return safe_json_parse(await call_groq(prompt))


# ── Agent 5: CV Improvement ───────────────────────────────────────────────────
async def agent_improve_cv(cv_text: str, cv_data: dict, job_role: str) -> dict:
    prompt = f"""You are an expert CV writer specializing in ATS optimization for Pakistani job markets.

ORIGINAL CV (excerpt):
{cv_text[:3000]}

CANDIDATE DATA:
{json.dumps(cv_data, indent=2)}

TARGET ROLE: {job_role}

Return ONLY a valid JSON object:
{{
  "improved_summary": "powerful 3-4 sentence professional summary for the target role",
  "bullet_improvements": [
    {{"original": "original bullet/text", "improved": "ATS-optimized version"}},
    {{"original": "...", "improved": "..."}},
    {{"original": "...", "improved": "..."}}
  ],
  "ats_keywords": ["ATS keywords to include for this role"],
  "cv_tips": ["5 actionable tips to improve this CV"],
  "format_suggestions": ["formatting improvements"]
}}"""
    return safe_json_parse(await call_groq(prompt))


# ── Agent 6: Interview Prep ───────────────────────────────────────────────────
async def agent_interview_prep(cv_data: dict, job_role: str, gap_data: dict) -> dict:
    prompt = f"""You are an interview coach for job seekers in Pakistan.

CANDIDATE:
- Skills: {cv_data.get('technical_skills', [])}
- Experience: {cv_data.get('years_of_experience', 'unknown')} years
- Missing Skills: {gap_data.get('missing_technical_skills', [])}

TARGET ROLE: {job_role}

Return ONLY a valid JSON object:
{{
  "likely_questions": [
    {{"question": "interview question", "tip": "how to answer effectively"}},
    {{"question": "...", "tip": "..."}},
    {{"question": "...", "tip": "..."}},
    {{"question": "...", "tip": "..."}},
    {{"question": "...", "tip": "..."}}
  ],
  "technical_questions": ["5 likely technical questions for this role"],
  "sample_answer": {{
    "question": "Tell me about yourself",
    "answer": "tailored sample answer based on candidate profile"
  }},
  "dos": ["5 interview dos for Pakistani job market"],
  "donts": ["5 interview don'ts"]
}}"""
    return safe_json_parse(await call_groq(prompt))


# ── Orchestrator ──────────────────────────────────────────────────────────────
async def run_career_analysis(cv_text: str, job_role: str, job_description: str) -> dict:
    # Agent 1: CV analysis
    cv_data = await agent_analyze_cv(cv_text)

    # Run sequentially to prevent bursting Groq TPM token limits
    match_data = await agent_match_job(cv_data, job_role, job_description)
    gap_data = await agent_detect_skill_gaps(cv_data, job_role, job_description)

    cv_improvements = await agent_improve_cv(cv_text, cv_data, job_role)
    interview_prep = await agent_interview_prep(cv_data, job_role, gap_data)

    return {
        "cv_analysis": cv_data,
        "job_match": match_data,
        "skill_gaps": gap_data,
        "cv_improvements": cv_improvements,
        "interview_prep": interview_prep,
    }
