import streamlit as st
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import boto3
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
access_id = os.getenv('AWS_ACCESS_KEY_ID')
secret_id = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')



def load_data_from_s3():
    session = boto3.Session(
        aws_access_key_id=access_id,
        aws_secret_access_key=secret_id,
        region_name=region_name
)
    s3 = session.client('s3')
    response = s3.get_object(Bucket='new-trail01', Key='FIR_Details_Data.csv')
    file_content = response['Body'].read()
    data = pd.read_csv(BytesIO(file_content))
    return data


@st.cache_data()
def prepare_data(data, district_name):
    district_data = data[data['District_Name'] == district_name]
    # Ensure the 'Offence_From_Date' column is set as a DatetimeIndex
    district_data['Offence_From_Date'] = pd.to_datetime(district_data['Offence_From_Date'])
    district_data = district_data.set_index('Offence_From_Date')  # Set the index
    return district_data.resample('M').size()


@st.cache_resource()
def prophet_forecast(district_resampled, periods):
    df_prophet = pd.DataFrame(district_resampled.reset_index())
    df_prophet.columns = ['ds', 'y']
    model = Prophet()
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=periods, freq='M')
    forecast = model.predict(future)
    return forecast

@st.cache_data()
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


def forecast_main():
    st.title('District-Wise Crime Rate Prediction using Facebook Prophet')
    data = load_data_from_s3()
    if 'District_Name' not in data.columns:
        st.error("The dataset does not contain 'District_Name'. Please upload a dataset with location data.")
        return
    
    data = data[data['Offence_From_Date'] >= '2019-01-01']
    data.dropna(subset=['Offence_From_Date', 'District_Name'], inplace=True)
    
    if data.empty:
        st.error("No data available from 2019 onwards. Please check your dataset.")
        return
    
    district_list = data['District_Name'].unique()
    selected_district = st.selectbox('Select a District for Analysis', district_list)
    district_resampled = prepare_data(data, selected_district)
    
    if district_resampled.empty:
        st.error(f"No data available for {selected_district} from 2019 onwards. Please select another district.")
        return
    
    forecast_periods = st.slider('Select number of months to forecast', min_value=1, max_value=48, value=12)
    forecast = prophet_forecast(district_resampled, forecast_periods)
    
    plot_forecast(forecast, f'Forecast Visualization for {selected_district}')

if __name__ == "__main__":
    forecast_main()
