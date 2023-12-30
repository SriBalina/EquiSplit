import streamlit as st
from collections import defaultdict
import streamlit as st
import pymongo
from collections import defaultdict


        
mongo_username = st.secrets.secrets.mongo_username
mongo_password = st.secrets.secrets.mongo_password

# MongoDB connection URI
mongo_uri = f"mongodb+srv://{mongo_username}:{mongo_password}@cluster0.bf0tukv.mongodb.net/test?retryWrites=true&w=majority"
client = pymongo.MongoClient(mongo_uri)
db = client["user_authentication"]
balances_collection = db["balances"]

def store_balances(username, group_name, transactions):
    try:
        # Store or update transactions in MongoDB if username is provided
        if username:
            balances_collection.update_one(
                {"username": username},
                {"$push": {"transactions": {"group_name": group_name, "transactions": transactions}}},
                upsert=True
            )
            st.success("Balances stored successfully!")
    except Exception as e:
        st.error(f"An error occurred while storing balances: {str(e)}")




def splitwise_calculator(group):
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
    print(transactions)
    transactions=simplify_transactions(transactions)
    return transactions




def simplify_transactions(transactions):
    balances = defaultdict(float)

    # Calculate net balance for each person
    for debtor, creditor, amount in transactions:
        balances[debtor] -= amount
        balances[creditor] += amount

    simplified_transactions = []

    while True:
        # Find the person with the maximum positive balance (creditor)
        creditor = max(balances, key=balances.get)
        
        # Find the person with the maximum negative balance (debtor)
        debtor = min(balances, key=balances.get)

        # If either debtor or creditor has a zero balance, break the loop
        if balances[creditor] == 0 or balances[debtor] == 0:
            break

        # Calculate the amount to be settled
        settled_amount = min(abs(balances[creditor]), abs(balances[debtor]))

        # Update balances and add the transaction to the result
        balances[creditor] -= settled_amount
        balances[debtor] += settled_amount
        simplified_transactions.append((debtor, creditor, settled_amount))

    return simplified_transactions



# Streamlit app
st.title("Splitwise Group Expenses")

# Create or Load a group
group_name = st.text_input("Enter Group Name:")
group_key = f"group_{group_name.lower().replace(' ', '_')}"
group = st.session_state.get(group_key, {"members": [], "expenses": []})

# Add members to the group
st.header("Group Members")
new_member = st.text_input("Add a new member:")
if st.button("Add Member") and new_member.strip() != "":
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
    st.write("### Transactions:")
    for transaction in transactions:
        debtor, creditor, amount = transaction
        st.write(f"{debtor} pay Rs.{amount:.2f} to {creditor}")
    try:
        username = st.session_state.username
        store_balances(username, group_name, transactions)
    except Exception as e:
        st.warning(f"You are not logged in. Please log in to store details.")   
