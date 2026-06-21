import os
from typing import Dict, Any, List, Callable, Optional
import yt_dlp
import static_ffmpeg
import static_ffmpeg.run

# Add static FFmpeg binaries to environment PATH
static_ffmpeg.add_paths()

class YouTubeDownloader:
    """
    Core service to interface with yt-dlp for extracting YouTube video information
    and downloading video/audio directly to the user's local Downloads directory.
    """

    def __init__(self) -> None:
        # Determine Windows default Downloads directory
        self.download_dir: str = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(self.download_dir):
            # Fallback to current working directory if Downloads directory not found
            self.download_dir = os.getcwd()

        # Get FFmpeg binary directory dynamically
        try:
            ffmpeg_exe, _ = static_ffmpeg.run.get_or_fetch_platform_executables_else_raise()
            self.ffmpeg_dir = os.path.dirname(ffmpeg_exe)
        except Exception:
            self.ffmpeg_dir = None

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Extracts video metadata and unique available resolutions.

        Args:
            url: The YouTube video URL.

        Returns:
            Dict containing title, thumbnail, duration (seconds), and list of available heights.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'js_runtimes': {'deno': {}, 'node': {}},
            'remote_components': {'ejs:github'},
        }
        if self.ffmpeg_dir:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_dir
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError("Failed to extract video information.")

            # Filter unique video heights (resolutions)
            formats: List[Dict[str, Any]] = info.get("formats", [])
            heights = set()
            for f in formats:
                # Include formats that contain video stream (vcodec != 'none') and have a height
                if f.get("vcodec") != "none" and f.get("height"):
                    heights.add(f["height"])

            # Sort heights in descending order (e.g., 2160, 1080, 720...)
            sorted_heights = sorted(list(heights), reverse=True)

            return {
                "title": info.get("title", "Unknown Title"),
                "thumbnail": info.get("thumbnail", ""),
                "duration": info.get("duration", 0),
                "author": info.get("uploader", "Unknown Uploader"),
                "heights": sorted_heights
            }

    def _create_progress_hook(self, callback: Callable[[float, str], None]) -> Callable[[Dict[str, Any]], None]:
        """
        Creates a progress hook callback for yt-dlp.
        """
        def hook(d: Dict[str, Any]) -> None:
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                filename = os.path.basename(d.get('filename', 'file'))
                
                if total > 0:
                    percent = downloaded / total
                    callback(percent, f"Downloading: {percent:.1%} ({filename})")
                else:
                    callback(0.0, f"Downloading: {downloaded / (1024 * 1024):.2f} MB...")
            elif d['status'] == 'finished':
                callback(1.0, "Download completed. Processing and merging streams...")
        return hook

    def download_video(
        self, 
        url: str, 
        height: int, 
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """
        Downloads a video with the selected height and merges with best audio.

        Args:
            url: The YouTube video URL.
            height: The target vertical resolution (e.g., 1080).
            progress_callback: Optional function called with (progress_fraction, status_text).

        Returns:
            The absolute path of the downloaded file.
        """
        # Ensure output directory exists
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Build output template: Downloads/Title [heightp].ext
        outtmpl = os.path.join(self.download_dir, f"%(title)s [{height}p].%(ext)s")

        ydl_opts: Dict[str, Any] = {
            # Select best video of exact or lower height, and best audio, then merge them
            'format': f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
            'format_sort': ['vcodec:h264', 'acodec:aac'],
            'outtmpl': outtmpl,
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'js_runtimes': {'deno': {}, 'node': {}},
            'remote_components': {'ejs:github'},
        }
        if self.ffmpeg_dir:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_dir

        if progress_callback:
            ydl_opts['progress_hooks'] = [self._create_progress_hook(progress_callback)]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Since merge_output_format is set to mp4, change extension if necessary
            base, _ = os.path.splitext(filename)
            final_filename = f"{base}.mp4"
            if not os.path.exists(final_filename) and os.path.exists(filename):
                final_filename = filename
            return os.path.abspath(final_filename)

    def download_audio(
        self, 
        url: str, 
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """
        Downloads the best audio stream and converts it to MP3.

        Args:
            url: The YouTube video URL.
            progress_callback: Optional function called with (progress_fraction, status_text).

        Returns:
            The absolute path of the downloaded MP3 file.
        """
        os.makedirs(self.download_dir, exist_ok=True)
        outtmpl = os.path.join(self.download_dir, "%(title)s.%(ext)s")

        ydl_opts: Dict[str, Any] = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'quiet': True,
            'no_warnings': True,
            'js_runtimes': {'deno': {}, 'node': {}},
            'remote_components': {'ejs:github'},
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        if self.ffmpeg_dir:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_dir

        if progress_callback:
            ydl_opts['progress_hooks'] = [self._create_progress_hook(progress_callback)]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info with download=True runs the download and postprocessors
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # The postprocessor converts output extension to mp3
            base, _ = os.path.splitext(filename)
            final_filename = f"{base}.mp3"
            return os.path.abspath(final_filename)
