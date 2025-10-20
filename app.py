from flask import Flask, render_template, abort, request, send_file
import os
import markdown
import re
import io
from collections import Counter
import matplotlib
matplotlib.use("Agg")  # Non-GUI backend for server
import matplotlib.pyplot as plt

app = Flask(__name__)

# project data stored in a dictionary
PROJECTS = {
    "simulation": {
        "title": "Unity Simulation Prototype",
        "emoji": "🧠",
        "description": "An exploratory project with Hatsune Miku that focuses on user-entity interaction. This paved all future projects.",
        "tech": ["C#", "Unity"],
        "size": "beginning",
    },
    "chatbot": {
        "title": "Immersive Chatbot",
        "emoji": "💬",
        "description": "An AI LLM that uses multiple layers of memory and temporal messaging to feel like a living companion.",
        "tech": ["Python", "OpenAI API", "JSON", "ChromaDB"],
        "size": "big",
        "links": {
            "GitHub": "Coming soon"
        }
    },
    "video-site": {
        "title": "ParkerVerse: The Gamified Social Media",
        "emoji": "📺",
        "description": "A social media site mixed with a video game: ephemeral video storage, individual focus trees, user communities, and more...",
        "tech": ["Python", "Supabase", "Flask"],
        "size": "big",
        "links": {
            "Site link (very slow)": "https://parkerhub.onrender.com/",
            "Discord development server": "https://discord.gg/ggcvmBEdBB"
        }
    },
    "secret-santa": {
        "title": "Secret Santa Probability Calculator",
        "emoji": "🎁",
        "description": "A software that generates the probability of being paired with any given person in Secret Santa.",
        "tech": ["Python", "NumPy", "Matplotlib"],
        "size": "small",
        "links": {
            "GitHub": "https://github.com/GamerParker123/Secret-Santa-Probability-Tracker"
        }
    },
    "fact-of-the-day": {
        "title": "\"Fact of the Day\" (FOD) Generator",
        "emoji": "📆",
        "description": "An automatic slideshow generator that generates a fun fact every day.",
        "tech": ["Python", "Pillow"],
        "size": "small",
        "links": {
            "GitHub": "https://github.com/GamerParker123/FOD-Maker"
        }
    },
    "hapax-analyzer": {
        "title": "Hapax Analyzer",
        "emoji": "📝",
        "description": "Scans a text file for hapax legomena (unique words) and displays their rate throughout the file by generating a line graph. I made this project because I was interested in what the hapax rate would look like over the course of a text.",
        "tech": ["Python", "Matplotlib"],
        "size": "small",
        "links": {
            "GitHub": "https://github.com/GamerParker123/Hapax-Analyzer"
        }
    },
    "ai-programming-assistant": {
        "title": "AI Programming Assistant",
        "emoji": "🤖",
        "description": "An application that uses embedded search and chunking to edit relevant files in your codebase.",
        "tech": ["Python", "Tkinter", "difflib", "OpenAI API", "ChromaDB"],
        "size": "medium",
        "links": {
            "GitHub": "Coming soon"
        }
    },
    "spotify-nicheness-analyzer": {
        "title": "Spotify Nicheness Analyzer",
        "emoji": "🎧",
        "description": "Determines how \"niche\" your Spotify playlists are in a user-friendly, shareable format.",
        "tech": ["Python", "Flask", "Base64", "SQLite", "Requests", "aiohttp"],
        "size": "medium",
        "links": {
            "GitHub": "https://github.com/GamerParker123/MusicNichenessRater"
        }
    },
    "smart-mp3-player": {
        "title": "Smart MP3 Player",
        "emoji": "🎵",
        "description": "Uses specialized weighting to shuffle playlists and features audio normalization.",
        "tech": ["Python", "Tkinter", "Mutagen", "VLC", "Pillow"],
        "size": "medium",
        "links": {
            "GitHub": "https://github.com/GamerParker123/smart-mp3-player"
        }
    },
    "productivity-timer": {
        "title": "Productivity Timer",
        "emoji": "⏱️",
        "description": "A Pomodoro-style timer that graphs your desktop activity and lets you block apps during work time.",
        "tech": ["Python", "Tkinter", "Matplotlib"],
        "size": "medium",
        "links": {
            "GitHub": "https://github.com/GamerParker123/Productivity-Timer"
        }
    },
    "spreadsheet-filler": {
        "title": "Spreadsheet Filler",
        "emoji": "📊",
        "description": "Fills out spreadsheets using an LLM given a set of parameters.",
        "tech": ["Python", "OpenAI API", "Tkinter"],
        "size": "small",
        "links": {
            "GitHub": "Coming soon"
        }
    },
    "text-scrambler": {
        "title": "Text Scrambler",
        "emoji": "🔀",
        "description": "Generates every possible iteration of the characters in a word (or the words in a sentence).",
        "tech": ["Python", "Tkinter"],
        "size": "small",
        "links": {
            "GitHub": "https://github.com/GamerParker123/Text-Scrambler"
        }
    },
}

@app.context_processor
def inject_projects():
    return dict(projects=PROJECTS)

@app.route('/')
def index():
    return render_template('index.html', title="The KonnerVerse")

@app.route('/project/<key>', methods=["GET", "POST"])
def project(key):
    project = PROJECTS.get(key)
    if not project:
        abort(404)

    hapax_img = None

    # Only handle file uploads for the Hapax Analyzer project
    if key == "hapax-analyzer" and request.method == "POST":
        file = request.files["file"]
        text = file.read().decode("utf-8").lower()

        words = re.findall(r'\b\w+\b', text)
        seen_counts = Counter()
        hapax_rates = []

        for i, word in enumerate(words):
            seen_counts[word] += 1
            hapaxes = sum(1 for count in seen_counts.values() if count == 1)
            hapax_rate = hapaxes / (i + 1)
            hapax_rates.append(hapax_rate)

        # Generate plot to a BytesIO object
        plt.figure(figsize=(14, 6))
        plt.plot(hapax_rates, color='blue', linewidth=1)
        plt.title("Hapax Legomena Rate Over Text Progression")
        plt.xlabel("Word Index")
        plt.ylabel("Hapax Rate")
        plt.grid(True)
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)
        plt.close()

        # Convert to base64 string so we can embed in HTML
        import base64
        hapax_img = base64.b64encode(img.read()).decode('utf-8')

    return render_template(
        "project.html",
        project=project,
        title=project["title"],
        hapax_img=hapax_img,
        key=key
    )

DEVLOGS_FOLDER = "devlogs_md"

def load_devlogs():
    devlogs = []
    for filename in sorted(os.listdir(DEVLOGS_FOLDER)):
        if filename.endswith(".md"):
            filepath = os.path.join(DEVLOGS_FOLDER, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract header metadata
            header_match = re.match(r"---\n(.*?)\n---\n(.*)", content, re.DOTALL)
            if header_match:
                header_text, body_md = header_match.groups()
                metadata = {}
                for line in header_text.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
                devlogs.append({
                    "id": int(filename.replace(".md", "")),
                    "title": metadata.get("title", "Untitled"),
                    "date": metadata.get("date", ""),
                    "summary": metadata.get("summary", ""),
                    "content": markdown.markdown(body_md)
                })
    return sorted(devlogs, key=lambda d: d["id"])  # sort by ID

@app.route('/devlogs')
def devlogs():
    devlogs_list = load_devlogs()
    return render_template("devlogs.html", title="Journal Devlogs", devlogs=devlogs_list)

@app.route('/devlogs/<int:devlog_id>')
def devlog(devlog_id):
    devlogs_list = load_devlogs()
    devlog_entry = next((d for d in devlogs_list if d["id"] == devlog_id), None)
    if not devlog_entry:
        abort(404)
    return render_template("devlog_entry.html", title=devlog_entry["title"], devlog=devlog_entry)

if __name__ == '__main__':
    app.run(debug=True)
