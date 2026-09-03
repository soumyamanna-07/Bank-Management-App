"""Streamlit front end for the bank.

Run it with:  streamlit run app.py
"""

import streamlit as st

from bank import MAX_DEPOSIT, MIN_AGE, PIN_LENGTH, Bank, BankError

st.set_page_config(page_title="Bank Management", page_icon="₹", layout="centered")


@st.cache_resource
def get_bank() -> Bank:
    """One Bank instance shared across reruns, so data.json is read only once."""
    return Bank()


try:
    bank = get_bank()
except BankError as err:
    st.error(str(err))
    st.stop()

st.session_state.setdefault("account_no", None)
st.session_state.setdefault("pin", None)


def sign_in(record: dict) -> None:
    st.session_state.account_no = record["accountNo"]
    st.session_state.pin = record["pin"]


def sign_out() -> None:
    st.session_state.account_no = None
    st.session_state.pin = None


def money(amount: float) -> str:
    return f"{amount:,.2f}"


# ---------------------------------------------------------------- signed out

if st.session_state.account_no is None:
    st.title("Bank Management")
    st.caption("Sign in with your account number, or open a new account.")

    existing, new = st.tabs(["Sign in", "Open an account"])

    with existing:
        with st.form("sign_in"):
            account_no = st.text_input("Account number")
            pin = st.text_input("PIN", type="password", max_chars=PIN_LENGTH)
            submitted = st.form_submit_button("Sign in")

        if submitted:
            try:
                record = bank.authenticate(account_no, pin)
            except BankError as err:
                st.error(str(err))
            else:
                sign_in(record)
                st.rerun()

    with new:
        with st.form("create_account"):
            name = st.text_input("Full name")
            age = st.number_input("Age", min_value=0, max_value=120, step=1, value=18)
            email = st.text_input("Email")
            pin = st.text_input(
                f"Choose a {PIN_LENGTH}-digit PIN", type="password", max_chars=PIN_LENGTH
            )
            submitted = st.form_submit_button("Open account")

        if submitted:
            try:
                record = bank.create_account(name, int(age), email, pin)
            except BankError as err:
                st.error(str(err))
            else:
                st.success("Your account is open. Write this number down.")
                st.code(record["accountNo"], language=None)
                st.caption("You will need it every time you sign in.")

        st.caption(f"You have to be {MIN_AGE} or older to open an account.")

    st.stop()


# ----------------------------------------------------------------- signed in

user = bank.find(st.session_state.account_no, st.session_state.pin)
if user is None:
    # The account was closed or the PIN changed in another session.
    sign_out()
    st.rerun()

with st.sidebar:
    st.write(user["name"])
    st.caption(user["accountNo"])
    if st.button("Sign out"):
        sign_out()
        st.rerun()

st.title(f"Hello, {user['name'].split()[0]}")
st.metric("Balance", money(user["balance"]))

deposit_tab, withdraw_tab, details_tab, update_tab, close_tab = st.tabs(
    ["Deposit", "Withdraw", "Details", "Update", "Close account"]
)

with deposit_tab:
    with st.form("deposit"):
        amount = st.number_input(
            "Amount", min_value=0.0, max_value=float(MAX_DEPOSIT), step=100.0
        )
        submitted = st.form_submit_button("Deposit")

    if submitted:
        try:
            balance = bank.deposit(user["accountNo"], user["pin"], amount)
        except BankError as err:
            st.error(str(err))
        else:
            st.success(f"Deposited {money(amount)}. Your balance is {money(balance)}.")
            st.rerun()

    st.caption(f"Single deposits are capped at {MAX_DEPOSIT:,}.")

with withdraw_tab:
    with st.form("withdraw"):
        amount = st.number_input("Amount", min_value=0.0, step=100.0, key="withdraw_amt")
        submitted = st.form_submit_button("Withdraw")

    if submitted:
        try:
            balance = bank.withdraw(user["accountNo"], user["pin"], amount)
        except BankError as err:
            st.error(str(err))
        else:
            st.success(f"Withdrew {money(amount)}. Your balance is {money(balance)}.")
            st.rerun()

with details_tab:
    st.write(
        {
            "Name": user["name"],
            "Age": user["age"],
            "Email": user["email"],
            "Account number": user["accountNo"],
            "Balance": money(user["balance"]),
        }
    )

with update_tab:
    st.caption("Leave a field empty to keep what you have now.")

    with st.form("update"):
        name = st.text_input("New name", placeholder=user["name"])
        email = st.text_input("New email", placeholder=user["email"])
        new_pin = st.text_input("New PIN", type="password", max_chars=PIN_LENGTH)
        submitted = st.form_submit_button("Save changes")

    if submitted:
        try:
            record = bank.update_details(
                user["accountNo"], user["pin"], name, email, new_pin
            )
        except BankError as err:
            st.error(str(err))
        else:
            sign_in(record)  # the PIN may have changed
            st.success("Details saved.")
            st.rerun()

    st.caption("Age, account number and balance cannot be edited here.")

with close_tab:
    st.warning("Closing an account removes it permanently.")
    confirm = st.checkbox("I understand this cannot be undone")

    if st.button("Close my account", disabled=not confirm):
        try:
            bank.close_account(user["accountNo"], user["pin"])
        except BankError as err:
            st.error(str(err))
        else:
            sign_out()
            st.rerun()
