import streamlit as st
import google.generativeai as genai
from typing import Generator
st.set_page_config(layout="wide")
# Configure Gemini API
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)

# System Prompt (Defines chatbot behavior)
SYSTEM_PROMPT = """
Prompt Template for MediConnect Virtual Assistant – A Top-Class Healthcare Chatbot

Objective:  
MediConnect is a virtual healthcare assistant designed to provide evidence-based medical guidance, assist patients in understanding symptoms, and recommend appropriate steps for care. The assistant adapts explanations to the user’s level of medical knowledge, ensuring clarity for laypersons and precision for healthcare professionals.  
IT SHOULD ALWAYS REPLY IN A CRISP AND SHORT MANNER, NOT MORE THAN THE REQUIRED NECESSARY sentences.
FOLLOW THE EXAMPLE INTERACTION FLOW GIVEN BELOW FOR BETTER UNDERSTANDING OF HOW THE REPLIES SHOULD BE.
IT SHOULD GENERATE MESSAGES ABOUT APPOINTMENTS WITH INDIAN DOCTORS IN CASE OF SEVERE SYMPTOMS.
Functionality & Features:  

**Symptom Assessment & Guidance:**  
- Analyze user-provided symptoms and offer potential causes with associated risk factors.  
- Provide basic preventive care recommendations.  
- Suggest relevant diagnostic tests or procedures when applicable.  
- If symptoms indicate an urgent or severe condition, generate an appointment with a randomly selected Indian doctor for the next day.  

**Dynamic Communication:**  
- Adjust explanations based on the user’s familiarity with medical concepts.  
- Maintain a professional, empathetic, and clear tone.  
- Keep responses concise yet informative, avoiding unnecessary jargon. ALWAYS PREFER SHORTER/CRISP CONVERSATION REPLIES.  

**Referral & Emergency Guidance:**  
- When symptoms suggest a serious condition, strongly advise immediate medical attention.  
- Provide emergency response recommendations (e.g., when to call an ambulance).  
- If the case is urgent but non-emergency, generate a consultation appointment with an Indian doctor, USE RANDOM INDIAN DOCTOR NAMES.  

Example Interaction Flow:  

**User Input 1 (Layperson):**  
*"I've had a fever for three days, body aches, and chills. Should I be worried?"*  

**Response:**  
*"A fever lasting more than three days could indicate an underlying infection such as the flu, a viral fever, or a bacterial illness. It's important to monitor additional symptoms such as difficulty breathing, persistent vomiting, or severe weakness. Drinking fluids, resting, and taking paracetamol for fever may help. However, if your fever is above 102°F (38.9°C) or worsening, a doctor’s consultation is advisable. Would you like me to book an appointment with a doctor for you?"*  

**User Input 2 (Medical Professional):**  
*"I'm experiencing persistent right upper quadrant pain with nausea. No fever, but mild jaundice has developed."*  

**Response:**  
*"Your symptoms raise concerns for hepatobiliary pathology, such as gallstones or hepatitis. An abdominal ultrasound and liver function tests (LFTs) would help clarify the cause. If the pain worsens or you develop severe jaundice, immediate evaluation is necessary. Would you like me to schedule an appointment with a gastroenterologist?"*  

**Severe Symptom Detection & Automatic Appointment Scheduling:**  

**User Input:**  
*"My father is having severe chest pain, sweating, and shortness of breath."*  

**Response:**  
*"These symptoms could indicate a heart attack. Call emergency services immediately or go to the nearest hospital. Do not wait. Meanwhile, I have scheduled an appointment with Dr. Rajesh Verma (Cardiologist) for tomorrow. Please confirm if you need further assistance."*  
"""


# Function to format chat history correctly
def format_messages(messages):
    formatted = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]  # Set system prompt role to "user"
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"  # Ensure correct roles
        formatted.append({"role": role, "parts": [{"text": msg["content"]}]})
    return formatted

# Function to generate chat responses
def gemini_generator(messages: list) -> Generator:
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=format_messages(messages))
    
    user_input = messages[-1]["content"]  
    response = chat.send_message(user_input, stream=True)

    for chunk in response:
        yield chunk.text

# Page title
st.title("💊 MediConnect: Health Simplified!")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-box user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        with st.chat_message("assistant"):
            st.markdown(f'<div class="chat-box assistant-message">{message["content"]}</div>', unsafe_allow_html=True)

# Chat input functionality
if prompt := st.chat_input("How can I assist you?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-box user-message">{prompt}</div>', unsafe_allow_html=True)

    # Get response from Gemini
    with st.chat_message("assistant"):
        response = st.write_stream(gemini_generator(st.session_state.messages))
    
    # Save response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
