
import streamlit as st
from google import genai

st.title("Gemini API Connection Test")

st.write("Connecting to Gemini...")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Explain what a job description is in two simple sentences."
    )

    st.success("Gemini connected successfully!")
    st.write(response.text)

except Exception as e:
    st.error("Something went wrong.")
    st.write(str(e))
