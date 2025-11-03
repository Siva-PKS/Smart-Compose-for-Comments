import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="💡 AI Inline Smart Compose", layout="centered")

# Configure Gemini API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.markdown("### 💬 AI-Powered Smart Comment Box")
st.caption("Start typing — AI suggests completions inline within the same textbox.")

# --- Function to get AI suggestions ---
def get_ai_suggestions(text):
    if not text.strip():
        return []
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        The user typed: "{text}"
        Suggest 2 short, natural, contextually meaningful completions that could follow this text.
        Each suggestion must be under 10 words.
        Only return the completions, one per line.
        """
        res = model.generate_content(prompt)
        lines = [l.strip("-• ").strip() for l in res.text.split("\n") if l.strip()]
        return lines[:2]
    except Exception as e:
        return []

# --- Manage state ---
if "text" not in st.session_state:
    st.session_state.text = ""
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

typed = st.text_area(
    "Your Comment",
    value=st.session_state.text,
    height=160,
    placeholder="Type your comment here...",
    label_visibility="collapsed"
)

# --- Generate suggestions on change ---
if typed != st.session_state.text:
    st.session_state.text = typed
    st.session_state.suggestions = get_ai_suggestions(typed)

suggestions = st.session_state.suggestions
suggestions_json = json.dumps(suggestions)

# --- Inline popup suggestion box within same text area ---
st.components.v1.html(f"""
<div style="position: relative; width: 100%;">
  <textarea id="aiBox" rows="6"
    style="width:100%;padding:10px 10px 60px 10px;font-size:16px;
           border-radius:10px;border:1px solid #ccc;resize:none;
           font-family:sans-serif;outline:none;"
    placeholder="Type your comment...">{typed}</textarea>

  <!-- Popup for AI suggestions -->
  <div id="popup"
       style="position:absolute; bottom:10px; left:12px; right:12px;
              background:#fff; border:1px solid #ccc;
              border-radius:6px; box-shadow:0px 2px 8px rgba(0,0,0,0.1);
              font-family:sans-serif; font-size:14px; display:none;
              z-index:10; padding:4px;">
  </div>
</div>

<script>
const suggestions = {suggestions_json};
const inputBox = document.getElementById("aiBox");
const popup = document.getElementById("popup");

function showPopup() {{
  popup.innerHTML = "";
  if (suggestions.length === 0 || inputBox.value.trim() === "") {{
    popup.style.display = "none";
    return;
  }}

  suggestions.forEach((s) => {{
    const item = document.createElement("div");
    item.textContent = s;
    item.style.padding = "5px 8px";
    item.style.cursor = "pointer";
    item.style.borderRadius = "4px";
    item.onmouseover = () => item.style.background = "#f0f0f0";
    item.onmouseout = () => item.style.background = "#fff";
    item.onclick = () => {{
      inputBox.value = inputBox.value.trim() + " " + s;
      popup.style.display = "none";
    }};
    popup.appendChild(item);
  }});
  popup.style.display = "block";
}}

showPopup();
</script>
""", height=230)
