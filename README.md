# 🌸 Anita CMS

*"Amiya, Aina, and Asta walk into a codebase..."*

<div align="center">
  <img src="https://github.com/user-attachments/assets/f3ab4ac9-853b-4be9-be92-560f0948caaf" alt="Anita" width="557" height="557" style="border: 2px solid #f0f0f0; border-radius: 8px; padding: 5px;" />
</div>

**Anita CMS** is a lightweight, AI-assisted, hybrid content management system that combines:

*   **Amiya’s** clean admin power 💼
*   **Aina’s** visual, API-aware web generation 🎨
*   **Asta’s** markdown mastery 🖋️

All running on **FastAPI + SQLite**, with **zero Node.js dependency** and pure **vanilla JS** magic.
*(Yes, it’s actually fast. Like, under-50ms fast.)*

---

## 🌟 What’s Inside Anita?

### 🏰 Admin Panel (Amiya)

Manage everything from one cozy dashboard:

*   View, edit, and delete pages
*   Build and manage custom forms
*   Access form submissions and export to CSV
*   Configure AI, mail, and global site settings
*   Tag any page as your **Home, Blog, Contact, or any other custom page** — no IDE required!

---

### 📝 Pages (Asta & Aina)

Hybrid content management that adapts to your needs. Create, design, and publish everything without ever touching the backend code.

*   **Markdown Mode (Asta Editor)**
    *   Perfect for blogs, documentation, and content-rich articles.
    *   Real-time preview and syntax highlighting.
    *   AI-assisted writing to draft, rewrite, and refine your text.

*   **HTML Mode (Aina Generator)**
    *   An AI powerhouse for visual creation. Aina is fully aware of your site's backend routes and APIs.
    *   **API-Aware Generation**: Tell Aina to create a blog homepage, and she'll generate the HTML and JavaScript needed to fetch and display posts from the correct API endpoint. The same goes for blog templates or any custom page interacting with the backend.
    *   **Form Attachment**: Need a contact form you just built in the admin panel? Aina can seamlessly "attach" and render it on any page, already wired up to the forms API.
    *   **Total Visual Control**: Generate entire landing pages, "About Us" sections, or a unique `/best_cat` page, all through conversational prompts.

*Switch freely between Markdown and HTML — no reloads, no fuss.*

---

### 🧠 AI Integration (Aina + Asta)

Anita bakes AI right into your workflow, with full **OpenAI compatibility** (and others via config):

*   **Aina Builds**: Generate complex, API-driven pages like a blog home or post templates. She understands your site's structure and can create interactive experiences.
*   **Asta Writes**: Generate articles, expand on ideas, or change the tone of your content with a simple command.
*   **Context-Aware Editing**: Highlight text and ask the AI to "rewrite," "expand," or "make it funnier."
*   **Local Model Support**: Configure a local AI model for maximum privacy and control.
*   **Fine-Tune Your AI**: Select your provider, temperature, tone, and creativity levels to match your brand's voice.

> Aina builds the house, interacting with the foundation (API). Asta writes the story inside. Anita approves. 💅

---

### 💌 Mail System (via Resend)

A modern CMS needs a reliable way to communicate.

*   Simplified mail configuration under **Admin → Config → Mail**.
*   Built on Resend for high deliverability and ease of use.
*   Power your contact forms, user notifications, and more without complex setups.

---

### 🧾 Forms (NEW!)

Anita's form-building capabilities are now a core feature.

*   Build **custom forms** with various field types directly from the admin panel.
*   Aina can intelligently insert your forms into the websites she generates.
*   View all submissions in one place or **export them as a CSV** for use in other tools.
*   Perfect for contact pages, surveys, lead capture, or user feedback.

---

### 🔐 Security

Simple, robust, and secure by default.

*   **JWT + Cookies + Admin authentication** ensures your management panel is protected.
*   A straightforward, single-role system for simplicity.
*   Secure defaults are baked in, so you can focus on creating.

---

## 🏷️ Important Tags

Anita uses tags to assign special roles to pages, unlocking automatic routing and functionality.

### **`home`**

The chosen one. The page with this tag becomes your site’s landing page at `/`.

### **`blog`**

Pages with this tag are automatically listed on your blog homepage.

### **`blog-home`**

Marks a page as the main blog listing, served at `/blog`.

### **`blog-template`**

The layout for individual blog posts, rendered at `/blog/{slug}`. Aina can generate a design for this that correctly fetches and displays post content.

### **`main`**

Any page with this tag gets served at `/{slug}`. Ideal for standalone pages like `/about`, `/projects`, or `/pricing`.

---

## ⚙️ Tech Stack

| Component | Technology |
| :--- | :--- |
| Backend | FastAPI + SQLite |
| Frontend | Vanilla JS |
| Markdown Editor | Asta Editor |
| HTML Generator | Aina System |
| AI Layer | OpenAI-compatible |
| Mail Service | Resend |

---

## 🚀 Quick Start

### 🧩 Manual Setup

```bash
# Create and activate virtual environment
python -m uv venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies
uv pip install -r requirements.txt

# Configure environment
cp example.env .env
# Open .env and update JWT_SECRET with a secure random string
# You can generate one with: python -c "import secrets; print(secrets.token_hex(32))"

# Run the app
python main.py
```

### 💻 Windows Easy Mode

1.  Download `anita_installer.bat` from [Releases](https://github.com/Iteranya/anita-cms/releases).
2.  Double-click to:
    *   Create a virtual environment
    *   Install dependencies
    *   Add a desktop shortcut
3.  Click the shiny new ANITA icon ✨.

---

## 🎮 Usage

1.  Visit `/admin`.
2.  Create pages using Markdown or let Aina generate them with HTML.
3.  Add forms or AI-assisted sections as needed.
4.  Tag your homepage, blog pages, and other main pages.
5.  Publish and brag about building a fully functional, API-driven site in under an hour.

---

## 💡 Why Choose Anita?

### For the **Practical Dreamers**

*   Build dynamic websites and blogs without writing a single line of backend code.
*   Let Aina handle the API interactions while you focus on the vision.
*   Stay lightweight, fast, and completely understandable.

### For the **Overworked and Underpaid**

*   Create stunning, interactive client sites at lightning speed.
*   One-click publishing and editing from a simple admin panel.
*   "It just works" — even when the deadline is tomorrow.

### For the **Vanilla JS Enjoyers**

*   No `node_modules/` nightmares.
*   Clean, easily themeable CSS variables.
*   A truly hackable and transparent core.

## But I Need Custom Features!!

### I'm All About Abstraction~

*  Use Aina-chan integrated form api to create a dashboard to edit cafe menu
*  Make another form API to create a beautiful art portfolio
*  Make a custom form API to create an event planner

### How to?

*  Demo coming up soon!
*  Check out Artes Paradox's channel for tutorials, coming up!
---

## 🗺️ Roadmap

### ✨ Upcoming Features

*   [ ] Full AI-powered site scaffolding
*   [ ] Sitemap & SEO auto-generation
*   [ ] Theme builder + component playground
*   [ ] “Blog-ify” mode for instant writing platforms
*   [ ] Improved role management

### 🐞 Always Improving

*   [ ] Stability fixes & bug bounties (emotional or caffeine-based)
*   [ ] Performance tuning
*   [ ] “That’s not a bug, it’s a feature” mode

---

## 🤗 Support & Contribution

```text
   ╭───────────────────────────╮
   │   HUGS ACCEPTED HERE →    │
   │        (.づ◡﹏◡)づ.        │
   ╰───────────────────────────╯
```

**Ways to help:**

*   Open issues (even just to say hi 👋)
*   Submit PRs (or cursed memes)
*   Star the repo (for serotonin)
*   Tell Anita she’s doing great (she thrives on validation)

---

## 📜 License

**AGPL-3.0** — because open source should stay open 💖
