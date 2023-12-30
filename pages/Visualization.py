import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
# Connect to MongoDB
client = MongoClient("mongodb+srv://lalithaveni16:lIuZaky5tXTytPN7@cluster0.3b4gvq9.mongodb.net/")
db = client["user_authentication"]
balances_collection = db["balances"]


def fetch_user_balances(username):
    user_balances = []
    
    # Find the user data in the collection
    user_data = balances_collection.find_one({"username": username})

    if user_data:
        transactions = user_data.get("transactions", [])
        for group_data in transactions:
            group_name = group_data["group_name"]
            balances = group_data.get("transactions", [])
            user_balances.append({"group_name": group_name, "balances": balances})

    return user_balances



def main():
    st.title("Expense Balances Visualization")

    # Retrieve username from the session state
    username = st.session_state.get("username", "")

    # Display username
    st.write(f"Welcome, {username}!")

    # Fetch and visualize expense balances for the current user
    if st.button("Fetch Expense Balances"):
        user_balances = fetch_user_balances(username)
        print("User Balances:", user_balances)  # Add this line for debugging

        if user_balances:
            for group_data in user_balances:
                group_name = group_data["group_name"]
                balances = group_data.get("balances", [])
                if balances:
                    # Plotting using Matplotlib for each group
                    
                    df = pd.DataFrame(balances, columns=["Payer", "Payee", "Amount"])
                    plt.figure(figsize=(8, 6))
                    labels = [f"{row['Payer']}\n({row['Payee']})" for index, row in df.iterrows()]

                    plt.pie(df["Amount"], labels=labels, autopct="%1.1f%%", startangle=140)
                    plt.title(f"Expense Balances - {group_name}")
                    st.pyplot(plt)
                else:
                    st.warning(f"No expenses found for group: {group_name}")
                    
        else:
            st.warning("No expense balances found for the current user.")

if __name__ == "__main__":
    main()
