import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import boto3
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
access_id = os.getenv('AWS_ACCESS_KEY_ID')
secret_id = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')

@st.cache_data(experimental_allow_widgets=True, show_spinner=True) 
def load_data_from_s3():
    session = boto3.Session(
        aws_access_key_id=access_id,
        aws_secret_access_key=secret_id,
        region_name=region_name
)
    s3 = session.client('s3')
    response = s3.get_object(Bucket='new-trail01', Key='VictimInfoDetails.csv')
    file_content = response['Body'].read()
    data = pd.read_csv(BytesIO(file_content))
    return data

def plot_bar_graph_features(filtered_data, feature_type):
    if filtered_data.empty:
        st.error('No data available for this selection.')
        return
    feature_counts = filtered_data[feature_type].value_counts().sort_index()
    top_features = feature_counts.sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    plt.bar(top_features.index, top_features.values, color='blue')
    plt.xlabel(feature_type)
    plt.ylabel('Number of Victims')
    plt.title(f'Top 10 {feature_type} with Highest Number of Victims')
    plt.xticks(rotation=45)
    st.pyplot()

def Victim_main():
    st.title('Spatial Analysis of Victim Database')
    data = load_data_from_s3()
    selected_district = st.selectbox('Select District', [''] + sorted(data['District_Name'].unique()))
    
    if selected_district:
        filtered_data = data[data['District_Name'] == selected_district]
        if filtered_data.empty:
            st.write("No data available for the selected district.")
            return
        
        selected_unit = st.selectbox('Select Unit Name', [''] + sorted(filtered_data['UnitName'].unique()))
        
        if selected_unit:
            filtered_data = filtered_data[filtered_data['UnitName'] == selected_unit]
            if filtered_data.empty:
                st.write("No data available for the selected unit.")
                return
            
            feature_type = st.radio("Select Feature Type", ["Sex", "Caste", "Profession", "PersonType", "InjuryType", "PresentCity", "PresentState", "Nationality_Name", "Age"])
            
            if feature_type:
                plot_bar_graph_features(filtered_data, feature_type)


