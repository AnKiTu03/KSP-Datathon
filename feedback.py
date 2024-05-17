import streamlit as st
import streamlit_survey as ss
from firebase_admin import credentials, firestore, initialize_app, get_app

survey = ss.StreamlitSurvey()
# Initialize Firebase Admin
def init_firebase():
    try:
        # Try to get the existing app, if it has already been initialized
        app = get_app()
    except ValueError as e:
        # If no app is initialized yet, initialize one
        cred = credentials.Certificate('datathon-ksp-firebase-adminsdk-bq5gw-c742dc8077.json')
        app = initialize_app(cred)
    return firestore.client(app)

db = init_firebase()

def feedback_main():
    st.title("Feedback Form")
    st.write(r"$\textsf{\Large Name*}$")
    name = st.text_input("Name",label_visibility="collapsed")
    st.write(r"$\textsf{\Large Contact(Email)*}$")
    email = st.text_input("Email",label_visibility="collapsed")
    st.write(" ")
    st.write(r"$\textsf{\Large Most useful feature}$")
    Selected_feature = survey.selectbox("Most useful feature", options=['DashBoard', 'MapView', 'Video Analysis', 'Victim Analysis','Forecast'],label_visibility="collapsed")
    st.write(" ")
    st.write(r"$\textsf{\Large Overall functioning of all the features}$")
    overall = survey.select_slider(
            "overall functioning of all the features", options=["Bad", "Slightly Bad", "Neutral", "Good", "Great"],label_visibility="collapsed"
        )
    st.write(" ")
    st.write(r"$\textsf{\Large User Interface}$")
    user_interface = st.select_slider(
            "User Interface",
            options=["Very Bad", "Bad", "Neutral", "Good", "Very Good"],label_visibility="collapsed"
        )
    st.write(" ")
    st.write(r"$\textsf{\Large Recommendations for Improvement}$")
    st.write(" ")   
    recommendations = st.text_area("Recommendations for Improvement",label_visibility="collapsed")
        
    submit = st.button("Submit")
    if submit:
        if name and email:
            # Store data in Firebase
            doc_ref = db.collection('feedback').document()
            doc_ref.set({
                'name': name,
                'email': email,
                'Most useful feature' : Selected_feature,
                'overall' : overall,
                'user_interface' : user_interface,
                'recommendations' : recommendations
            })
            st.success("Thank you for your feedback!")
        else:
            st.error("Please fill out all fields")
