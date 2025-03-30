import streamlit as st
from components.header import render_header
from components.footer import render_footer
from content.definitions import render_definitions

def main():
    st.set_page_config(
        page_title="Nevada GDE Water Needs Explorer - Definitions and Disclaimers",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Add custom Google font
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        """,
        unsafe_allow_html=True
    )
    
    # Load custom CSS
    with open("styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Render header with logos
    render_header()
    
    # Main title and subtitle
    st.markdown("<h1 class='main-title'>Nevada GDE Water Needs Explorer</h1>", unsafe_allow_html=True)
    
    render_definitions()
    
    # Close container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
