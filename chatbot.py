import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
import boto3
from pandasai import SmartDatalake

def chat_with_data():
    # Load environment variables
    load_dotenv()

    # AWS credentials and region
    access_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_id = os.getenv('AWS_SECRET_ACCESS_KEY')
    region_name = os.getenv('AWS_REGION')

    # Initialize a session using Amazon S3
    session = boto3.Session(
        aws_access_key_id=access_id,
        aws_secret_access_key=secret_id,
        region_name=region_name
    )
    s3 = session.client('s3')

    # Read the CSV file from S3
    response = s3.get_object(Bucket='new-trail01', Key='FIR_Details_Data.csv')
    file_content = response['Body'].read()
    data = pd.read_csv(BytesIO(file_content))

    pandasai_api_key = os.getenv('PANDASAI_API_KEY')
    os.environ['PANDASAI_API_KEY'] = pandasai_api_key

    # Initialize SmartDatalake with the data
    lake = SmartDatalake([data])

    # Streamlit UI
    st.title("Data Chat Bot Interface")
    st.header("Chat with Data")

    user_input = st.chat_input("Ask a question about the data:")

    # Display user question and bot response
    if user_input:
        # Send the question to pandasai and get the response
        try:
            response = lake.chat(user_input)
            st.text_area("Bot Response:", value=response, height=300)
        except Exception as e:
            st.error(f"Error processing your question: {e}")
    else:
        st.write("Please enter a question to start chatting.")


