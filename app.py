import streamlit as st
import google.generativeai as genai
import re

# ---------- Streamlit page setup ----------
st.set_page_config(page_title="💬 Smart AI Comment Composer", layout="centered")

st.markdown("### ✍️ AI Smart Compose")
st.caption("Type your comment. Click ✨ Suggest to get 2 short AI completions you can insert.")

# ---------- Configure Gemini ----------
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# ---------- Helper: fetch two short AI completions ----------
def get_ai_suggestions(text: str):
    if not text.strip():
        return []
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        Continue this sentence naturally:
        "{text}"
        Give exactly 2 short, meaningful continuations (under 12 words each).
        Return only those 2 lines, no numbering, bullets or introductions.
        """
        res = model.generate_content(prompt)
        # Clean and split text
        lines = re.split(r"[\n•\-]+", res.text)
        suggestions = [l.strip() for l in lines if len(l.strip()) > 3]
        return suggestions[:2]
    except Exception as e:
        st.error(f"Error generating suggestions: {e}")
        return []

# ---------- Session state ----------
if "typed" not in st.session_state:
    st.session_state.typed = ""
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

# ---------- Main input ----------
st.session_state.typed = st.text_area(
    "Write your comment:",
    value=st.session_state.typed,
    height=180,
    placeholder="Start typing your comment here...",
)

# ---------- Suggestion button ----------
if st.button("✨ Suggest"):
    st.session_state.suggestions = get_ai_suggestions(st.session_state.typed)

# ---------- Display suggestions below the same box ----------
if st.session_state.suggestions:
    st.markdown("**AI suggestions:**")
    cols = st.columns(len(st.session_state.suggestions))
    for i, suggestion in enumerate(st.session_state.suggestions):
        if cols[i].button(f"💡 {suggestion}"):
            st.session_state.typed += " " + suggestion
            st.session_state.suggestions = []
            st.rerun()

# ---------- Small styling note ----------
st.markdown(
    "<style>.stTextArea textarea{font-size:16px;border-radius:10px;}</style>",
    unsafe_allow_html=True,
)
