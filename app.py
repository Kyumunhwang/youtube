import streamlit as st
import os
import subprocess
from downloader import YouTubeDownloader

# Set Streamlit page configuration with a premium icon and title
st.set_page_config(
    page_title="StreamYT Downloader",
    page_icon="📥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Premium Custom CSS for Sleek Dark Theme, Custom Fonts, Gradients, and Glassmorphism
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Global Typography */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif;
        background-color: #0e1117;
        color: #f0f2f6;
    }

    /* Main Title Styling with Gradient */
    .title-text {
        background: linear-gradient(135deg, #ff4b4b, #ff7e40, #ff1e56);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    
    .subtitle-text {
        color: #8a99ad;
        font-size: 1.1rem;
        font-weight: 300;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Glassmorphism Containers */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    /* Input Field Customization */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    div[data-baseweb="input"]:focus-within {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 0 1px #ff4b4b !important;
    }

    /* Premium Styled Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #ff4b4b, #ff7e40) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2) !important;
        width: 100% !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4) !important;
        background: linear-gradient(90deg, #ff3333, #ff6a26) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0px) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if "downloader" not in st.session_state:
    st.session_state.downloader = YouTubeDownloader()
if "video_info" not in st.session_state:
    st.session_state.video_info = None
if "last_url" not in st.session_state:
    st.session_state.last_url = ""
if "last_downloaded_file" not in st.session_state:
    st.session_state.last_downloaded_file = None

# Application Header
st.markdown('<div class="title-text">StreamYT Downloader</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle-text">Target Folder: <code>{st.session_state.downloader.download_dir}</code></div>', unsafe_allow_html=True)

# Main Form Container (Input Section)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

url_input = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

# Handle URL Change / Fetch Metadata
if url_input:
    clean_url = url_input.strip()
    if clean_url != st.session_state.last_url:
        st.session_state.video_info = None
        st.session_state.last_url = clean_url
        st.session_state.last_downloaded_file = None

    if st.session_state.video_info is None:
        with st.spinner("Fetching video information..."):
            try:
                st.session_state.video_info = st.session_state.downloader.get_video_info(clean_url)
            except Exception as e:
                st.error(f"Error fetching metadata: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)

# Display Video Metadata and Download Options
if st.session_state.video_info:
    info = st.session_state.video_info
    
    # 1. Metadata Display Card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col_thumb, col_details = st.columns([2, 3])
    with col_thumb:
        if info.get("thumbnail"):
            # Use container width to support modern Streamlit versions cleanly
            st.image(info["thumbnail"], use_container_width=True)
    with col_details:
        st.markdown(f"### {info.get('title', 'YouTube Video')}")
        st.markdown(f"**Uploader:** {info.get('author', 'Unknown')}")
        
        # Format duration into HH:MM:SS or MM:SS
        duration_sec = info.get('duration', 0)
        hours = duration_sec // 3600
        minutes = (duration_sec % 3600) // 60
        seconds = duration_sec % 60
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"
        st.markdown(f"**Duration:** {duration_str}")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Configuration & Download Card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Download Settings")

    download_type = st.radio("Choose Download Type:", ["Video & Audio", "Audio Only (MP3)"], horizontal=True)

    if download_type == "Video & Audio":
        # Format resolutions for selectbox (e.g. 1080p, 720p)
        available_heights = info.get("heights", [])
        if not available_heights:
            st.warning("No discrete video resolutions extracted. Will download best available format.")
            selected_height = None
        else:
            resolution_options = {h: f"{h}p" for h in available_heights}
            for h in available_heights:
                if h >= 2160:
                    resolution_options[h] = f"{h}p (4K UHD)"
                elif h >= 1440:
                    resolution_options[h] = f"{h}p (2K QHD)"
                elif h >= 1080:
                    resolution_options[h] = f"{h}p (Full HD)"
                elif h >= 720:
                    resolution_options[h] = f"{h}p (HD)"

            selected_height = st.selectbox(
                "Select Resolution:",
                options=available_heights,
                format_func=lambda x: resolution_options.get(x, f"{x}p")
            )
    else:
        selected_height = None

    # Placeholders for progress reports
    progress_container = st.empty()
    status_container = st.empty()

    def update_progress(percent: float, text: str) -> None:
        """Callback to update progress bar and status text dynamically."""
        with progress_container:
            st.progress(percent)
        with status_container:
            st.markdown(f"⚡ **{text}**")

    # Download Trigger Button
    if st.button("Start Download"):
        update_progress(0.0, "Initializing download process...")
        
        try:
            if download_type == "Video & Audio":
                height_val = selected_height if selected_height else 1080
                with st.spinner("Downloading video..."):
                    filepath = st.session_state.downloader.download_video(
                        url=st.session_state.last_url,
                        height=height_val,
                        progress_callback=update_progress
                    )
            else:
                with st.spinner("Downloading audio and converting to MP3..."):
                    filepath = st.session_state.downloader.download_audio(
                        url=st.session_state.last_url,
                        progress_callback=update_progress
                    )

            update_progress(1.0, "Process completed successfully!")
            st.session_state.last_downloaded_file = filepath
            
        except Exception as e:
            st.error(f"An error occurred during download: {str(e)}")

    if st.session_state.last_downloaded_file and os.path.exists(st.session_state.last_downloaded_file):
        downloaded_path = st.session_state.last_downloaded_file
        st.success("🎉 Download completed successfully!")
        st.info(f"**Saved to:** `{downloaded_path}`")
        if st.button("📂 Open in File Explorer"):
            try:
                subprocess.run(["explorer", f"/select,{os.path.normpath(downloaded_path)}"])
            except Exception as exp_err:
                st.warning(f"Could not open explorer automatically: {str(exp_err)}")

    st.markdown('</div>', unsafe_allow_html=True)
