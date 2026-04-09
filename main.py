import streamlit as st
import requests
import time

# --- CONFIGURATION ---
# Replace with your n8n PRODUCTION Webhook URL
N8N_WEBHOOK_URL = "https://shumas.app.n8n.cloud/webhook/chat-input"

st.set_page_config(page_title="Keystone AI Assistant", page_icon="🏠", layout="centered")

# --- CUSTOM CSS FOR CHATGPT FEEL ---
st.markdown("""
    <style>
    .stChatFloatingInputContainer { background-color: rgba(0,0,0,0); }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    div[data-testid="stExpander"] { border: none; box-shadow: none; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏠 Keystone Realty")
    st.markdown("### FYP Project: RAG AI Assistant")
    st.info("Developed by: SHUMAS CHOHAN\n\nBuilt with: n8n, Pinecone, Vapi.")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN UI ---
st.title("How can I help you today?")

# Show suggestions ONLY if there is no chat history yet
if not st.session_state.messages:
    st.write("Try asking about:")
    
    # 2x2 Grid of Suggestions
    col1, col2 = st.columns(2)
    
    suggestions = [
        "🏡 What is the price of 14 Birchwood Lane?",
        "🐾 Which rentals are pet-friendly?",
        "📄 What documents do I need to rent?",
        "📈 How was the Lakewood market in Q1 2025?"
    ]
    
    # Button Logic
    clicked_suggestion = None
    with col1:
        if st.button(suggestions[0]): clicked_suggestion = suggestions[0]
        if st.button(suggestions[1]): clicked_suggestion = suggestions[1]
    with col2:
        if st.button(suggestions[2]): clicked_suggestion = suggestions[2]
        if st.button(suggestions[3]): clicked_suggestion = suggestions[3]

    # If a suggestion is clicked, treat it as the first prompt
    if clicked_suggestion:
        st.session_state.messages.append({"role": "user", "content": clicked_suggestion})
        st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT LOGIC ---
if prompt := st.chat_input("Ask about properties, agents, or the buying process..."):
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get AI Response
    with st.chat_message("assistant"):
        with st.spinner("Searching Keystone Database..."):
            try:
                payload = {
                    "message": {
                        "toolCallList": [{
                            "id": f"call_{int(time.time())}",
                            "function": { "arguments": f"{{\"query\": \"{prompt}\"}}" }
                        }]
                    }
                }
                
                response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=25)
                
                if response.status_code == 200:
                    data = response.json()
                    full_response = data["results"][0]["result"]
                else:
                    full_response = "I'm sorry, I'm having trouble connecting to the database right now."
            
            except Exception as e:
                full_response = "Check your n8n Production URL and ensure the workflow is 'Published'."

            # 3. "Streaming" Typing Effect
            placeholder = st.empty()
            typed_text = ""
            for word in full_response.split():
                typed_text += word + " "
                placeholder.markdown(typed_text + "▌")
                time.sleep(0.05)
            placeholder.markdown(typed_text)

    # 4. Save to History
    st.session_state.messages.append({"role": "assistant", "content": full_response})