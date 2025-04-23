import streamlit as st
import hashlib
from cryptography.fernet import Fernet

if "fernet_key" not in st.session_state:
    st.session_state.fernet_key = Fernet.generate_key()
cipher = Fernet(st.session_state.fernet_key)

if "stored_data" not in st.session_state:
    st.session_state.stored_data = {}

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text, passkey):
    hashed_passkey = hash_passkey(passkey)

    for data in st.session_state.stored_data.values():
        if data["encrypted_text"] == encrypted_text and data["passkey"] == hashed_passkey:
            st.session_state.failed_attempts = 0
            return cipher.decrypt(encrypted_text.encode()).decode()

    st.session_state.failed_attempts += 1
    return None

st.set_page_config(page_title="Secure Data Encryption", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .stTextInput input {
        padding: 10px;
        font-size: 16px;
    }
    .stTextArea textarea {
        padding: 10px;
        font-size: 16px;
    }
    .stSuccess, .stError, .stWarning {
        font-size: 18px;
        font-weight: bold;
    }
    .stInfo {
        font-size: 16px;
    }

    .css-1d391kg {
        background-color: #1d1f27;
        padding-top: 20px;
        padding-bottom: 20px;
    }

    .css-1q2q4r6 {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
        padding: 10px;
        margin-top: 20px;
        border-radius: 5px;
        cursor: pointer;
    }

    .css-1q2q4r6:hover {
        background-color: #3a3f56;
    }
    </style>
""", unsafe_allow_html=True)

menu = ["Home", "Store Data", "Retrieve Data", "Login", "How to Use"]

if st.session_state.get("force_login"):
    choice = "Login"
else:
    choice = st.sidebar.radio("Navigate", menu)

if choice == "Home":
    st.subheader("🏠 Welcome to the Secure Data System")
    st.info("Use this app to **store & retrieve data securely** using encrypted keys. All data is kept in memory (no files or databases).")

elif choice == "Store Data":
    st.subheader("📂 Store Data Securely")
    st.write("Enter the data you want to encrypt and create a passkey for access.")

    user_data = st.text_area("Enter Data to Encrypt:")
    passkey = st.text_input("Create a Passkey:", type="password")

    if st.button("Encrypt & Store"):
        if user_data and passkey:
            hashed_pass = hash_passkey(passkey)
            encrypted_text = encrypt_data(user_data)
            st.session_state.stored_data[encrypted_text] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_pass
            }
            st.success("✅ Data encrypted and stored successfully!")
            st.code(encrypted_text, language="text")
        else:
            st.warning("⚠️ Please enter both data and a passkey.")

elif choice == "Retrieve Data":
    st.subheader("🔍 Retrieve Your Data")
    st.write("Enter the encrypted data and your passkey to decrypt.")

    encrypted_input = st.text_area("Enter Encrypted Data:")
    passkey_input = st.text_input("Enter Your Passkey:", type="password")

    if st.button("Decrypt"):
        if encrypted_input and passkey_input:
            result = decrypt_data(encrypted_input, passkey_input)
            if result:
                st.success("✅ Decryption Successful!")
                st.write("**Decrypted Data:**")
                st.code(result, language="text")
            else:
                st.error(f"❌ Incorrect passkey! Attempts remaining: {3 - st.session_state.failed_attempts}")
                if st.session_state.failed_attempts >= 3:
                    st.warning("🔐 Too many failed attempts! Please reauthorize.")
                    st.session_state.force_login = True
                    st.rerun()
        else:
            st.warning("⚠️ Please provide both the encrypted text and passkey.")

elif choice == "Login":
    st.subheader("🔑 Reauthorization Required")
    st.write("You have failed 3 times to decrypt the data. Please enter the master password to continue.")

    master_password = st.text_input("Enter Master Password:", type="password")

    if st.button("Login"):
        if master_password == "admin123":
            st.session_state.failed_attempts = 0
            st.success("✅ Logged in successfully. You may now try again.")
            st.session_state.force_login = False
            st.rerun()
        else:
            st.error("❌ Wrong password! Access denied.")

elif choice == "How to Use":
    st.subheader("📘 How to Use the Secure Data System")
    st.markdown("""
    **Step-by-step guide to using this app:**

    1. **Go to 'Store Data'**
       - Enter the information you want to keep safe.
       - Create a secret passkey.
       - Click **Encrypt & Store**.

    2. **Copy Encrypted Data**
       - After storing, copy the encrypted code shown.
       - This is your reference to retrieve the data later.

    3. **Go to 'Retrieve Data'**
       - Paste the encrypted data you copied.
       - Enter the same passkey.
       - Click **Decrypt** to view the original message.

    4. **Too many wrong tries?**
       - After 3 failed decryption attempts, you will be redirected to the **Login** page.
       - Use master password: `admin123` to regain access.

    5. **Note:**
       - This app only stores data temporarily (session-based).
       - Do not close or refresh the page unless you saved your encrypted key.
    """)
