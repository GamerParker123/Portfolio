from flask import Flask, render_template, abort, request, send_file
import os
import markdown
import re
import io
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

# project data stored in a dictionary
PROJECTS = {
    "simulation": {
        "title": "Unity Simulation Prototype",
        "emoji": "🧠",
        "description": "An exploratory project with Hatsune Miku that focuses on user-entity interaction. This paved all future projects. NOTE: All assets are free models I downloaded from Sketchfab.",
        "tech": ["C#", "Unity"],
        "size": "beginning",
        "screenshots": [
            { "src": "/static/images/simulation1.png", "alt": "Miku can be interacted with to open a chatbot menu" },
            { "src": "/static/images/simulation2.png", "alt": "The chatbot menu" },
            { "src": "/static/images/simulation3.png", "alt": "A panned shot of the entire room" },
            { "src": "/static/images/simulation4.png", "alt": "The user can pick up a leek and give it to Miku" },
            { "src": "/static/images/simulation5.png", "alt": "The user can interact with the TV to play songs" },
            { "src": "/static/images/simulation6.png", "alt": "The song selection menu" }
        ],
        "details": {
        "motivation": "I wanted to bring Hatsune Miku to life in a simulated world. I also aimed to learn more about general software development, as this was my first major independent computer science project.",
        "about": "This Unity simulation focuses on basic user-AI interaction. The user moves freely in a room and is able to experiment with different parts. For example, clicking Miku will play an animation where she's pushed over, and her chatbot model will generate a response based on the action. Unfortunately, I don't update this project anymore because I don't have access to a VR cable to connect my computer to my headset. DISCLAIMER: In my attempt to convert to VR, I broke the keyboard controls, so I can't show a full demonstration of the project. To compensate, I've taken screenshots of key features (see below).",
        "lessons": "I gained lots of experience with Unity and C#, which are tools I'd never used before. AI integration was particularly tricky, as the messages weren't being parsed correctly. I ended up needing to parse manually, which wasn't ideal, but it got the job done. Finally, while this project is temporarily discontinued, it's arguably my most important, as it inspired me to create everything else in this portfolio."
        }
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
    fact_img = None

    # === Handle FOD Generator ===
    if key == "fact-of-the-day" and request.method == "POST":
        import requests, io, base64, random, datetime, os
        from PIL import Image, ImageDraw, ImageFont

        IMAGE_FOLDER = os.path.join("static", "fod_images")  # put your images here
        FONT_PATH = os.path.join("static", "fonts", "Anton-Regular.ttf")

        def get_random_fact():
            url = "https://uselessfacts.jsph.pl/random.json?language=en"
            try:
                r = requests.get(url, timeout=5)
                r.raise_for_status()
                return r.json()["text"].replace("`", "'")
            except:
                return "Fun Fact: Whales are cool."

        def wrap_text(text, font, max_width):
            lines, line = [], ""
            for word in text.split():
                test = line + word + " "
                if font.getlength(test) <= max_width:
                    line = test
                else:
                    lines.append(line.strip())
                    line = word + " "
            lines.append(line.strip())
            return lines

        # === Get valid fact with rerolls ===
        max_words = 40
        reroll_limit = 10
        rerolls = 0
        fact = get_random_fact()

        while rerolls < reroll_limit:
            word_count = len(fact.split())
            if word_count > max_words:
                fact = get_random_fact()
                rerolls += 1
                continue
            break
        else:
            fact = "Fun Fact: Whales are cool."

        # === Canvas ===
        W, H = 960, 540
        img = Image.new(
            "RGB",
            (W, H),
            (random.randint(0, 150), random.randint(0, 150), random.randint(0, 150))
        )
        draw = ImageDraw.Draw(img)

        # === Random image ===
        images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if images:
            img_path = os.path.join(IMAGE_FOLDER, random.choice(images))
            fg_img = Image.open(img_path).convert("RGBA")
            fg_img.thumbnail((400, 400))
        else:
            fg_img = None

        # === Randomly choose layout side ===
        image_on_left = datetime.date.today().day % 2 == 1

        # === Title ===
        title_font = ImageFont.truetype(FONT_PATH, 52)
        date_str = datetime.date.today().strftime("%m/%d/%y")
        title_text = f"FOD {date_str}:"
        title_width = title_font.getlength(title_text)
        title_height = title_font.getbbox(title_text)[3] - title_font.getbbox(title_text)[1]

        # === Auto-scale fact font ===
        max_fact_height = int(H * 0.6)
        font_size = 46
        while font_size > 20:
            test_font = ImageFont.truetype(FONT_PATH, font_size)
            lines = wrap_text(fact, test_font, 400)
            total_height = len(lines) * (test_font.getbbox("A")[3] - test_font.getbbox("A")[1] + 8)
            if total_height <= max_fact_height:
                fact_font = test_font
                break
            font_size -= 2
        else:
            fact_font = ImageFont.truetype(FONT_PATH, 24)

        # === Place image ===
        if fg_img:
            img_x = 50 if image_on_left else W - fg_img.width - 50
            img_y = (H - fg_img.height) // 2
            img.paste(fg_img, (img_x, img_y), fg_img)
        text_x = W - 450 if image_on_left else 50  # opposite side of image

        # === Draw title ===
        draw.text((text_x, 50), title_text, font=title_font, fill="white")
        draw.line((text_x, 50 + title_height + 15, text_x + title_width, 50 + title_height + 15),
                fill="white", width=4)

        # === Draw fact ===
        lines = wrap_text(fact, fact_font, 400)
        line_height = fact_font.getbbox("A")[3] - fact_font.getbbox("A")[1] + 8
        total_height = len(lines) * line_height
        start_y = (H - total_height) // 2 + 20
        for i, line in enumerate(lines):
            draw.text((text_x, start_y + i * line_height), line, font=fact_font, fill="white")

        # === Convert to base64 ===
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        fact_img = base64.b64encode(buf.read()).decode("utf-8")

    # === Handle Hapax Analyzer ===
    if key == "hapax-analyzer" and request.method == "POST":
        import re, io, base64
        from collections import Counter
        import matplotlib.pyplot as plt

        file = request.files["file"]
        text = file.read().decode("utf-8").lower()
        words = re.findall(r'\b\w+\b', text)
        seen_counts = Counter()
        hapax_rates = []

        for i, word in enumerate(words):
            seen_counts[word] += 1
            hapaxes = sum(1 for c in seen_counts.values() if c == 1)
            hapax_rates.append(hapaxes / (i + 1))

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

        hapax_img = base64.b64encode(img.read()).decode('utf-8')

    # ✅ Unified return
    return render_template(
        "project.html",
        project=project,
        title=project["title"],
        fact_img=fact_img,
        hapax_img=hapax_img,
        key=key
    )

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEVLOGS_FOLDER = os.path.join(BASE_DIR, 'devlogs_md')

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
