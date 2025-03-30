import streamlit as st

def render_footer():
    """Render the footer with attribution."""
    st.markdown("---")
    st.markdown(
        """
        <div class="footer">
            <p>© 2025 Nevada GDE Water Needs Explorer. A collaboration between The Nature Conservancy, 
            University of Nevada, and the Bureau of Reclamation.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )