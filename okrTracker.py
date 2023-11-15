import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth

# Initialize session state for data
if 'okr_data' not in st.session_state:
    st.session_state.okr_data = pd.DataFrame(columns=["Username", "Week Start", "Objectives", "Key Results", "Last Week's Plans", "Progress", "Next Week's Plans"])

# Prepare the authenticator configuration
hashed_passwords = {
    st.secrets.jsmith['username']: st.secrets.jsmith['password'],
    st.secrets.ccook['username']: st.secrets.ccook['password'],
    st.secrets.yulei['username']: st.secrets.yulei['password']
}

credentials = {
    'usernames': {
        st.secrets.jsmith['username']: st.secrets.jsmith['name'],
        st.secrets.ccook['username']: st.secrets.ccook['name'],
        st.secrets.yulei['username']: st.secrets.yulei['name']
    }
}

# Initialize the authenticator
authenticator = stauth.Authenticate(
    credentials,
    st.secrets.cookie_name,
    st.secrets.cookie_key,
    st.secrets.cookie_expiry_days,
    st.secrets.preauthorized_emails
)

# Perform the login process
name, authentication_status, username = authenticator.login('Login', 'main')

# OKR application logic based on authentication status
if authentication_status:
    # Logout button
    if st.button('Logout'):
        authenticator.logout('main')
        st.write("You have been logged out")

    # Determine user's role
    if username == st.secrets.jsmith['username'] and st.secrets.jsmith['user_role'] == 'admin':
        user_role = 'admin'
    elif username == st.secrets.yulei['username'] and st.secrets.yulei['user_role'] == 'admin':
        user_role = 'admin'
    else:
        user_role = 'user'

    if user_role == 'admin':
        st.write(f'Welcome Admin *{name}*')
        st.title('Admin View: OKR and Gantt Chart Manager')
        st.write(st.session_state.okr_data)
    else:
        st.write(f'Welcome *{name}*')
        st.title('Student OKR and Gantt Chart Manager')

        # OKR form for regular users
        with st.form("okr_form"):
            # ... (form fields go here)

            submitted = st.form_submit_button("Submit")
            if submitted:
                # ... (handle form submission)

        # Display user-specific OKR data
        user_records = st.session_state.okr_data[st.session_state.okr_data["Username"] == username]
        st.write(user_records)

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
