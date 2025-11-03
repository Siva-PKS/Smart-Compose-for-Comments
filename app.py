import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="💡 Inline AI Smart Compose", layout="centered")

# Configure Gemini API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.markdown("### ✍️ Smart Inline AI Suggestion")
st.caption("Start typing — an inline gray suggestion will appear (press Tab to accept).")

# Function to get inline suggestion
def get_inline_suggestion(text):
    if not text.strip():
        return ""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        User typed: "{text}"
        Predict the next few words that the user is most likely to type next.
        Keep it short (5-12 words max), same tone and language.
        """
        res = model.generate_content(prompt)
        suggestion = res.text.strip().split("\n")[0]
        return suggestion
    except Exception as e:
        return ""

# Persistent state
if "typed_text" not in st.session_state:
    st.session_state.typed_text = ""
if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""

typed = st.text_input("Type here:", value=st.session_state.typed_text, label_visibility="collapsed")

if typed != st.session_state.typed_text:
    st.session_state.typed_text = typed
    st.session_state.suggestion = get_inline_suggestion(typed)

suggestion = st.session_state.suggestion

# Inject HTML + JS overlay to show ghost text inline
st.components.v1.html(f"""
<div style="position: relative; width: 100%;">
  <textarea id="aiBox" rows="5"
    style="width:100%;padding:10px;font-size:16px;border-radius:10px;
           border:1px solid #ccc;resize:none;font-family:sans-serif;
           outline:none;color:black;">{typed}</textarea>

  <div id="ghostText"
    style="position:absolute;top:10px;left:10px;
           color:#aaa;font-size:16px;font-family:sans-serif;
           pointer-events:none;white-space:pre-wrap;
           overflow:hidden;"></div>
</div>

<script>
const input = document.getElementById('aiBox');
const ghost = document.getElementById('ghostText');
const suggestion = {json.dumps(suggestion)};

function updateGhost() {{
  const typed = input.value;
  ghost.textContent = typed + (typed.trim() ? " " : "") + suggestion;
  ghost.style.width = input.offsetWidth + "px";
  ghost.style.height = input.offsetHeight + "px";
}}

// Tab key to accept suggestion
input.addEventListener('keydown', (e) => {{
  if (e.key === 'Tab' && suggestion) {{
    e.preventDefault();
    input.value = input.value + " " + suggestion;
    ghost.textContent = "";
  }}
}});

updateGhost();
</script>
""", height=180)

