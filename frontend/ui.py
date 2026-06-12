import streamlit as st
import requests
import pyrebase

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>

.main-title{
    text-align:center;
    font-size:40px;
    font-weight:bold;
    color:#4CAF50;
}

.user{
    color:#4CAF50;
    font-weight:bold;
}

.assistant{
    color:#00B0FF;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# API URL
# =========================================================
API_URL = "https://ai-research-agent-backend-1.onrender.com/api/chat"
HISTORY_URL = "https://ai-research-agent-backend-1.onrender.com/api/history"

# =========================================================
# FIREBASE CONFIG
# =========================================================
firebaseConfig = {
    "apiKey": "AIzaSyCJ1dJif8R7Or5xsMXLKImWNVGwOGalJtE",
    "authDomain": "shopify-ai-support-agent.firebaseapp.com",
    "databaseURL": "https://shopify-ai-support-agent-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "shopify-ai-support-agent",
    "storageBucket": "shopify-ai-support-agent.firebasestorage.app",
    "messagingSenderId": "286570662798",
    "appId": "1:286570662798:web:525b8174650a8f6ee7f2df",
    "measurementId": "G-5ES202VKJT"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# =========================================================
# SESSION STATE
# =========================================================
if "token" not in st.session_state:
    st.session_state.token = None

if "email" not in st.session_state:
    st.session_state.email = None


# =========================================================
# TITLE
# =========================================================
st.markdown('<div class="main-title">🤖 AI Research Assistant</div>', unsafe_allow_html=True)
st.markdown("---")

# =========================================================
# LOGIN / SIGNUP
# =========================================================
if st.session_state.token is None:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.subheader("Login")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)

                st.session_state.token = user["idToken"]
                st.session_state.email = user["email"]

                st.success("Login Successful")
                st.rerun()

            except Exception as e:
                st.error("Login Failed")
                st.write(e)

    with tab2:
        st.subheader("Signup")

        email = st.text_input("Signup Email", key="signup_email")
        password = st.text_input("Signup Password", type="password", key="signup_password")

        if st.button("Create Account"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("Account Created!")
            except Exception as e:
                st.error("Signup Failed")
                st.write(e)

# =========================================================
# CHAT APP
# =========================================================
else:

    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    # =====================================================
    # LOAD HISTORY FROM POSTGRES (LANGGRAPH)
    # =====================================================
    history = []
    topics = []

    try:
        res = requests.get(HISTORY_URL, headers=headers, timeout=20)

        if res.status_code == 200:
            data = res.json()

            topics = data.get("topics", [])
            history = data.get("messages", [])

    except Exception as e:
          topics = []
        

    # =====================================================
    # SIDEBAR
    # =====================================================
    with st.sidebar:

        st.success(f"Logged in as {st.session_state.email}")

        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.email = None
            st.rerun()

        st.divider()
        st.subheader("📌 Latest Topic")

        for t in topics:
           st.markdown(f"- {t}")

        

        

        st.divider()
        st.subheader("🧠 AI Features")
        st.info("✔ LangGraph Agent")
        st.info("✔ Postgres Memory")
        st.info("✔ FastAPI Backend")
        st.info("✔ Firebase Auth")

    # =====================================================
    # MAIN CHAT
    # =====================================================
    st.subheader("💬 Chat with AI Research Assistant")

    # show DB history in chat window
    for msg in history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask your research question...")

    if user_input and user_input.strip():

        with st.chat_message("user"):
            st.write(user_input)

        placeholder = st.chat_message("assistant").empty()

        try:
            with st.spinner("Researching..."):

                res = requests.post(
                    API_URL,
                    json={"query": user_input},
                    headers=headers,
                    timeout=60
                )

            if res.status_code == 200:
                response_text = res.json().get("answer", "No response")
            else:
                response_text = f"Error {res.status_code}: {res.text}"

        except Exception as e:
            response_text = f"Request failed: {str(e)}"

        placeholder.write(response_text)