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
    "chatbot": {
        "title": "Immersive Chatbot",
        "emoji": "💬",
        "description": "An AI LLM that uses multiple layers of memory and temporal messaging to feel like a living companion.",
        "tech": ["Python", "OpenAI API", "JSON", "ChromaDB", "Hugging Face"],
        "size": "big",
        "links": {
            "GitHub (public version w/ sensitive info removed)": "https://github.com/GamerParker123/Immersive-Chatbot-Public"
        },
        "videos": [
            {
                "src": "/static/videos/mikuchatbotdemo.mp4",
                "title": "Quick demonstration of the chatbot's main features"
            }
        ],
        "screenshots": [
            { "src": "/static/images/chatbot1.png", "alt": "The user talks to Hatsune Miku in a texting-like format" },
            { "src": "/static/images/chatbot2.png", "alt": "The chat bot stores contextual memory, including future plans" },
            { "src": "/static/images/chatbot3.png", "alt": "The user prompts Miku more plans" },
            { "src": "/static/images/chatbot4.png", "alt": "The contextual memory is updated with the new plans" },
            { "src": "/static/images/chatbot5.png", "alt": "Miku will send up to 3 responses if the user doesn't respond back" },
            { "src": "/static/images/chatbot6.png", "alt": "Recurring events are dynamically stored in memory" },
            { "src": "/static/images/chatbot7.png", "alt": "Each memory is given a \"strength\" depending on message similarity, recency, and repetition (if a user says something about oranges, Miku will remember other references of oranges)" },
            { "src": "/static/images/chatbot8.png", "alt": "Miku is assigned an automatically generated personality document based on her traits, and this updates daily (traits slowly drift based on her emotions)" },
        ],
        "details": {
        "motivation": "This project has two primary motivations. First, it's an extension to my Unity simulation prototype (see my motivation for that in its respective section). Half of the battle is making Miku act like, well, Miku, and that requires a powerful AI model. The second motivation came from a limitation I saw with modern chat bots. Current LLMs are pretty good at generating responses given some conversation data, but they don't know how to collect that data effectively. This means you can't grow with an AI like you can another person. Current language models won't remember old experiences with you or relevant facts. Solving that problem has been the core of this project.",
        "about": "This is a chat bot with the personality of Hatsune Miku. However, the LLM layer is a very small piece; it uses OpenAI's API. The bulk of the effort is put toward memory allocation. I've divided memory into a few crucial categories: recent, strong, contextual, episodic, and wildcard. Recent memories are what you'd expect - just the most recent messages in the conversation. Strong memories are a bit more complex. They use embedded search to map word vectors and match similar messages. They also factor emotion; messages with a similar emotion to the message sent will be stronger. Emotions are calculated using j-hartmann's Emotion English DistilRoBERTa-base model from Hugging Face, and they're divided into seven types (anger, disgust, fear, joy, neutral, sadness, surprise). Strength is also weighted by message recency, so more recent messages are slightly stronger. After all of this is calculated, the model takes the strongest messages relative to whatever the user sent and adds them to the prompt. The next type of memory, contextual memory, describes anything going on at the given moment. It includes time, mood, the current activity, recurring events (like anniversaries), locations, and plans. To generate mood, current activity, and plans, a helper LLM is used. This fixes a big issue with current chat bots, which is that they get sidetracked in long conversations. With my system, you're able to say, \"I want to go to the movies\" and \"I want to get ice cream,\" and the AI isn't going to forget either of those plans until they're completed. Next, episodic memory is message summaries. To help the AI remember general ideas without overfilling the context window, summaries of old conversations are generated and insertered. It uses a hierarchical model where a summary is generated for every 10 messages. Once you have 10 of these 10-message summaries, it generates a summary based off of those, and so on. This reflects how humans think: they get the gist of past events, even if they don't remember the specifics. Finally, wildcard memories are just randomly selected memories, slightly weighted for recency. This is used to generate inspiration and add more unexpectedness to responses. Outside of memory, this project has one more key differentiator: temporal messaging. The AI knows how much time has passed between messages, and it'll send another response if the user hasn't spoken in a while. In actual conversations, not every comment gets the same amount of weight. Sometimes you get a small interjection or no comment at all, and temporal messaging brings this aspect to AI. If the user's response is absent, the AI is prompted to either expand or switch topics. Most chat bots are assistants that only respond when spoken to. Mine pokes you every so often.",
        "lessons": "I dabbled in LLMs for the Unity prototype but nothing this advanced. I've had to learn how to quantify written text. Thankfully, a lot of this has been done for me, like current language models, but a lot of my memory system was designed from scratch. One big lesson was learning how semantic search works. This is how search engines like Google operate (although I'm sure they're more sophisticated), and it's pretty simple. You take a set of words, assign a vector to them based on tons of data, and calculate the distance between those vectors. The elegance of these systems has been surprising. In general, a big piece of the puzzle has been thinking about how people work. Whenever I test my chat bot and think, \"this feels off,\" I try to figure out why. That's what inspired me to implement the temporal messaging system. Current chat bots put too much pressure on the user to continue the conversation. I wanted to lower that barrier, so I thought about real conversations. And in real conversations, people don't talk back-and-forth perfectly. It's filled with silences, appended comments, and interjections. I've learned not only how to make a functional AI, but also how humans work (well, a little)."
        }
    },
    "video-site": {
        "title": "ParkerVerse: The Gamified Social Media",
        "emoji": "📺",
        "description": "A social media site mixed with a video game: ephemeral video storage, individual focus trees, user communities, and more...",
        "tech": ["Python", "Supabase", "Flask"],
        "size": "big",
        "links": {
            "GitHub (public version w/ sensitive info removed)": "https://github.com/GamerParker123/ParkerVersePublic",
            "Site link (WORKING VERSION OF THE SITE)": "https://parkerhub.onrender.com/",
            "Discord development server": "https://discord.gg/ggcvmBEdBB"
        },
        "videos": [
            {
                "src": "/static/videos/parkerversedemo.mp4",
                "title": "Quick demonstration of ParkerVerse's main features"
            }
        ],
        "screenshots": [
            { "src": "/static/images/parkerverse1.png", "alt": "The home page (in flame theme - unlocked in the focus tree) + note for all ParkerVerse screenshots: none of the videos depicted are my intellectual property; they're uploaded by site users" },
            { "src": "/static/images/parkerverse2.png", "alt": "The \"Hall of Fame\" page (in dark theme)" },
            { "src": "/static/images/parkerverse3.png", "alt": "An example of a video page (in aqua theme - unlocked in the focus tree)" },
            { "src": "/static/images/parkerverse4.png", "alt": "An example of a profile page (everything is in aqua theme after this)" },
            { "src": "/static/images/parkerverse5.png", "alt": "The focus tree page" },
            { "src": "/static/images/parkerverse6.png", "alt": "The video upload page" }
        ],
        "details": {
        "motivation": "For the past few years that I've been using YouTube, I've noticed more and more ads showing up on my videos. Apparently, they show you more ads if you tolerate them more. When this dawned on me, I was pretty angry. So for fun, I started working on a basic website you could upload videos to. I did that in an evening, and that's when I realized I could make something tangible. I wanted to make a video site that didn't use predatory monetization tactics like most platforms. Part of this came out of principle, but I also saw that many others were upset with the corporatization of social platforms. Despite that, no platform seemed to escape the grasp of corporations. I wanted to change that. However, I soon realized that I couldn't simply make YouTube 2.0. People are creatures of habit, and you need something uniquely attractive to convince them to use another service. That's when I had one of my favorite revelations: I don't need to design this like a social media platform. Inspired by Snapchat and Wordle's daily retention strategies, I chose to design the site like a game. Users would have streaks to encourage daily activity, and there would be a focus tree where they can unlock new features. I saw an untapped part of social media, and I wanted to experiment with it. That's the long answer to why I created ParkerVerse. (I could go much longer, trust me xD)",
        "about": "ParkerVerse is a site that incentivizes to upload and interact with others as much as you can. Multiple systems are in place to boost user activity. First, users have streaks. One is for visiting the site daily, and another is for uploading weekly. These are basic ways to encourage users to use the platform frequently. The main draw is the focus tree, which is where users spend currency (earned by being active - pretty much anything you could think of earns currency) to unlock new features. The user gets to choose what they want to unlock, and the tree is divided into a few distinct paths. One path is for profile customization, which includes things like profile pictures and banners. Another is for developer benefits, such as video tags and higher upload limits. The third is for quality of life additions, like new themes, and the fourth is for purely fun features (i.e., cursor trails, secret minigames, etc.). By giving the social media format a concrete sense of progression, engagement can be greatly increased. Another method of engaging users is through connections. Because everyone is incentivized to interact with each other, almost every post gets some form of engagement. When you get even a couple comments on a video, you feel validated. This naturally extends into the site's community system, where users can join topic-based public communities or private communities with friends. These communities have their own focus trees that grow with activity, further encouraging users to share videos. The final major site attractor is its ephemeral storage. Videos are deleted after one day, except for the most voted video of the day (which is sent to a permanent \"Hall of Fame\" to be viewed by others). Again, this gives people a reason to check the site frequently. It has the nice side effect of drastically reducing storage costs. All in all, ParkerVerse aims to make the internet a little more fun and connected than it was before.",
        "lessons": "When it comes to raw coding, this has been one of the easier projects to develop. Web development and video sharing aren't as technically difficult to implement as other things. Personally, the lessons learned with ParkerVerse stem from scalability. There have been multiple times where I've thought the site might be doomed. I've learned to pivot when that happens. Initially, I essentially wanted to make YouTube with greater customization and less ads. However, I realized that data storage is expensive; this is what convinced me to make storage ephemeral. Next, I realized my site wasn't \"sticky\" - even if it was functionally sound, users didn't have a reason to return. That's when I took on a game design perspective. The latest issue has been bandwidth, which I've battled by implementing strong video compression. ParkerVerse has taught me how to optimize for profit and usability."
        }
    },
    "simulation": {
        "title": "Unity Simulation Prototype",
        "emoji": "🧠",
        "description": "An exploratory project with Hatsune Miku that focuses on user-entity interaction. This paved all future projects. NOTE: All assets are free models I downloaded from Sketchfab.",
        "tech": ["C#", "Unity", "OpenAI API"],
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
    "ai-programming-assistant": {
        "title": "AI Programming Assistant",
        "emoji": "🤖",
        "description": "An application that uses embedded search and chunking to edit relevant files in your codebase.",
        "tech": ["Python", "Tkinter", "difflib", "OpenAI API", "ChromaDB"],
        "size": "medium",
        "links": {
            "GitHub (public version w/ sensitive info removed)": "https://github.com/GamerParker123/AICodeAssistantPublic"
        },
        "screenshots": [
            { "src": "/static/images/aiprogrammingassistant1.png", "alt": "The user submits a prompt, the AI selects a relevant file and code chunks, and it displays the changes" }
        ],
        "details": {
        "motivation": ".",
        "about": ".",
        "lessons": "."
        }
    },
    "spotify-nicheness-analyzer": {
        "title": "Spotify Nicheness Analyzer",
        "emoji": "🎧",
        "description": "Determines how \"niche\" your Spotify playlists are in a user-friendly, shareable format.",
        "tech": ["Python", "Flask", "Base64", "SQLite", "Requests", "aiohttp"],
        "size": "medium",
        "links": {
            "GitHub (public version w/ sensitive info removed)": "https://github.com/GamerParker123/MusicNichenessRaterPublic"
        },
        "screenshots": [
            { "src": "/static/images/nichenessanalyzer1.png", "alt": "The submission page of the analyzer" },
            { "src": "/static/images/nichenessanalyzer2.png", "alt": "Playlist selection" },
            { "src": "/static/images/nichenessanalyzer3.png", "alt": "The results page, showing your \"nicheness\" score and a few other visuals" },
        ],
        "details": {
        "motivation": "I wanted to design a public-facing project optimized for virality. People cling strongly to individuality, so I thought it would be fun to design a tool where they could see how \"unique\" your song tastes are and be able to share it with others.",
        "about": "This tool uses Spotify to authorize users and collect playlist data. Once the user inputs some playlists, they're able to calculate a \"nicheness score\" that displays how unique their playlist is. They're encouraged to share their results on social media. Unfortunately, due to Spotify's developer limitations, I'm unable to make the project public (which kind of defeats the virality point, haha). However, all the code is available in the GitHub link, and screenshots are pasted below.",
        "lessons": "This was the first tool I designed specifically for shareability, and it taught me how to make poppy displays using CSS and JS. It was unlike anything I'd made before, as it's one of the first things I didn't design for my own needs."
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
        },
        "screenshots": [
            { "src": "/static/images/smartmp3player1.png", "alt": "The player displays the current song, artist, and cover art - additionally, the user can add songs/playlists and like/dislike songs. There is also a button to skip, and you can change the volume or go to a different timestamp in the song" }
        ],
        "details": {
        "motivation": ".",
        "about": ".",
        "lessons": "."
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
        },
        "screenshots": [
            { "src": "/static/images/productivitytimer1.png", "alt": "Visible is the current phase (work/break) and the status. You're also able to see how much time is left until the next phase and how much \"overtime\" you have (time spent working past your limit). Below, there's a pie chart displaying how much time you've spent in each phase and the number of cycles completed for the day/week. There's also a graph below that displays your top five most used applications and how much you used them per hour. In the bottom, right, you can pause/unpause and continue to the next phase when the current one is complete. Alternatively, you can enable \"auto phase changes\" and have phases change automatically." },
            { "src": "/static/images/productivitytimer2.png", "alt": "Below the graph stuff, you can set your work and break durations (default is 52 minutes of work / 17 minutes of break). You can also add/remove apps to block during your work period." }
        ],
        "details": {
        "motivation": ".",
        "about": ".",
        "lessons": "."
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
    #"spreadsheet-filler": {
    #    "title": "Spreadsheet Filler",
    #    "emoji": "📊",
    #    "description": "Fills out spreadsheets using an LLM given a set of parameters.",
    #    "tech": ["Python", "OpenAI API", "Tkinter"],
    #    "size": "small",
    #    "links": {
    #        "GitHub": "Coming soon"
    #    }
    #},
    #"text-scrambler": {
    #    "title": "Text Scrambler",
    #    "emoji": "🔀",
    #    "description": "Generates every possible iteration of the characters in a word (or the words in a sentence).",
    #    "tech": ["Python", "Tkinter"],
    #    "size": "small",
    #    "links": {
    #        "GitHub": "https://github.com/GamerParker123/Text-Scrambler"
    #    }
    #},
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

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        IMAGE_FOLDER = os.path.join(BASE_DIR, 'static', 'fod_images')
        FONT_PATH = os.path.join(BASE_DIR, "static", "fonts", "Anton-Regular.ttf")

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
