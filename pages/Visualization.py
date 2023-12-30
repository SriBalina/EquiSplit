import streamlit as st
import plotly.express as plt
import pandas as pd
import pymongo
# Connect to MongoDB
mongo_username = st.secrets.secrets.mongo_username
mongo_password = st.secrets.secrets.mongo_password

# MongoDB connection URI
mongo_uri = f"mongodb+srv://{mongo_username}:{mongo_password}@cluster0.bf0tukv.mongodb.net/test?retryWrites=true&w=majority"
client = pymongo.MongoClient(mongo_uri)
db = client["user_authentication"]
balances_collection = db["balances"]


def fetch_user_balances(username):
    user_balances = []
    
    # Find the user data in the collection
    user_data = balances_collection.find_one({"username": username})

    if user_data:
        transactions = user_data.get("transactions", [])
        print(transactions)
        for group_data in transactions:
            group_name = group_data["group_name"]
            balances = group_data.get("transactions", [])
            user_balances.append({"group_name": group_name, "balances": balances})

    return user_balances



def main():
    st.title("Expense Balances Visualization")

    # Retrieve username from the session state
    username = st.session_state.get("username", "")
    if username:
        st.write(f"Welcome, {username}!")
    else:
        st.write(f"Login to Fetch")
    # Display username
    

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
                    # Create labels for the pie chart
                    df["Labels"] = [f"{row['Payer']} ({row['Payee']})" for _, row in df.iterrows()]

                    # Create a pie chart using plotly.express
                    fig = plt.pie(df, values="Amount", names="Labels", title=f"Expense Balances - {group_name}", 
                                template="plotly", hole=0.4)

                    # Show the plot using Streamlit
                    st.plotly_chart(fig)
                else:
                    st.warning(f"No expenses found for group: {group_name}")
                    
        else:
            st.warning("No expense balances found for the current user.")

if __name__ == "__main__":
    main()
