import streamlit as st
import time
from openai import OpenAI

# --- CONFIGURATION ---
st.set_page_config(page_title="💬 Smart Compose for Comments", page_icon="✨")

# Load API key securely from Streamlit Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- APP TITLE ---
st.title("💬 Smart Compose for Comments")

st.write(
    """
Type your comment below.  
AI will automatically suggest a clearer, more polite version after you pause typing.
"""
)

# --- SESSION STATE ---
if "last_input" not in st.session_state:
    st.session_state.last_input = ""
if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""
if "last_change_time" not in st.session_state:
    st.session_state.last_change_time = 0.0

# --- HELPER FUNCTION ---
def get_ai_suggestion(text: str) -> str:
    """Ask OpenAI for a polite rephrasing or completion of the comment."""
    if not text.strip():
        return ""
    prompt = (
        "Rephrase this comment politely and clearly, "
        "keeping the original meaning and tone.\n\n"
        f"Comment: {text.strip()}"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful writing assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"AI Error – {e}")
        return ""

# --- USER INPUT AREA ---
text = st.text_area(
    "✏️ Your comment here:",
    value=st.session_state.last_input,
    height=120,
    placeholder="Type something and pause for a moment to see a suggestion…",
)

# Detect typing pause (≈1.5 seconds)
if text != st.session_state.last_input:
    st.session_state.last_input = text
    st.session_state.last_change_time = time.time()
elif time.time() - st.session_state.last_change_time > 1.5:
    # Typing paused → call AI
    st.session_state.suggestion = get_ai_suggestion(text)
    # Reset timer so it doesn’t call repeatedly
    st.session_state.last_change_time = time.time()

# --- DISPLAY AI SUGGESTION ---
if st.session_state.suggestion:
    st.markdown("### ✨ AI Suggestion")
    st.info(st.session_state.suggestion)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Accept Suggestion"):
            st.session_state.last_input = st.session_state.suggestion
            st.session_state.suggestion = ""
            st.experimental_rerun()
    with col2:
        if st.button("♻️ Regenerate"):
            st.session_state.suggestion = get_ai_suggestion(text)
            st.experimental_rerun()

# --- SUBMIT SECTION ---
if st.button("📤 Submit Comment"):
    final_comment = st.session_state.last_input.strip()
    if not final_comment:
        st.warning("Please type a comment before submitting.")
    else:
        st.success("✅ Comment submitted successfully!")
        st.write("**Your final comment:**")
        st.write(final_comment)
