import pandas as pd
from sklearn.cluster import KMeans
import folium
from folium.plugins import MarkerCluster
import streamlit as st
from streamlit_folium import folium_static
import boto3
from io import BytesIO

import os
from dotenv import load_dotenv

load_dotenv()
access_id = os.getenv('AWS_ACCESS_KEY_ID')
secret_id = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')


def apply_kmeans(df, n_clusters=10):
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    df['cluster'] = kmeans.fit_predict(df[['Latitude', 'Longitude']])
    return df, kmeans.cluster_centers_

def visualize_clusters(df, centers):
    map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
    map = folium.Map(location=map_center, zoom_start=12)
    marker_cluster = MarkerCluster().add_to(map)

    for _, row in df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.Icon(icon='record', color='red'),
        ).add_to(marker_cluster)

    for center in centers:
        folium.Marker(
            location=center,
            icon=folium.Icon(icon='star', color='blue'),
            popup='Patrol Center'
        ).add_to(map)

    return map


def patrolling_main(data):
    st.title('Patrolling Map')
    data.dropna(subset=['Latitude', 'Longitude'], inplace=True)
    df = data.drop_duplicates(subset=['Latitude', 'Longitude', 'CrimeHead_Name'])
    clusters = st.slider('Select number of clusters', min_value=3, max_value=20, value=10, step=1)
    df, centers = apply_kmeans(df, clusters)
    crime_map = visualize_clusters(df, centers)
    folium_static(crime_map)

