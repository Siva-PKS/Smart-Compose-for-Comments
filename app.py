import streamlit as st
import google.generativeai as genai
import re
import time

# ---------- Streamlit page setup ----------
st.set_page_config(page_title="💬 Smart AI Comment Composer", layout="centered")

st.markdown("### ✍️ AI Smart Compose")
st.caption("Type your comment. Click ✨ Suggest to get 2 short AI completions you can insert.")

# ---------- Configure Gemini ----------
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# ---------- Helper: safe Gemini call with retry ----------
def call_gemini_with_retry(prompt, retries=3):
    model = genai.GenerativeModel("gemini-2.0-flash")

    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)

            # ✅ SAFE text extraction (important fix)
            if response and hasattr(response, "text") and response.text:
                return response.text
            elif response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                return ""

        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                wait = (2 ** attempt) * 5
                time.sleep(wait)
            else:
                raise

    return ""


# ---------- Helper: fetch two short AI completions ----------
def get_ai_suggestions(text: str):
    if not text.strip():
        return []

    try:
        prompt = f"""
Continue this sentence naturally:
"{text}"

Give exactly 2 short, meaningful continuations (under 12 words each).
Return only those 2 lines, no numbering, bullets or introductions.
"""

        raw_text = call_gemini_with_retry(prompt)

        if not raw_text:
            return []

        # ✅ Better cleaning
        lines = re.split(r"[\n•\-]+", raw_text)
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
    with st.spinner("Generating suggestions..."):
        st.session_state.suggestions = get_ai_suggestions(st.session_state.typed)

# ---------- Display suggestions ----------
if st.session_state.suggestions:
    st.markdown("**AI suggestions:**")
    cols = st.columns(len(st.session_state.suggestions))

    for i, suggestion in enumerate(st.session_state.suggestions):
        if cols[i].button(f"💡 {suggestion}", key=f"sugg_{i}"):
            st.session_state.typed += " " + suggestion
            st.session_state.suggestions = []
            st.rerun()

# ---------- Styling ----------
st.markdown(
    "<style>.stTextArea textarea{font-size:16px;border-radius:10px;}</style>",
    unsafe_allow_html=True,
)
