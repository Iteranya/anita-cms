<div align="center">
  <img src="https://github.com/user-attachments/assets/dced49c6-87ce-42d3-b83d-d6a1fa751393" alt="Anita" width="557" height="557" style="border: 2px solid #f0f0f0; border-radius: 8px; padding: 5px;" />
</div>

# 🌸 Anita CMS

**Your Creative Partner for the Web.**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red.svg)](https://www.sqlalchemy.org/)

Anita is a lightweight, self-hosted Content Management System (CMS) designed to give you total creative freedom without the monthly subscriptions or technical headaches. It combines the speed of modern web frameworks with a team of embedded AI assistants to help you build, write, and design.

---

## 🌟 Why Anita?

*   **Own Your Data:** No vendor lock-in. No hidden fees. Your website runs on your machine or your server.
*   **AI-Native:** Built from the ground up to work with LLMs (like ChatGPT, Claude, or local models) to handle the heavy lifting.
*   **Hybrid Engine:** Seamlessly mix standard blogging with completely custom-coded pages.

---

## 🏗️ Technical Architecture

Anita is built for simplicity in development and robustness in production.

### 🗄️ Database & ORM
Anita is powered by **SQLAlchemy**, the industry-standard ORM for Python.
*   **Zero-Config Start:** By default, Anita runs on **SQLite**. The entire database is a single file (`anita.db`). You can copy, backup, or move your website just by copying this file.
*   **PostgreSQL Ready:** Need to scale? Because Anita is built on SQLAlchemy, switching to **PostgreSQL** (or MySQL) is as simple as changing a single connection string in your `.env` file. No code changes required.

### ⚡ Service-Oriented Backend
Under the hood, Anita is a modular **FastAPI** application. It uses a clean service-layer architecture (Controllers → Services → Data Access), ensuring the codebase is easy to maintain and extend if you are a developer.

---

## 📄 The Hybrid Content Engine

Most CMSs force you to choose: *Are you a blog using a rigid theme? Or are you a static site hand-coding HTML?*

**Anita lets you be both.** Every page can be toggled between two modes:

### 1. Markdown Mode (For Writers)
Perfect for blog posts, documentation, and articles.
*   Write in simple Markdown.
*   **Template Injection:** Anita wraps your Markdown in a "Master Template" (which is itself an editable page in the system).
*   **Customize the Render:** You can edit the code of the `blog-template` page to instantly change the layout, fonts, and style of *all* your Markdown pages at once.

### 2. HTML Mode (For Designers)
Perfect for Landing Pages, Homepages, and Interactive Art.
*   The page serves **raw HTML** directly from the database.
*   No constraints. Import GSAP, Three.js, or Tailwind CDN directly.
*   Aina (the AI Architect) can write this code for you, giving you bespoke layouts that standard CMS themes can't match.

---

## 🤖 Meet Your AI Team

Anita isn't just a tool; it's a studio. You have two dedicated AI specialists ready to help:

### 🖋️ Asta: The Editor
Asta is your **Markdown & Content Assistant**.

<img width="1917" height="906" alt="Screenshot 2025-11-18 192317" src="https://github.com/user-attachments/assets/b6ba65fd-51d4-40c9-981a-5e8c2ad92a55" />

*   **Context Aware:** Asta helps you draft blog posts and documentation.
*   **Smart Editing:** Ask Asta to "fix the tone," "expand this section," or "summarize this for a meta description."

### 🎨 Aina: The Architect
Aina is your **Site Builder & Designer**.

<img width="1919" height="906" alt="Screenshot 2025-11-21 152132" src="https://github.com/user-attachments/assets/a457de07-a322-4102-9060-ea439a541856" />

*   **Route Aware:** Aina understands your website's structure (pages, forms, assets).
*   **Code Generation:** Describe the page you want, and Aina generates the HTML/CSS structure for you.
*   **Integration:** Aina knows how to fetch data from your custom Forms to build dynamic layouts.

---

## 🛠️ The Power Feature: Dynamic Forms

Anita treats "Forms" as more than just a way to collect emails. **Forms are your No-Code Backend.**

When you create a Form in Anita, you are instantly creating a database schema and an API endpoint. This allows you to build complex data structures without writing a single line of Python or SQL.

**What can you build?**
*   **☕ Cafe Menu:** Create a form with `dish_name`, `price`, and `photo`.
*   **🎨 Portfolio:** Create a form with `project_title`, `client`, and `gallery_images`.
*   **📅 Events:** Create a form with `date`, `location`, and `rsvp_link`.

Once your form is created, **Aina** can access this data to generate dynamic galleries, lists, and tables automatically.

---

## 🚀 Installation

### Windows (One-Click)
1.  Download the `anita_installer.bat` file from the Release Page
2.  Double-click to install.
3.  Launch via the desktop shortcut.

### Mac / Linux / Manual Setup
We recommend using `uv` for lightning-fast dependency management.

```bash
# 1. Clone the repository
git clone https://github.com/iteranya/anita-cms.git
cd anita-cms

# 2. Create virtual environment
python -m uv venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# 3. Install dependencies
uv pip install -r requirements.txt

# 4. Configuration
cp example.env .env
# Edit .env to add your JWT_SECRET

# 5. Run the server
python main.py
```

Once running, access your dashboard at:
`http://127.0.0.1:8000/admin`

---

## 🤝 Contributing

Anita is open-source software. We welcome contributions!
*   **Frontend:** HTML/JS/CSS (located in `static/`).
*   **Backend:** Python/FastAPI (located in `routes/`, `services/`, and `data/`).

Please feel free to open issues or submit Pull Requests.

---

## 📄 License

Anita CMS is licensed under **AGPL-3.0**.
*   **Free to use.**
*   **Free to modify.**
*   **Open source forever.**
