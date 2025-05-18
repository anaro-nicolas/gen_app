import streamlit as st
from dataclasses import dataclass
from loguru import logger 

@dataclass
class User:
    username: str = None
    role: str = None
    user_id: int = None

    def __reduce__(self):
        return (self.__class__, (self.username, self.role, self.user_id))
    

class AuthenticationInterface:
    
    def __init__(self):
        self.roles = [None,"ADMIN", "USER"]
    
    def login(self,username:str=None):
        st.header("Log in")
        if 'user' not in st.session_state:
            st.session_state.user = User()
        
        role = st.selectbox("Choose your role", self.roles) 
        if st.button("Log in"):
            logger.debug(f"Role selected: {role}")
            st.session_state.user.role = role
            st.session_state.user.username = "Admin"
            st.session_state.user.user_id = 1
            st.rerun()
            
    def logout(self):
        st.session_state.user.role = None
        st.session_state.user.username = None
        st.session_state.user.user_id = None
        st.rerun()