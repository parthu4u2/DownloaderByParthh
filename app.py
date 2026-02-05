from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

from flask import Flask, after_this_request, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

YOUTUBE_PATTERN = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$", re.IGNORECASE
)
INSTAGRAM_PATTERN = re.compile(
    r"^(https?://)?(www\.)?instagram\.com/.+$", re.IGNORECASE
)


def _validate_url(platform: str, url: str) -> bool:
    if platform == "youtube":
        return bool(YOUTUBE_PATTERN.match(url))
    if platform == "instagram":
        return bool(INSTAGRAM_PATTERN.match(url))
    return False


def _download_media(url: str) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="media_dl_"))
    output_template = str(temp_dir / "%(title).120B.%(ext)s")

    ydl_opts = {
        "format": "bv*+ba/b",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = Path(ydl.prepare_filename(info))

        if file_path.suffix.lower() != ".mp4":
            mp4_candidate = file_path.with_suffix(".mp4")
            if mp4_candidate.exists():
                file_path = mp4_candidate

    if not file_path.exists():
        candidates = sorted(temp_dir.glob("*"), key=lambda p: p.stat().st_size, reverse=True)
        if not candidates:
            raise FileNotFoundError("Downloaded file not found")
        file_path = candidates[0]

    return file_path


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    platform = request.form.get("platform", "").strip().lower()
    url = request.form.get("url", "").strip()

    if not url or not platform:
        return render_template("index.html", error="Please choose a platform and enter a URL.")

    if not _validate_url(platform, url):
        return render_template(
            "index.html",
            error="The URL does not match the selected platform.",
            chosen_platform=platform,
            entered_url=url,
        )

    try:
        media_path = _download_media(url)
    except Exception as exc:  # noqa: BLE001
        return render_template(
            "index.html",
            error=f"Unable to download this media: {exc}",
            chosen_platform=platform,
            entered_url=url,
        )

    @after_this_request
    def cleanup(response):
        try:
            media_dir = media_path.parent
            if media_path.exists():
                media_path.unlink(missing_ok=True)
            if media_dir.exists():
                os.rmdir(media_dir)
        except OSError:
            pass
        return response

    return send_file(
        media_path,
        as_attachment=True,
        download_name=media_path.name,
        mimetype="video/mp4",
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
