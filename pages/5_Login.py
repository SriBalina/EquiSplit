import streamlit as st
from pymongo import MongoClient
from passlib.hash import bcrypt

# Connect to MongoDB
client = MongoClient("mongodb+srv://lalithaveni16:lIuZaky5tXTytPN7@cluster0.3b4gvq9.mongodb.net/")
db = client["user_authentication"]
collection = db["users"]

# Streamlit UI
def main():
    st.title("Login Page")

    # Initialize session state
    if 'login_status' not in st.session_state:
        st.session_state.login_status = False
        st.session_state.username = None

    # Input Form
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    # Check if the user is registered
    user = collection.find_one({"username": username})
    if user:
        # Login Button
        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state.login_status = True
                st.session_state.username = username
                st.success("Login successful!")
                st.write(f"Welcome, {st.session_state.username}!")
            else:
                st.error("Invalid username or password.")
    else:
        st.warning("User not registered. Please register below.")

    # Registration Form
    email = st.text_input("Email:")
    new_username = st.text_input("New Username:")
    new_password = st.text_input("New Password:", type="password")

    # Register Button
    if st.button("Register"):
        register_user(email, new_username, new_password)
        st.success("Registration successful! You can now log in.")

def authenticate_user(username, password):
    # Find user in the database
    user = collection.find_one({"username": username})

    # Check if the user exists and the password is correct
    if user and bcrypt.verify(password, user["password_hash"]):
        return True
    else:
        return False

def register_user(email, username, password):
    # Hash the password before storing it
    hashed_password = bcrypt.hash(password)

    # Create a new user document
    new_user = {
        "email": email,
        "username": username,
        "password_hash": hashed_password
    }

    # Insert the new user into the database
    collection.insert_one(new_user)

if __name__ == "__main__":
    main()
