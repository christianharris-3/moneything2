import streamlit as st
from src.sql_database import SQLDatabase
import pandas as pd
import bcrypt

def st_auth_ui():
    users_df = load_users()
    _, middle, _ = st.columns([0.4,0.3,0.4])

    if "auth_input" not in st.session_state:
        st.session_state["auth_input"] = "login"

    with middle.container(border=True):

        if st.session_state["auth_input"] == "login":
            login_ui(users_df)
        else:
            register_ui(users_df)


def login_ui(users_df):
    left, right = st.columns([0.6, 0.4], vertical_alignment="center")

    left.markdown("### Login")
    if right.button("Register", use_container_width=True):
        st.session_state["auth_input"] = "register"
        st.rerun()
    username = st.text_input("Username", key="login_username_input")
    password = st.text_input("Password", type="password", key="login_password_input")
    if st.button("Login", use_container_width=True):
        user_id = login(users_df, username, password)
        if user_id is None:
            st.toast("Incorrect Username or password", icon="⛔")
        else:
            st.toast("Logged in successfully!", icon="✔️")
            st.session_state["authenticated"] = True
            st.session_state["current_user_id"] = user_id
            st.switch_page("pages/1_Input_Transactions.py")

def register_ui(users_df):
    left, right = st.columns([0.6, 0.4], vertical_alignment="center")

    left.markdown("### Register")
    if right.button("Login", use_container_width=True, key="swap_to_login_ui_button"):
        st.session_state["auth_input"] = "login"
        st.rerun()
    username = st.text_input("Username", key="register_username_input")
    password1 = st.text_input("Password", type="password", key="register_password_1_input")
    password2 = st.text_input("Repeat Password", type="password", key="register_password_2_input")
    if st.button("Register", use_container_width=True):
        if password1 != password2:
            st.toast("Passwords must be the same", icon="⛔")
        elif username is None or username == "":
            st.toast("Username must be at least 1 character", icon="⛔")
        elif username in users_df["username"].values:
            st.toast("Username already in use, please choose another", icon="⛔")
        else:
            register_user(username, password1)
            st.session_state["auth_input"] = "login"
            st.toast("Account Registered", icon="✔️")

def load_users():
    db = SQLDatabase(has_user_id=False)
    db.create_tables()

    cursor = db.execute_sql(
        "SELECT * FROM Users"
    )
    users = cursor.fetchall()
    users_df = pd.DataFrame(
        users,
        columns=[
            "user_id",
            "username",
            "password_hash"
        ]

    )

    return users_df

def register_user(username, password):
    db = SQLDatabase()
    db.add_user(
        username,
        hash_password(password)
    )

def hash_password(password):
    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()
    return password_hash

def check_password(password, password_hash):
    return bcrypt.hashpw(
        password.encode(),
        password_hash.encode()
    )

def login(user_df, username, password):
    filtered_df = user_df[user_df["username"] == username]
    if len(filtered_df) == 0:
        return None
    row = filtered_df.iloc[0]
    password_hash = row["password_hash"]
    if check_password(password, password_hash):
        return row["user_id"]
    return None
