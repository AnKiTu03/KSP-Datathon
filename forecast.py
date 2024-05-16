import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import os
import boto3
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables
load_dotenv()
access_id = os.getenv('AWS_ACCESS_KEY_ID')
secret_id = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')

@st.cache_data(show_spinner=True)
def load_data_from_s3(bucket_name, file_key):
    session = boto3.Session(
        aws_access_key_id=access_id,
        aws_secret_access_key=secret_id,
        region_name=region_name
    )
    s3 = session.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = response['Body'].read()
    data = pd.read_csv(BytesIO(file_content))
    return data

# Function to load pre-trained model
@st.cache_resource()
def load_model(district):
    model_path = f'models/{district}_model.pkl'
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        st.error(f"No pre-trained model found for {district}.")
        return None

# Function to prepare data for a specific district
@st.cache_data()
def prepare_data(data, district_name):
    district_data = data[data['UnitName'] == district_name]
    district_data['Offence_From_Date'] = pd.to_datetime(district_data['Offence_From_Date'])
    district_data = district_data.set_index('Offence_From_Date')
    return district_data.resample('M').size()

# Function to plot forecast
def plot_forecast(forecast, title):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(forecast['ds'], forecast['yhat'], label='Forecast (yhat)', color='red', marker='o')
    ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.2, label='Forecast Confidence Interval')
    ax.plot(forecast['ds'], forecast['trend'], label='Trend', color='blue', linestyle='--')
    ax.set_title(title)
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Crimes')
    ax.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(fig)

# Main function to run Streamlit app
def forecast_main():
    bucket_name = 'new-trail01'
    file_key = 'FIR_Details_Data.csv'
    
    with st.spinner('Loading data from S3...'):
        data = load_data_from_s3(bucket_name, file_key)
        
    st.title('District-Wise Crime Rate Prediction using Facebook Prophet')

    if 'UnitName' not in data.columns:
        st.error("The dataset does not contain 'UnitName'. Please upload a dataset with location data.")
        return
    
    data = data[data['Offence_From_Date'] >= '2019-01-01']
    data.dropna(subset=['Offence_From_Date', 'UnitName'], inplace=True)
    
    if data.empty:
        st.error("No data available from 2019 onwards. Please check your dataset.")
        return
    
    district_list = data['UnitName'].unique()
    selected_district = st.selectbox('Select a District for Analysis', district_list)
    
    forecast_periods = st.slider('Select number of months to forecast', min_value=12, max_value=48, value=12, step=12)
    
    with st.spinner(f'Loading model for {selected_district}...'):
        model = load_model(selected_district)
    
    if model:
        district_resampled = prepare_data(data, selected_district)
        df_prophet = pd.DataFrame(district_resampled.reset_index())
        df_prophet.columns = ['ds', 'y']
        
        with st.spinner('Generating forecast...'):
            future = model.make_future_dataframe(periods=forecast_periods, freq='M')
            forecast = model.predict(future)
        
        plot_forecast(forecast, f'Forecast Visualization for {selected_district}')
