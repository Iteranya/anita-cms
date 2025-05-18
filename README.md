# Anita CMS 🎀

*"Amiya, Aina, and Asta walk into a codebase..."*

<div align="center">
  <!-- This creates a simple border effect around the image -->
  <img src="https://github.com/user-attachments/assets/988871b4-9726-46e5-a72b-ebe551ad70f3" alt="Anita" width="450" style="border: 2px solid #f0f0f0; border-radius: 8px; padding: 5px;" />
</div>


**ANITA CMS** is the lovechild of three powerful projects - combining Amiya's simplicity, Aina's AI website generation, and Asta's markdown superpowers into one delightful CMS. No bloated frameworks, no Node.js nonsense - just pure vanilla JS magic with a FastAPI backend and SQLite database.


## ✨ Core Features Showcase

### Visual Component Overview
<div align="center">
  <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-bottom: 30px;">
    <div style="flex: 1; min-width: 300px;">
      <img src="https://github.com/user-attachments/assets/cb007f35-16d5-4360-9738-228bc27998b7" alt="Asta Markdown Editor" style="border: 1px solid #e1e4e8; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);"/>
      <p style="text-align: center; margin-top: 8px; color: #666;"><strong>Asta Markdown Editor</strong><br>AI-assisted writing with full markdown support</p>
    </div>
    <div style="flex: 1; min-width: 300px;">
      <img src="https://github.com/user-attachments/assets/9680ad2b-78de-47b8-9c51-09309aa8e51e" alt="Aina Website Generator" style="border: 1px solid #e1e4e8; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);"/>
      <p style="text-align: center; margin-top: 8px; color: #666;"><strong>Aina Website Generator</strong><br>Visual HTML builder with AI layout suggestions</p>
    </div>
    <div style="flex: 1; min-width: 300px;">
      <img src="https://github.com/user-attachments/assets/e74c76fc-653b-47ce-9c6b-3ac1cdec3411" alt="Amiya Admin Panel" style="border: 1px solid #e1e4e8; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);"/>
      <p style="text-align: center; margin-top: 8px; color: #666;"><strong>Amiya Admin Panel</strong><br>Centralized control for all your projects</p>
    </div>
  </div>
</div>

### Hybrid Content Management System

Our dual-mode editor gives you the best of both worlds:

- **Markdown Mode (Asta Editor)**  
  Perfect for content-focused sites like blogs and documentation. Features include:
  - Real-time preview with syntax highlighting
  - AI-powered writing assistance

- **HTML Mode (Aina Generator)**  
  Ideal for visually-rich pages with:
  - Real-time website generation
  - AI-generated sites
  - Edit and ask follow ups on the fly

*Switch between markdown and html to be rendered on display!*

### Intelligent AI Integration

We've baked AI into every workflow without vendor lock-in:

- **Content Creation**  
  ✍️ Generate draft text in markdown with tone/style controls  
  🎨 Get entire sites ready for AI Generation
  🔄 Context-aware rewriting (select text → right-click → improve)

- **Flexible Backend**  
  🔌 Connect to OpenAI, Anthropic, or self-hosted models  
  💾 Local AI model support (via OpenAI Library)

### Lightweight Yet Powerful Architecture

Built for developers who value performance and simplicity:

- **Frontend**  
  🍦 Pure vanilla JS (no framework bloat)  
  🎨 CSS variables for easy theming  

- **Backend**  
  🐍 FastAPI for rapid request handling  
  🗃️ SQLite for portable data storage  
  ⚡ Average response time <50ms  

### Project Management Made Simple

The admin panel helps you stay organized:

- **Site Management**  
  🏗️ One-click project creation  
  🗑️ Bulk delete for spring cleaning  
  🏷️ Tag-based filtering (e.g., #blog, #portfolio)  


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
1. Download `anita_installer.bat` from [Releases](https://github.com/Iteranya/anita-cms/releases)
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
| AI              | OpenAI Library      |


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
- [x] Authentication system
- [x] User roles/permissions (admin only for now)
- [x] Session management
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

## ⚠️ Warning: Regarding Security

This project is currently in active development and **only has basic security feature**:
- Cookie Based Security
- No user management capabilities  
- No role-based access control
- Single user authentication only

## 📜 License

AGPL-3.0 - Because open source should stay open!
