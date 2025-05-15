# Anita CMS 🎀

*"Amiya, Aina, and Asta walk into a codebase..."*

![Anita](https://github.com/user-attachments/assets/988871b4-9726-46e5-a72b-ebe551ad70f3)


**ANITA CMS** is the lovechild of three powerful projects - combining Amiya's simplicity, Aina's AI website generation, and Asta's markdown superpowers into one delightful CMS. No bloated frameworks, no Node.js nonsense - just pure vanilla JS magic with a FastAPI backend and SQLite database.

## ✨ Key Features

### Hybrid Content System
- **Markdown Mode**: Full Asta-powered editor with AI assistance
- **HTML Mode**: Aina's static site generator built right in
- **Toggle freely** between content types

### AI Everywhere
- ✍️ AI text generation in markdown
- 🎨 AI website generator
- 🔄 Right-click rewrite anything

### Zero Bloat Architecture
- 🚫 No Node.js required
- 🍦 Vanilla JS/CSS frontend
- 🐍 FastAPI + SQLite backend
- ⚡ Ultra-fast response times


### Admin Panel
- 🏗️ Create/delete sites with one click
- 🏷️ Tag system for organization (blog, portfolio, etc.)
- 🔄 Quick-switch between projects


## 🚀 Installation

### Manual Setup
```bash
# Create and activate virtual environment
python -m uv venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies
uv pip install -r requirements.txt

# Run!
python main.py
```

### Windows Easy Mode
1. Download `anita_installer.bat` from [Releases](https://github.com/your-repo/releases)
2. Double-click to:
   - Create virtual environment
   - Install dependencies
   - Add desktop shortcut
3. Click the shiny new ANITA icon!

## 🎮 Usage

1. Access admin panel at `/admin`
2. Create new pages as either:
   - **Markdown** (with Asta editor)
   - **HTML** (with Aina generator)
3. Toggle between editors as needed
4. Let the AI help when stuck
5. Publish with one click

## 🧩 Tech Stack

| Component       | Technology          |
|-----------------|---------------------|
| Backend         | FastAPI + SQLite    |
| Frontend        | Vanilla JS          |
| Markdown        | Asta Editor         |
| HTML Generator  | Aina System         |
| AI              | OpenAI API          |


## 🌈 Why ANITA?

### For The Underpaid Heroes
- **$20 Website Warriors**: When clients pay in exposure bucks but demand production quality
- **Interns Needing Wins**: Quick portfolio pieces that don't look like Geocities throwbacks
- **0.5 Developer Teams**: Full-time responsibilities, half-time budget, zero-time patience for bloat

### For The Vanilla Purists
- **Node.js Allergy Sufferers**: Who break out in hives at `npm install`
- **"Just Give Me Plain JS"** Crowd: Who want modern features without framework lock-in
- **Build-Your-Own-Adventure** Devs: Tiny core you can extend without fighting someone else's abstractions

### For The Time-Pressed
- **"Need It Yesterday"** Clients: Who think "simple blog" means "launch in 20 minutes"
- **Landing Page Mercenaries**: Who get paid per conversion, not per hour spent configuring
- **"Make It Pop"** Designers: Who want AI-generated wow factor without touching DevTools

### Secret Bonus
- **Codebase Smaller Than**:
  - Your average `node_modules` folder
  - A single React component's dependency tree  
  - The CSS for most "lightweight" frameworks
- **Hackable Core**: The opposite of "magic" frameworks - you can actually understand AND modify everything


## 🗺️ Roadmap & Help Wanted

### 🔐 Security & Multi-User (Urgent!)
- [ ] **Config Panel** (HOW DID WE MISS THIS?!)
- [ ] Authentication system
- [ ] User roles/permissions
- [ ] Session management
- [ ] Audit logging

### ✨ AI-Powered Site Creator (Dream Mode)
- [ ] Sitemap schema generator ("It'll work, trust me")
- [ ] AI layout suggestions
- [ ] Content-first scaffolding
- [ ] "Make it pop" button (for clients who say that)

### 🎨 Customization Galore
- [ ] Theme builder
- [ ] Component playground
- [ ] CSS variable editor
- [ ] "Blog-ify" mode (for when you need that Medium clout)

### 🐛 Bug Hunting Party
- [ ] Stability improvements
- [ ] Edge case testing
- [ ] "That's not a bug, it's a feature" documentation
- [ ] Performance profiling

### 🤗 Emotional Support Needed
```text
   ╭───────────────────────────╮
   │                           │
   │   HUGS ACCEPTED HERE →    │
   │         (.づ◡﹏◡)づ.       │
   │                           │
   ╰───────────────────────────╯
```
**Contribute by:**
- Opening issues (even just to say hi)
- Submitting PRs (or funny memes)
- Starring the repo (serotonin boost)
- Telling the dev "you got this" (lies help)

*"Roadmap subject to change based on caffeine levels and existential dread"*

## ⚠️ Warning: Work in Progress

This project is currently in active development and **lacks critical security features**:
- No built-in authentication system
- No user management capabilities  
- No role-based access control
- No production-ready security measures

**DO NOT USE IN PRODUCTION ENVIRONMENTS** without implementing proper security controls. The current version is intended for local development and testing purposes only.


## 📜 License

AGPL-3.0 - Because open source should stay open!

---

*"Disclaimer: Yes, page.db accidentally saved in the repo, will delete later"*
