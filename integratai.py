
from google import genai
import streamlit as st


def ask_gemini(job_description, profile, question):
    api_key = st.secrets["GEMINI_API_KEY"]

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an AI assistant inside a Job Description Analyser.

Help the user understand a job and compare its requirements
with their career profile.

JOB DESCRIPTION:
{job_description[:12000]}

USER'S CAREER PROFILE:
{profile[:5000]}

USER'S QUESTION:
{question[:2000]}

Instructions:
1. Answer in simple, precise English.
2. Keep the answer to a maximum of 80 words.
3. Use 3 to 5 short bullet points whenever appropriate.
4. Answer the user's exact question directly.
5. Avoid long introductions, repeated information, and unnecessary explanations.
6. Use only the supplied job description and career profile.
7. Never invent skills, job requirements, salary details, or experience.
8. If information is missing, say so in one short sentence.
9. Keep answers focused on the job and career preparation.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
