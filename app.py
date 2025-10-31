import streamlit as st
import google.generativeai as genai

# ---------------------------
# CONFIGURE GOOGLE API KEY
# ---------------------------
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("❌ GOOGLE_API_KEY not found in Streamlit secrets.")
    st.stop()

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="💬 Smart Comment Suggestion",
    page_icon="💡",
    layout="centered"
)

st.title("💬 AI Smart Comment Suggestion (Google Gemini 2.5 Flash)")
st.caption("Type your comment — AI will rephrase or complete it clearly and politely.")

# ---------------------------
# FUNCTION TO GET AI SUGGESTION
# ---------------------------
def get_ai_suggestion(text):
    if not text.strip():
        return ""

    # ✅ Correct Gemini 2.5 Flash model
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    You are an AI assistant that helps users write clear, polite, and professional comments.
    Rewrite or complete this comment in a better way:
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
user_input = st.text_area(
    "✍️ Type your comment:",
    height=150,
    placeholder="Type here..."
)

if user_input:
    with st.spinner("💡 Generating AI suggestion..."):
        suggestion = get_ai_suggestion(user_input)

    if suggestion:
        st.markdown("### 💬 Suggested Version:")
        st.info(suggestion)

st.markdown("---")
st.caption("Powered by Google Gemini · Built with Streamlit Cloud")
