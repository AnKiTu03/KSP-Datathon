import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import boto3
from pandasai import SmartDatalake
import requests

os.environ["GOOGLE_API_KEY"] = os.getenv('GEN_AI')

load_dotenv()
gen_api = os.getenv('GEN_AI')

genai.configure(api_key = gen_api)
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

def trans(txt):
  

   url = "https://microsoft-translator-text.p.rapidapi.com/translate"

   querystring = {"to[0]":"kn","api-version":"3.0","profanityAction":"NoAction","textType":"plain"}

   payload = [{ "Text": txt }]
   headers = {
	   "content-type": "application/json",
	   "X-RapidAPI-Key": "c9cf11c221msh7ba92db113f7b27p125495jsnd35a5d990324",
	   "X-RapidAPI-Host": "microsoft-translator-text.p.rapidapi.com"
   }

   response = requests.post(url, json=payload, headers=headers, params=querystring)

   if response.status_code == 200:
    parsed_data = response.json()
    translated_text = parsed_data[0]['translations'][0]['text']
    return translated_text
   else:
       return "Server Limit Exceeded"

@st.cache_data(show_spinner=True)   
def load_data_from_s3():
    load_dotenv()
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
    return data


def chat_with_data():
    data =  load_data_from_s3()
    pandasai_api_key = os.getenv('PANDASAI_API_KEY')
    os.environ['PANDASAI_API_KEY'] = pandasai_api_key
   
    llm = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
  safety_settings=safety_settings,
  generation_config=generation_config,)

    # Initialize SmartDatalake with the data
    lake = SmartDatalake([data])

    # Streamlit UI
    st.title("Data Chat Bot Interface")
    st.header("Chat with Data")
    bu = st.toggle("Kannada")

    user_input = st.chat_input("Ask a question about the data:")

    if user_input:
        try:
            with st.spinner("Processing your question..."):
                r = lake.chat(user_input)
                Human_prompt = f"Given the question {user_input} , you will recieve an answer {r} from the Database. Frame an user friendly respone using this."
            
                response = llm.generate_content(Human_prompt)
                response = response.text
                if bu:
                    response = trans(response)
                
            st.text_area("Bot Response:", value=response, height=300)
        except Exception as e:
            st.error(f"Error processing your question: {e}")
    else:
        st.write("Please enter a question to start chatting.")

