import streamlit as st

st.header("Settings")
st.write("---")
st.write(f"Welcome to the settings page : {st.session_state.user.username}")
st.write(f"You are logged in as {st.session_state.user.role}.")
st.write("Here you can change your settings.")
st.write("---")
