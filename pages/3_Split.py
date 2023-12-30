import streamlit as st
from pymongo import MongoClient
from st_pages import Page, show_pages, hide_pages

# Connect to MongoDB
client = MongoClient("mongodb+srv://lalithaveni16:lIuZaky5tXTytPN7@cluster0.3b4gvq9.mongodb.net/")
db = client["user_authentication"]
balances_collection = db["balances"]


def store_balances(username, group_name, transactions):
    # Store or update transactions in MongoDB
    balances_collection.update_one(
        {"username": username},
        {"$push": {"transactions": {"group_name": group_name, "transactions": transactions}}},
        upsert=True
    )

def retrieve_all_transactions(username):
    # Retrieve all transactions for a user from MongoDB
    user_data = balances_collection.find_one({"username": username})
    return user_data.get("transactions", []) if user_data else []

def splitwise_calculator(group):
    # ... (rest of your code)
    # Calculate the total amount spent by each person
    total_spent = {member: 0 for member in group["members"]}
    
    # Calculate the amount owed or to be reimbursed for each person
    balances = {member: 0 for member in group["members"]}
    transactions = []

    for expense in group["expenses"]:
        payer = expense["payer"]
        amount_paid = expense["amount_paid"]
        consumers = expense["consumers"]
        
        total_spent[payer] += amount_paid

        # Update balances for the consumers
        for consumer in consumers:
            if consumer != payer:
                balances[consumer] += amount_paid / len(consumers)
                transactions.append((consumer, payer, amount_paid / len(consumers)))

    return transactions


# Streamlit app
st.title("Splitwise Group Expenses")
st.write(f"Welcome, {st.session_state.username}!")



# Retrieve username and group name from session state
username = st.session_state.username

## Button to show previous transactions
if st.button("Show Previous Transactions"):
    previous_transactions = retrieve_all_transactions(username)
    st.write("### Previous Transactions:")
    for group_transaction in previous_transactions:
        group_name = group_transaction.get("group_name", "")
        transactions_list = group_transaction.get("transactions", [])
        st.write(f"Group: {group_name}")
        for transaction in transactions_list:
            st.write(transaction)
        

group_name = st.text_input("Enter Group Name:")
group_key = f"group_{group_name.lower().replace(' ', '_')}"
group = st.session_state.get(group_key, {"members": [], "expenses": []})



# ... (rest of your code)
# Add members to the group
st.header("Group Members")
new_member = st.text_input("Add a new member:")
if st.button("Add Member"):
    group["members"].append(new_member.strip())
    st.session_state[group_key] = group

# Display current group members
st.write("### Members:")
for member in group["members"]:
    st.write(f"- {member}")

# Record expenses
st.header("Record Expenses")
payer = st.selectbox("Select the person who paid:", group["members"])
amount_paid = st.number_input("Enter the amount paid:")
consumers = st.multiselect("Select people sharing the expense:", group["members"])

if st.button("Record Expense") and amount_paid > 0 and consumers:
    expense = {"payer": payer, "amount_paid": amount_paid, "consumers": consumers}
    group["expenses"].append(expense)
    st.session_state[group_key] = group



# Calculate and display the result when the "Calculate" button is clicked
if st.button("Calculate Splitwise"):
    transactions = splitwise_calculator(group)

    # Store balances in MongoDB
    store_balances(username, group_name, transactions)

    st.write("### Transactions:")
    for transaction in transactions:
        debtor, creditor, amount = transaction
        st.write(f"{debtor} pay Rs.{amount:.2f} to {creditor}")

