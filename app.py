import streamlit as st
import google.generativeai as genai
import json
import re

st.set_page_config(page_title="💬 Inline AI Suggestion", layout="centered")

# --- Configure Gemini ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.markdown("### ✨ AI Smart Comment Composer")
st.caption("Type your comment — AI will suggest 2 completions inside the same text box.")

# --- Get AI suggestions ---
def get_ai_suggestions(text):
    if not text.strip():
        return []
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        Continue this text naturally and meaningfully:
        "{text}"
        Provide exactly 2 short, contextually relevant suggestions (under 12 words each).
        Return only the suggestions, one per line. No bullets, no introductions.
        """
        res = model.generate_content(prompt)
        lines = re.split(r"[\n•\-]+", res.text)
        suggestions = [l.strip() for l in lines if len(l.strip()) > 3]
        return suggestions[:2]
    except Exception:
        return []

# --- Persistent states ---
if "typed" not in st.session_state:
    st.session_state.typed = ""
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

# --- Input text area ---
typed = st.text_area("Write your comment:", value=st.session_state.typed, height=180, key="text_input")

# --- If text changes, fetch AI suggestions ---
if typed != st.session_state.typed:
    st.session_state.typed = typed
    st.session_state.suggestions = get_ai_suggestions(typed)

suggestions = st.session_state.suggestions

# --- Inject visible popup directly below the cursor ---
if suggestions:
    st.components.v1.html(f"""
    <script>
    const textarea = window.parent.document.querySelector('textarea');
    if (textarea && !window.aiPopupCreated) {{
        window.aiPopupCreated = true;
        let popup = document.createElement('div');
        popup.id = 'aiSuggestPopup';
        popup.style.position = 'absolute';
        popup.style.background = '#fff';
        popup.style.border = '1px solid #ccc';
        popup.style.borderRadius = '8px';
        popup.style.padding = '6px';
        popup.style.fontSize = '14px';
        popup.style.color = '#333';
        popup.style.zIndex = '9999';
        popup.style.maxWidth = '95%';
        popup.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';

        const suggestions = {json.dumps(suggestions)};
        suggestions.forEach(text => {{
            let item = document.createElement('div');
            item.textContent = text;
            item.style.padding = '4px 8px';
            item.style.borderRadius = '4px';
            item.onmouseover = () => item.style.background = '#f0f0f0';
            item.onmouseout = () => item.style.background = 'white';
            item.onclick = () => {{
                textarea.value = textarea.value + " " + text;
                popup.remove();
                window.aiPopupCreated = false;
            }};
            popup.appendChild(item);
        }});

        // Position popup under textarea
        const rect = textarea.getBoundingClientRect();
        popup.style.left = rect.left + window.scrollX + 'px';
        popup.style.top = rect.bottom + window.scrollY - 10 + 'px';
        popup.style.width = rect.width * 0.95 + 'px';

        document.body.appendChild(popup);
    }}
    </script>
    """, height=0)
