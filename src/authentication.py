import streamlit as st

def st_auth_ui():
    _, middle, _ = st.columns([0.4,0.3,0.4])

    if "auth_input" not in st.session_state:
        st.session_state["auth_input"] = "login"

    with middle.container(border=True):

        if st.session_state["auth_input"] == "login":
            login_ui()
        else:
            register_ui()


def login_ui():
    left, right = st.columns([0.6, 0.4], vertical_alignment="center")

    left.markdown("### Login")
    if right.button("Register", use_container_width=True):
        st.session_state["auth_input"] = "register"
        st.rerun()
    st.text_input("Username", key="login_username_input")
    st.text_input("Password", type="password", key="login_password_input")
    if st.button("Login", use_container_width=True):
        athenticated = True
        if athenticated:
            st.toast("Logged in successfully!", icon="✔️")
        else:
            st.toast("Incorrect Username or password", icon="⛔")

def register_ui():
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
        elif username in "used usernames from db":
            st.toast("Username already in use, please choose another", icon="⛔")
        else:
            # TODO: create an entry in users table that doesnt exist
            st.session_state["auth_input"] = "login"
            st.toast("Account Registered", icon="✔️")
