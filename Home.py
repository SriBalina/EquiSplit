import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="VoyageHub",
    page_icon='🌎',
)

st.title('VoyageHub - Your Trip Partner')
image = Image.open('images/img.jpeg')
st.image(image, width=900)
# Displaying simple markdown
st.markdown("<h2>Navigate to :</h2>", unsafe_allow_html=True)
st.markdown("<h5>Weather - To forecast the weather of your desired place</h5>", unsafe_allow_html=True)
st.markdown("<h5>Chat - When you confused about places to visit or to explore things that friends can do in a trip</h5>", unsafe_allow_html=True)
st.markdown("<h5>Split - To split your bills</h5>", unsafe_allow_html=True)
