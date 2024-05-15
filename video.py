import streamlit as st
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tempfile import NamedTemporaryFile


CLASS_LABELS = ['Abuse', 'Arrest', 'Arson', 'Assault',
                'Burglary', 'Explosion', 'Fighting',
                'Normal', 'RoadAccidents', 'Robbery',
                'Shooting', 'Shoplifting', 'Stealing',
                'Vandalism']

def load_model_file(model_path='video_model.h5'):
    return load_model(model_path)

def preprocess_frame(frame):

    frame = cv2.resize(frame, (64, 64))  
    frame = frame / 255.0  
    frame = np.expand_dims(frame, axis=0)  
    return frame

def predict_on_video(video_path, model):

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)  # Get the frames per second of the video
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps

    all_predictions = []
    current_frame = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if current_frame % int(fps) == 0:
            processed_frame = preprocess_frame(frame)
            prediction = model.predict(processed_frame)
            all_predictions.append(prediction)

        current_frame += 1

    cap.release()

    avg_prediction = np.mean(all_predictions, axis=0)
    avg_class_index = np.argmax(avg_prediction)
    avg_class_label = CLASS_LABELS[avg_class_index]
    return avg_class_label

def video_main():
    st.title("Video Classification with ResNet50")
    model = load_model_file()

    uploaded_file = st.file_uploader("Choose a video...", type=["mp4", "avi", "mov"])

    if uploaded_file is not None:
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_video_path = temp_file.name

        st.video(uploaded_file)

        if st.button("Predict"):
            with st.spinner('Processing...'):
                avg_class_label = predict_on_video(temp_video_path, model)
            st.success(f"Most Likely Class Label: {avg_class_label}")


