import os
import sys
import streamlit as st
in_cloud = os.environ.get('STREAMLIT_SHARING', '') == '1' or os.environ.get('IS_STREAMLIT_CLOUD', '') == '1'
if not in_cloud:
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        has_audio_devices = True
    except:
        has_audio_devices = False
        in_cloud = True
st.sidebar.markdown("## Environment Info")
if in_cloud:
    st.sidebar.warning("⚠️ Running in cloud environment - audio recording is simulated")
else:
    st.sidebar.success("✅ Running in local environment - full functionality available")
if in_cloud:
    import sounddevice_patch
import app
if __name__ == "__main__":
    app.main()