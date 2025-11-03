import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="💡 Inline Smart Suggestion", layout="centered")

# Configure Gemini API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.markdown("### 💬 Smart Comment Box (Inline AI Suggestions)")
st.caption("Type your comment — AI will show 2 inline suggestions you can click to insert.")

# --- Function to get AI suggestions ---
def get_ai_suggestions(text):
    if not text.strip():
        return []
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        The user typed: "{text}"
        Suggest 2 short and natural completions (max 10 words each).
        Only return the completions, one per line.
        """
        res = model.generate_content(prompt)
        lines = [l.strip("-• ").strip() for l in res.text.split("\n") if l.strip()]
        return lines[:2]
    except Exception as e:
        return []

# --- Session state ---
if "text" not in st.session_state:
    st.session_state.text = ""
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

typed = st.session_state.text

# --- Text input area ---
typed = st.text_area(
    "Type your comment:",
    value=typed,
    height=160,
    label_visibility="collapsed",
    placeholder="Type something..."
)

# --- Update suggestions dynamically ---
if typed != st.session_state.text:
    st.session_state.text = typed
    st.session_state.suggestions = get_ai_suggestions(typed)

suggestions = st.session_state.suggestions
suggestions_json = json.dumps(suggestions)

# --- HTML + JS: popup inside text box ---
st.components.v1.html(f"""
<div style="position: relative; width: 100%;">
  <div style="position: relative;">
    <textarea id="commentBox" rows="6"
      style="width:100%;padding:10px 10px 40px 10px;font-size:16px;
             border-radius:10px;border:1px solid #ccc;resize:none;
             font-family:sans-serif;outline:none;overflow:auto;"
      placeholder="Type your comment...">{typed}</textarea>

    <!-- Inline suggestion container (inside text box) -->
    <div id="inlinePopup"
         style="position:absolute; bottom:8px; left:12px;
                background:#f9f9f9; border:1px solid #ccc;
                border-radius:8px; box-shadow:0px 4px 10px rgba(0,0,0,0.08);
                font-family:sans-serif; font-size:14px;
                display:none; z-index:10; padding:4px 8px;">
    </div>
  </div>
</div>

<script>
const suggestions = {suggestions_json};
const inputBox = document.getElementById("commentBox");
const popup = document.getElementById("inlinePopup");

function showSuggestions() {{
  popup.innerHTML = "";
  if (suggestions.length === 0 || inputBox.value.trim() === "") {{
    popup.style.display = "none";
    return;
  }}

  suggestions.forEach((s) => {{
    const opt = document.createElement("div");
    opt.textContent = s;
    opt.style.padding = "4px 6px";
    opt.style.cursor = "pointer";
    opt.style.borderRadius = "6px";
    opt.onmouseover = () => opt.style.background = "#eee";
    opt.onmouseout = () => opt.style.background = "#f9f9f9";
    opt.onclick = () => {{
      inputBox.value = inputBox.value.trim() + " " + s;
      popup.style.display = "none";
    }};
    popup.appendChild(opt);
  }});

  popup.style.display = "block";
}}

showSuggestions();
</script>
""", height=220)
