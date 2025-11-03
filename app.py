import streamlit as st
import google.generativeai as genai
import json
import re

st.set_page_config(page_title="💬 Inline AI Smart Compose", layout="centered")

# --- Configure Gemini ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.markdown("### 💬 AI Comment Smart Composer")
st.caption("Start typing your comment — AI suggests completions inline (click to insert).")

# --- Function to clean and extract 2 short suggestions ---
def get_ai_suggestions(text):
    if not text.strip():
        return []
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        You are an AI writing assistant. 
        The user typed: "{text}"
        Suggest 2 short, meaningful completions (max 12 words each) that naturally continue the text.
        Return only the suggestions, one per line. No introductions or numbering.
        """
        res = model.generate_content(prompt)
        raw = res.text.strip()
        # Clean unwanted formatting
        lines = re.split(r"[\n\-•]+", raw)
        suggestions = [l.strip("•- \t") for l in lines if len(l.strip()) > 3]
        return suggestions[:2]
    except Exception:
        return []

# --- Keep states ---
if "typed" not in st.session_state:
    st.session_state.typed = ""
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

typed = st.text_area("Write your comment:", value=st.session_state.typed, height=180)

# --- Fetch new suggestions ---
if typed != st.session_state.typed:
    st.session_state.typed = typed
    st.session_state.suggestions = get_ai_suggestions(typed)

suggestions = st.session_state.suggestions

# --- Inject popup directly inside the same textarea ---
if suggestions:
    st.components.v1.html(f"""
    <script>
    const textarea = window.parent.document.querySelector('textarea');
    if (textarea) {{
        // Remove old popup if present
        let oldPopup = document.getElementById('aiSuggestPopup');
        if (oldPopup) oldPopup.remove();

        // Create suggestion popup
        let popup = document.createElement('div');
        popup.id = 'aiSuggestPopup';
        popup.style.position = 'absolute';
        popup.style.background = 'white';
        popup.style.border = '1px solid #ccc';
        popup.style.borderRadius = '6px';
        popup.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
        popup.style.padding = '6px';
        popup.style.fontSize = '14px';
        popup.style.color = '#333';
        popup.style.cursor = 'pointer';
        popup.style.zIndex = '9999';
        popup.style.maxWidth = '95%';

        // Add suggestions as clickable divs
        const suggestions = {json.dumps(suggestions)};
        suggestions.forEach((text, i) => {{
            let item = document.createElement('div');
            item.textContent = text;
            item.style.padding = '4px 8px';
            item.style.borderRadius = '4px';
            item.onmouseover = () => item.style.background = '#f0f0f0';
            item.onmouseout = () => item.style.background = 'white';
            item.onclick = () => {{
                textarea.value = textarea.value + " " + text;
                popup.remove();
            }};
            popup.appendChild(item);
        }});

        // Position popup just below textarea
        const rect = textarea.getBoundingClientRect();
        popup.style.left = rect.left + window.scrollX + 'px';
        popup.style.top = rect.top + window.scrollY + rect.height - 8 + 'px';
        popup.style.width = rect.width * 0.95 + 'px';

        document.body.appendChild(popup);
    }}
    </script>
    """, height=0)
