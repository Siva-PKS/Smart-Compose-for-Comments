import streamlit as st
import google.generativeai as genai

# ---------------------------
# CONFIGURE GOOGLE API KEY
# ---------------------------
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="AI Smart Comment Suggestion", page_icon="💬", layout="centered")
st.title("💬 Smart Comment Suggestion (Google Gemini)")
st.write("Start typing your comment below — AI will suggest a polished version automatically.")

# ---------------------------
# FUNCTION TO GET AI SUGGESTION
# ---------------------------
def get_ai_suggestion(text):
    if not text.strip():
        return ""
    
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    You are an AI assistant helping users write professional and polite comments.
    Rephrase or complete this comment clearly and helpfully:
    "{text}"
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error generating suggestion: {str(e)}"

# ---------------------------
# STREAMLIT UI
# ---------------------------
user_input = st.text_area("✍️ Type your comment:", height=150, placeholder="Type here...")

if user_input:
    with st.spinner("Generating AI suggestion..."):
        suggestion = get_ai_suggestion(user_input)

    if suggestion:
        st.markdown("### 💡 Suggested Version:")
        st.info(suggestion)

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.caption("Powered by Google Gemini AI · Built with Streamlit Cloud")
