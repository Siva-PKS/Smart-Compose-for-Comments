import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Inline Smart Suggest", layout="centered")

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.markdown("### 💬 AI Inline Comment Assistant")

if "text" not in st.session_state:
    st.session_state.text = ""
if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""

def get_ai_suggestion(text):
    if not text.strip():
        return ""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"Suggest a short next phrase to complete this text naturally: {text}"
        response = model.generate_content(prompt)
        return response.text.strip().split("\n")[0]
    except Exception:
        return ""

typed = st.text_area("Your Comment", value=st.session_state.text, height=160, placeholder="Type your comment here...")

if typed != st.session_state.text:
    st.session_state.text = typed
    st.session_state.suggestion = get_ai_suggestion(typed)

# Simulate inline suggestion by showing ghost text below
ghost = st.session_state.suggestion
if ghost:
    st.markdown(f"""
    <div style='margin-top:-25px;color:gray;font-size:14px;opacity:0.6'>
        ➤ <i>{ghost}</i>
    </div>
    """, unsafe_allow_html=True)
