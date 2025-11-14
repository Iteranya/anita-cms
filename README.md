# 🌸 Anita CMS

*"Amiya, Aina, and Asta walk into a codebase..."*

<div align="center">
  <img src="https://github.com/user-attachments/assets/30fd931a-eaa9-4d87-91d8-7e027cd401c9" alt="Anita" width="450" style="border: 2px solid #f0f0f0; border-radius: 8px; padding: 5px;" />
</div>

**Anita CMS** is a lightweight, AI-assisted, hybrid content management system that combines:

* **Amiya’s** clean admin power 💼
* **Aina’s** visual web generation 🎨
* **Asta’s** markdown mastery 🖋️

All running on **FastAPI + SQLite**, with **zero Node.js dependency** and pure **vanilla JS** magic.
*(Yes, it’s actually fast. Like, under-50ms fast.)*

---

## 🌟 What’s Inside Anita?

### 🏰 Admin Panel (Amiya)

Manage everything from one cozy dashboard:

* View, edit, and delete pages
* Access forms and submissions
* Configure AI settings
* Update mail and site settings
* Tag any page as your **Home, Blog, Contact, and more** page — no IDE required!

---

### 📝 Pages (Asta & Aina)

Hybrid content management, your way:

* **Markdown Mode (Asta Editor)**

  * Perfect for blogs and documentation
  * Real-time preview + syntax highlighting
  * AI-assisted writing and rewriting

* **HTML Mode (Aina Generator)**

  * AI-powered website creation
  * Visual builder with layout suggestions
  * One-click “Make it Pop” button for instant client happiness

*Switch freely between Markdown and HTML — no reloads, no fuss.*

---

### 🧠 AI Integration (Aina + Asta)

Anita bakes AI right into your workflow, with full **OpenAI compatibility** (and others via config):

* Generate articles, landing pages, or even entire websites
* Context-aware AI editing (“rewrite,” “expand,” or “make funnier”)
* Local model support for the privacy-conscious devs
* Select your AI provider, temperature, tone, and creativity levels

> Aina builds. Asta writes. Anita approves. 💅

---

### 💌 Mail System (via Resend)

Because a CMS without email is just a glorified text editor.

* Simplified mail configuration under **Admin → Config → Mail**
* Resend-based schema for reliability and ease
* Send notifications, contact forms, and more without third-party chaos

---

### 🧾 Forms (NEW!)

Anita learned a new trick! 🎉

* Build **custom forms** directly from the admin panel
* Aina can now insert those forms on the websites she generates
* View submissions instantly or **export them as CSV**
* Perfect for contact pages, surveys, or capturing lost souls (a.k.a. user feedback)

---

### 🔐 Security

Anita may be cute, but she’s serious about protection.

* **JWT + Cookies + Admin authentication**
* Single-role for simplicity
* Secure defaults baked in — green lights all around 🟢

---

## ⚙️ Tech Stack

| Component       | Technology        |
| --------------- | ----------------- |
| Backend         | FastAPI + SQLite  |
| Frontend        | Vanilla JS        |
| Markdown Editor | Asta Editor       |
| HTML Generator  | Aina System       |
| AI Layer        | OpenAI-compatible |
| Mail Service    | Resend            |

---

## 🚀 Quick Start

### 🧩 Manual Setup

```bash
# Create and activate virtual environment
python -m uv venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies
uv pip install -r requirements.txt

# Run the app
python main.py
```

### 💻 Windows Easy Mode

1. Download `anita_installer.bat` from [Releases](https://github.com/Iteranya/anita-cms/releases)
2. Double-click to:

   * Create virtual environment
   * Install dependencies
   * Add desktop shortcut
3. Click the shiny new ANITA icon ✨

---

## 🎮 Usage

1. Visit `/admin`
2. Create pages (Markdown or HTML)
3. Add forms or AI-assisted sections
4. Tag your homepage and publish
5. Brag about finishing a site in under an hour

---

## 💡 Why Choose Anita?

### For the **Practical Dreamers**

* Build websites and blogs without fighting frameworks
* Toggle between AI and manual writing freely
* Stay lightweight and understandable

### For the **Overworked and Underpaid**

* Create stunning client sites at lightning speed
* One-click publishing and editing
* “It just works” — even at 2 AM before a deadline

### For the **Vanilla JS Enjoyers**

* No `node_modules/` nightmares
* CSS variables for easy theming
* Truly hackable core

---

## 🗺️ Roadmap

### ✨ Upcoming Features

* [ ] Full AI-powered site scaffolding
* [ ] Sitemap & SEO auto-generation
* [ ] Theme builder + component playground
* [ ] “Blog-ify” mode for instant writing platforms
* [ ] Improved role management

### 🐞 Always Improving

* [ ] Stability fixes & bug bounties (emotional or caffeine-based)
* [ ] Performance tuning
* [ ] “That’s not a bug, it’s a feature” mode

---

## 🤗 Support & Contribution

```text
   ╭───────────────────────────╮
   │   HUGS ACCEPTED HERE →    │
   │        (.づ◡﹏◡)づ.        │
   ╰───────────────────────────╯
```

**Ways to help:**

* Open issues (even just to say hi 👋)
* Submit PRs (or cursed memes)
* Star the repo (for serotonin)
* Tell Anita she’s doing great (she thrives on validation)

---

## 📜 License

**AGPL-3.0** — because open source should stay open 💖
