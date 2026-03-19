import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# ১. সার্ভার স্ট্যাটাস চেক
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# ২. ইউটিউব সার্চ (কিউয়ার্ড দিয়ে)
@app.route('/api/search', methods=['GET'])
def search_videos():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    ydl_opts = {'format': 'best', 'quiet': True, 'extract_flat': True, 'force_generic_extractor': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch20:{query}", download=False)
            videos = []
            for entry in search_results.get('entries', []):
                videos.append({
                    "id": entry.get('id'),
                    "title": entry.get('title'),
                    "thumbnail": entry.get('thumbnails')[0]['url'] if entry.get('thumbnails') else None,
                    "duration": entry.get('duration'),
                    "url": f"https://www.youtube.com/watch?v={entry.get('id')}"
                })
            return jsonify(videos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ৩. ভিডিও তথ্য সংগ্রহ (লিঙ্ক দিয়ে)
@app.route('/api/fetch-info', methods=['GET'])
def fetch_info():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {'format': 'best', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('url'):
                    formats.append({
                        "quality": f.get('format_note') or f.get('resolution'),
                        "ext": f.get('ext'),
                        "url": f.get('url'),
                        "filesize": f.get('filesize')
                    })
            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "formats": formats
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
