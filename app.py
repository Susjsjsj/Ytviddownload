from flask import Flask, request, jsonify, render_template_string
import yt_dlp

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YT Video Downloader</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
        }

        .container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }

        input[type="text"] {
            width: 80%;
            padding: 12px;
            margin: 1rem 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }

        button {
            background: #ff4757;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }

        button:hover {
            background: #ff6b81;
        }

        .formats {
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Download YouTube Videos</h1>
        <p>Paste your YouTube link below:</p>
        <input type="text" id="url" placeholder="https://youtube.com/watch?v=...">
        <button onclick="fetchVideoInfo()">Download</button>
        <div class="formats" id="formats"></div>
    </div>

    <script>
        async function fetchVideoInfo() {
            const url = document.getElementById('url').value;
            if (!url) return alert('Please enter a URL');

            try {
                const response = await fetch('/get-info', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });
                const data = await response.json();
                if (data.error) {
                    alert("Error: " + data.error);
                    return;
                }
                displayFormats(data.formats);
            } catch (err) {
                alert('Error fetching video info');
            }
        }

        function displayFormats(formats) {
            const formatsDiv = document.getElementById('formats');
            formatsDiv.innerHTML = formats.map(format => `
                <button onclick="window.open('${format.url}', '_blank')">
                    ${format.resolution} (${format.ext})
                </button>
            `).join('');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/get-info', methods=['POST'])
def get_info():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL required"}), 400

    ydl_opts = {'format': 'best', 'quiet': True, 'no_warnings': True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = [{
                'url': f['url'],
                'resolution': f.get('format_note', 'N/A'),
                'ext': f['ext']
            } for f in info['formats'] if f.get('url')]
            return jsonify({"formats": formats})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
