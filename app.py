import streamlit as st
import openai
import time

openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

st.title("💬 AI Smart Compose for Comments")

# Session state to hold autosuggestion
if "last_input" not in st.session_state:
    st.session_state.last_input = ""
if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""

def get_ai_suggestion(text):
    """Call LLM to get a rephrased suggestion."""
    if not text.strip():
        return ""
    prompt = f"Rephrase this partial comment politely and clearly, finishing the thought naturally:\n\n{text}"
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return resp["choices"][0]["message"]["content"].strip()

# Input area
text = st.text_area("Type your comment:", st.session_state.last_input, height=120)

# Detect typing pause (simulate debounce)
if text != st.session_state.last_input:
    st.session_state.last_input = text
    st.session_state.last_change_time = time.time()

if "last_change_time" in st.session_state and (time.time() - st.session_state.last_change_time > 1.5):
    # Call AI suggestion after 1.5s pause
    st.session_state.suggestion = get_ai_suggestion(text)

# Show AI suggestion
if st.session_state.suggestion:
    st.markdown("**AI Suggestion:** ✨")
    st.markdown(f"> {st.session_state.suggestion}")
    if st.button("✅ Accept suggestion"):
        st.session_state.last_input = st.session_state.suggestion
        st.experimental_rerun()

if st.button("Submit comment"):
    st.success(f"Comment posted:\n\n{text}")
