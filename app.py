import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="💬 Smart Comment AI", layout="centered")

# Configure Gemini API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.markdown("### 💡 Smart Comment Composer")
st.caption("Type your comment — AI will show 2 smart suggestions below.")

# --- Function to get AI suggestions ---
def get_ai_suggestions(text):
    if not text.strip():
        return []
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        The user typed: "{text}"
        Suggest the next part of their sentence or comment continuation.
        Give 2 short and natural completions (max 10 words each).
        Only output the completions, one per line.
        """
        res = model.generate_content(prompt)
        lines = [l.strip("-• ").strip() for l in res.text.split("\n") if l.strip()]
        return lines[:2]
    except Exception as e:
        return []

# --- State management ---
if "text" not in st.session_state:
    st.session_state.text = ""
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

typed = st.session_state.text

# --- Main text input box ---
typed = st.text_area(
    "Write your comment:",
    value=typed,
    height=150,
    label_visibility="collapsed",
    placeholder="Type your comment here..."
)

# --- Update suggestions when text changes ---
if typed != st.session_state.text:
    st.session_state.text = typed
    st.session_state.suggestions = get_ai_suggestions(typed)

suggestions = st.session_state.suggestions
suggestions_json = json.dumps(suggestions)

# --- Inject HTML & JS for interactive popup ---
st.components.v1.html(f"""
<div style="position: relative; width: 100%;">
  <textarea id="commentBox" rows="6"
    style="width:100%;padding:10px;font-size:16px;border-radius:10px;
           border:1px solid #ccc;resize:none;font-family:sans-serif;
           outline:none;" placeholder="Type your comment...">{typed}</textarea>

  <div id="popup"
       style="position:absolute; background:#fff; border:1px solid #ccc;
              border-radius:8px; box-shadow:0px 4px 10px rgba(0,0,0,0.1);
              padding:6px 10px; font-family:sans-serif; font-size:14px;
              display:none; z-index:100; max-width:95%;">
  </div>
</div>

<script>
const suggestions = {suggestions_json};
const inputBox = document.getElementById("commentBox");
const popup = document.getElementById("popup");

function showSuggestions() {{
  popup.innerHTML = "";
  if (suggestions.length === 0 || inputBox.value.trim() === "") {{
    popup.style.display = "none";
    return;
  }}

  suggestions.forEach((s, i) => {{
    const opt = document.createElement("div");
    opt.textContent = s;
    opt.style.padding = "6px";
    opt.style.cursor = "pointer";
    opt.style.borderRadius = "6px";
    opt.onmouseover = () => opt.style.background = "#f0f0f0";
    opt.onmouseout = () => opt.style.background = "#fff";
    opt.onclick = () => {{
      inputBox.value = inputBox.value.trim() + " " + s;
      popup.style.display = "none";
    }};
    popup.appendChild(opt);
  }});

  const rect = inputBox.getBoundingClientRect();
  popup.style.top = (window.scrollY + rect.bottom - 10) + "px";
  popup.style.left = (rect.left + 10) + "px";
  popup.style.display = "block";
}}

showSuggestions();
</script>
""", height=220)
