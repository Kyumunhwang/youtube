import os
import sys
import shutil
from typing import Dict, Any, List, Callable, Optional
import yt_dlp
import static_ffmpeg
import static_ffmpeg.run

# Add static FFmpeg binaries to environment PATH
static_ffmpeg.add_paths()


def get_system_downloads_folder() -> str:
    """
    Resolves the actual user Downloads directory on Windows via registry/known folders,
    falling back to standard home directory / Downloads.
    """
    if sys.platform == "win32":
        try:
            import winreg
            sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                downloads_guid = "{374DE290-123F-4565-9164-39C4925E467B}"
                try:
                    path, _ = winreg.QueryValueEx(key, downloads_guid)
                    expanded = os.path.expandvars(path)
                    if os.path.exists(expanded):
                        return expanded
                except FileNotFoundError:
                    pass
        except Exception:
            pass

    default_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    if os.path.exists(default_dir):
        return default_dir
    return os.getcwd()


def find_node_executable() -> Optional[str]:
    """
    Finds the Node.js executable on the system to resolve YouTube's JavaScript challenges.
    """
    node_path = shutil.which("node")
    if node_path and os.path.exists(node_path):
        return node_path

    # Common Windows installation locations
    candidate_paths = [
        r"C:\Program Files\nodejs\node.exe",
        r"C:\Program Files (x86)\nodejs\node.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\node\node.exe"),
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            return p
    return None


class YouTubeDownloader:
    """
    Core service to interface with yt-dlp for extracting YouTube video information
    and downloading video/audio directly to the user's local Downloads directory.
    Uses JS challenge solving (EJS) to prevent HTTP 403 Forbidden errors.
    """

    def __init__(self) -> None:
        self.download_dir: str = get_system_downloads_folder()

        # Get FFmpeg binary directory dynamically
        try:
            ffmpeg_exe, _ = static_ffmpeg.run.get_or_fetch_platform_executables_else_raise()
            self.ffmpeg_dir = os.path.dirname(ffmpeg_exe)
        except Exception:
            self.ffmpeg_dir = None

        # Resolve Node.js path for EJS challenge solving
        self.node_path = find_node_executable()

    def _get_base_ydl_opts(self) -> Dict[str, Any]:
        """
        Builds the baseline yt-dlp options configured with JS challenge solver
        and FFmpeg location to prevent HTTP 403 Forbidden and signature errors.
        """
        opts: Dict[str, Any] = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'noplaylist': True,
            'windowsfilenames': True,
            'remote_components': {'ejs:github': {}},
        }

        # Configure JS runtimes for YouTube challenge solving
        if self.node_path:
            opts['js_runtimes'] = {'node': {'path': self.node_path}}
        else:
            opts['js_runtimes'] = {'node': {}, 'deno': {}}

        if self.ffmpeg_dir:
            opts['ffmpeg_location'] = self.ffmpeg_dir

        return opts

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Extracts video metadata and unique available vertical resolutions (heights).

        Args:
            url: The YouTube video URL.

        Returns:
            Dict containing title, thumbnail, duration (seconds), author, and list of available heights.
        """
        ydl_opts = self._get_base_ydl_opts()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError("Failed to extract video information from the provided URL.")

            # Filter unique video heights (resolutions)
            formats: List[Dict[str, Any]] = info.get("formats", [])
            heights = set()
            for f in formats:
                h = f.get("height")
                if f.get("vcodec") != "none" and h and isinstance(h, int):
                    heights.add(h)

            sorted_heights = sorted(list(heights), reverse=True)

            return {
                "title": info.get("title", "Unknown Title"),
                "thumbnail": info.get("thumbnail", ""),
                "duration": int(info.get("duration") or 0),
                "author": info.get("uploader") or info.get("channel") or "Unknown Uploader",
                "heights": sorted_heights
            }

    def _create_progress_hook(self, callback: Callable[[float, str], None]) -> Callable[[Dict[str, Any]], None]:
        """
        Creates a progress hook callback for yt-dlp to update UI dynamically.
        """
        def hook(d: Dict[str, Any]) -> None:
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                filename = os.path.basename(d.get('filename', 'file'))

                if total > 0:
                    percent = min(max(downloaded / total, 0.0), 1.0)
                    callback(percent, f"Downloading: {percent:.1%} ({filename})")
                else:
                    mb = downloaded / (1024 * 1024)
                    callback(0.0, f"Downloading: {mb:.2f} MB...")
            elif d['status'] == 'finished':
                callback(1.0, "Download finished. Merging and post-processing streams...")
        return hook

    def download_video(
        self,
        url: str,
        height: int,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """
        Downloads a video with the selected height and merges with the best available audio stream.

        Args:
            url: The YouTube video URL.
            height: The target vertical resolution (e.g. 1080, 720).
            progress_callback: Optional function called with (progress_fraction, status_text).

        Returns:
            The absolute path of the downloaded file.
        """
        os.makedirs(self.download_dir, exist_ok=True)
        outtmpl = os.path.join(self.download_dir, f"%(title)s [{height}p].%(ext)s")

        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'format': f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best",
            'format_sort': ['vcodec:h264', 'acodec:aac'],
            'outtmpl': outtmpl,
            'merge_output_format': 'mp4',
        })

        if progress_callback:
            ydl_opts['progress_hooks'] = [self._create_progress_hook(progress_callback)]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise RuntimeError("Failed to download video stream.")

            # Check requested_downloads for exact filepath
            if 'requested_downloads' in info and info['requested_downloads']:
                target = info['requested_downloads'][0].get('filepath')
                if target and os.path.exists(target):
                    return os.path.abspath(target)

            # Fallback path resolution
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            candidate_mp4 = f"{base}.mp4"
            if os.path.exists(candidate_mp4):
                return os.path.abspath(candidate_mp4)
            if os.path.exists(filename):
                return os.path.abspath(filename)

            return os.path.abspath(candidate_mp4)

    def download_audio(
        self,
        url: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """
        Downloads the best audio stream and converts it to MP3 (192kbps).

        Args:
            url: The YouTube video URL.
            progress_callback: Optional function called with (progress_fraction, status_text).

        Returns:
            The absolute path of the downloaded MP3 file.
        """
        os.makedirs(self.download_dir, exist_ok=True)
        outtmpl = os.path.join(self.download_dir, "%(title)s.%(ext)s")

        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })

        if progress_callback:
            ydl_opts['progress_hooks'] = [self._create_progress_hook(progress_callback)]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise RuntimeError("Failed to download audio stream.")

            if 'requested_downloads' in info and info['requested_downloads']:
                target = info['requested_downloads'][0].get('filepath')
                if target and os.path.exists(target):
                    return os.path.abspath(target)

            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            candidate_mp3 = f"{base}.mp3"
            if os.path.exists(candidate_mp3):
                return os.path.abspath(candidate_mp3)
            if os.path.exists(filename):
                return os.path.abspath(filename)

            return os.path.abspath(candidate_mp3)
