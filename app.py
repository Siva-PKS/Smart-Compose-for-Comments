import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="💬 Smart Compose Inline", layout="centered")

# Configure Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("💡 AI Inline Suggestion Text Box")

# Function to get AI suggestions
def get_suggestions(text):
    if not text.strip():
        return []
    prompt = f"""User typed: "{text}"
Suggest 2 short likely completions (each under 12 words).
Return only 2 lines, no numbering."""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        res = model.generate_content(prompt)
        lines = [l.strip("-• ").strip() for l in res.text.split("\n") if l.strip()]
        return lines[:2]
    except Exception as e:
        return [f"(error: {e})"]

# Text state
if "text" not in st.session_state:
    st.session_state.text = ""

typed = st.text_input("Start typing here 👇", value=st.session_state.text, key="user_text", label_visibility="collapsed")

if typed != st.session_state.text:
    st.session_state.text = typed
    suggestions = get_suggestions(typed)
else:
    suggestions = []

# JavaScript-based inline display
suggestions_json = json.dumps(suggestions)
st.components.v1.html(f"""
<textarea id="smartbox" rows="6" style="
  width:100%;padding:10px;font-size:16px;border-radius:10px;
  border:1px solid #ccc;outline:none;resize:none;
  font-family:sans-serif;position:relative;"
  oninput="updateSuggestions()">{typed}</textarea>

<div id="suggestionbox" style="
  position:absolute;
  background:#f0f0f0;
  color:#666;
  font-size:14px;
  padding:5px;
  border-radius:8px;
  border:1px solid #ddd;
  display:none;
  white-space:pre-wrap;
  max-width:95%;
  margin-top:-20px;
  opacity:0.9;
  ">
</div>

<script>
const suggestions = {suggestions_json};
const inputBox = document.getElementById("smartbox");
const suggBox = document.getElementById("suggestionbox");

function updateSuggestions() {{
    if (suggestions.length > 0 && inputBox.value.trim() !== "") {{
        suggBox.innerHTML = "💡 " + suggestions.join("<br>💡 ");
        const rect = inputBox.getBoundingClientRect();
        suggBox.style.top = (window.scrollY + rect.top + inputBox.offsetHeight - 50) + "px";
        suggBox.style.left = (rect.left + 20) + "px";
        suggBox.style.display = "block";
    }} else {{
        suggBox.style.display = "none";
    }}
}}
updateSuggestions();
</script>
""", height=220)

