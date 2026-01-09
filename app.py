import os
import random
from flask import Flask, send_from_directory, request, Response
import song_processor

# Configuration
SONGBOOK_DIR = r"C:\git\songbook\output\dan_songbook\dan_songbook_split"
CHALLENGES_FILE = "challenges.txt"

app = Flask(__name__, static_folder=SONGBOOK_DIR)

# Load challenges
challenges = []
if os.path.exists(CHALLENGES_FILE):
    with open(CHALLENGES_FILE, 'r', encoding='utf-8') as f:
        challenges = [line.strip() for line in f if line.strip()]
else:
    print("Warning: challenges.txt not found. Run generate_challenges.py first.")
    challenges = ["Play all chords as triads"] # Fallback

@app.route('/')
def index():
    return send_from_directory(SONGBOOK_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    file_path = os.path.join(SONGBOOK_DIR, filename)
    
    if not os.path.exists(file_path):
        return "File not found", 404
        
    # If it's a song file (s_*.html), process it
    if filename.startswith('s_') and filename.endswith('.html'):
        # Pick a random challenge
        challenge = random.choice(challenges)
        print(f"Serving {filename} with challenge: {challenge}")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Process
        # We try/except to ensure we at least serve the original if something fails
        try:
            processed_content = song_processor.process_song(content, challenge)
            
            # Inject a header showing the challenge
            header_html = f"""
            <div style="background-color: #ffffe0; border: 2px solid #e6db55; padding: 10px; margin: 10px; font-family: sans-serif;">
                <strong>Chord Challenge:</strong> {challenge}
            </div>
            """
            # Inject after <body>
            processed_content = processed_content.replace('<body>', '<body>' + header_html)
            
            return processed_content
        except Exception as e:
            print(f"Error processing song: {e}")
            return content # Fallback to original
            
    # Otherwise serve as static file
    return send_from_directory(SONGBOOK_DIR, filename)

if __name__ == '__main__':
    print(f"Serving songbook from {SONGBOOK_DIR}")
    print(f"Loaded {len(challenges)} challenges")
    app.run(debug=True, port=5000)
