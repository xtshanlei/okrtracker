import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from st_files_connection import FilesConnection
import boto3
from io import StringIO

def upload_df_to_s3(df, bucket, file_name):
    # Convert DataFrame to a CSV string
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # Reset the pointer of the buffer to the beginning
    csv_buffer.seek(0)

    # Create an S3 client
    s3_client = boto3.client('s3')

    # Upload the CSV string directly to S3
    s3_client.put_object(Bucket=bucket, Key=file_name, Body=csv_buffer.getvalue())
    st.success('Upload to S3 successfully')

# Function to read a file from S3
def read_csv_from_s3(bucket, file_name):
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=bucket, Key=file_name)
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 200:
        df = pd.read_csv(response.get("Body"))
        return df
    else:
        st.error("Failed to retrieve file from S3")
        return pd.DataFrame()  # Return an empty DataFrame i


# Create connection object and retrieve file contents.
# Specify input format is a csv and to cache the result for 600 seconds.
conn = st.connection('s3', type=FilesConnection)
config_read = conn.read("supervisiontracker/secrets.yaml", input_format = 'text',ttl=10)


# Load configuration from the YAML file
config = yaml.load(config_read, Loader=SafeLoader)
st.write(config)
# Initialize session state for data
if 'okr_data' not in st.session_state:
    st.session_state.okr_data = read_csv_from_s3('supervisiontracker', 'okr.csv')
# Initialize the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Perform the login process
st.sidebar.title(':blue[Student OKR Tracker]')
st.sidebar.write('by :blue[Yulei]')
name, authentication_status, username = authenticator.login('Login', 'main')

# OKR application logic based on authentication status
if authentication_status:
    authenticator.logout('Logout', 'main')

    # Check the username for role-based content display
    if config['credentials']['usernames'][username]['user_role'] == 'admin':
        st.write(f'Welcome Admin *{name}*')
        st.title('Admin View: OKR and Gantt Chart Manager')
        st.dataframe(st.session_state.okr_data)
                # Functionality to remove records
        if st.session_state.okr_data.shape[0] > 0:
            selected_record = st.selectbox("Select a record to remove", st.session_state.okr_data.index)
            if st.button("Remove Record"):
                st.session_state.okr_data = st.session_state.okr_data.drop(selected_record)
                upload_df_to_s3(st.session_state.okr_data, 'supervisiontracker', 'okr.csv')
                st.success("Record removed successfully")
                st.write(st.session_state.okr_data)
    else:
        st.header(f'Welcome :blue[*{name}*]')
        st.subheader('Weekly OKR')

        with st.form("okr_form"):
            week_start = st.date_input("Week Starting Date")
            objectives = st.text_area("Objectives for This Stage")
            key_results = st.text_area("Key Results")
            last_week_plans = st.text_area("Plans from Last Week")
            progress = st.text_area("Progress for Those Plans")
            next_week_plans = st.text_area("Plans for Next Week")

            submitted = st.form_submit_button("Submit")
            if submitted:
                new_data = pd.DataFrame([{"Username": username, "Week Start": week_start, "Objectives": objectives, "Key Results": key_results, "Last Week's Plans": last_week_plans, "Progress": progress, "Next Week's Plans": next_week_plans}])
                st.session_state.okr_data = pd.concat([st.session_state.okr_data, new_data], ignore_index=True)
                upload_df_to_s3(st.session_state.okr_data, 'supervisiontracker', 'okr.csv')
                st.success("OKR Added Successfully")

        # Display OKR data specific to the logged-in user
        user_records = st.session_state.okr_data[st.session_state.okr_data["Username"] == username]
        st.dataframe(user_records)

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
