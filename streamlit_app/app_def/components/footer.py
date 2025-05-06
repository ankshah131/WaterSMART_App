import streamlit as st

def render_footer():
    """Render the footer with attribution."""
    st.markdown("---")
    st.markdown(
        """
        <div class="footer">
            <p>© Nevada GDE Water Needs Explorer. A collaboration between Desert Research Institute, University of Wisconsin, The Nature Conservancy, 
            and the Bureau of Reclamation.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
