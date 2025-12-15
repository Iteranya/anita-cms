<div align="center">
  <img src="https://github.com/user-attachments/assets/dced49c6-87ce-42d3-b83d-d6a1fa751393" alt="Anita" width="557" height="557" style="border: 2px solid #f0f0f0; border-radius: 8px; padding: 5px;" />
</div>

# 🌸 Anita CMS

**Your Creative Partner for the Web.**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![HTMX](https://img.shields.io/badge/Frontend-HTMX-blue)](https://htmx.org/)
[![Alpine.js](https://img.shields.io/badge/Frontend-Alpine.js-8BC34A)](https://alpinejs.dev/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red.svg)](https://www.sqlalchemy.org/)

Anita is a lightweight, self-hosted Content Management System (CMS) designed to give you total creative freedom without the monthly subscriptions or technical headaches. It combines the speed of modern web frameworks with a team of embedded AI assistants to help you build, write, and design.

---

## 🌟 Why Anita?

*   **Own Your Data:** No vendor lock-in. No hidden fees. Your website runs on your machine or your server.
*   **AI-Native:** Built from the ground up to work with LLMs (like ChatGPT, Claude, or local models) to handle the heavy lifting.
*   **Hybrid Engine:** Seamlessly mix rich Markdown articles with completely custom, interactive HTML pages using simple toggles.
*   **Secure by Default:** With built-in content sanitization, a configurable Content Security Policy (CSP), and attribute-based access, you control your site's security posture.

---

## 🏗️ Technical Architecture

Anita is built for simplicity in development and robustness in production.

### 🐍 Backend
Under the hood, Anita is a modular **FastAPI** application. It uses a clean service-layer architecture (Controllers → Services → Data Access), ensuring the codebase is easy to maintain and extend.

### 🗄️ Database & ORM
Anita is powered by **SQLAlchemy**, the industry-standard ORM for Python.
*   **Zero-Config Start:** By default, Anita runs on **SQLite**. The entire database is a single file (`anita.db`). You can copy, backup, or move your website just by copying this file.
*   **PostgreSQL Ready:** Need to scale? Because Anita is built on SQLAlchemy, switching to **PostgreSQL** (or MySQL) is as simple as changing a single connection string in your `.env` file. No code changes required.

### ⚡ Frontend
The admin dashboard is a snappy, modern interface built with **HTMX** and **Alpine.js**. For your public-facing pages, our custom middleware, **HikarinJS**, provides a safe and structured way for your interactive elements to communicate with the backend.

---

## 📄 The Hybrid Content Engine

Most CMSs force you to choose: *Are you a blog using a rigid theme? Or are you a static site hand-coding HTML?*

**Anita lets you be both, on the same page.** We use a powerful backend tagging system, presented to you as simple switches in the UI.

<img align="right" width="200" src="https://github.com/user-attachments/assets/b6ba65fd-51d4-40c9-981a-5e8c2ad92a55" alt="Asta, the Editor AI" />

#### For Writers (Markdown Mode)
Flip a switch to turn any page into a blog post.
*   Write in simple Markdown. Asta, your AI editor, is right there to help you draft.
*   Click the "Publish" button, and Anita wraps your content in a master `blog-template`.
*   You can edit the `blog-template` page itself to instantly change the layout, fonts, and style of *all* your Markdown pages at once.

#### For Designers (HTML Mode)
Flip another switch for full creative control. Perfect for landing pages and interactive art.
*   The page serves your **HTML, CSS, and JS** directly from the database.
*   **Safe by Default:** All HTML is sanitized using **Bleach** to prevent XSS attacks.
*   **Structured Interactivity:** To add dynamic behavior, Aina (your AI Architect) uses **HikarinJS**, our built-in Javascript module powered by **Alpine.js**. This allows for rich, client-side interactions that communicate safely with the backend.
*   **Full Control (When You Need It):** For advanced users, sanitization can be disabled in the granular security settings.

---

## 🤖 Meet Your AI Team

Anita isn't just a tool; it's a creative studio. You have two dedicated AI specialists ready to help.

### 🖋️ Asta: The Editor
Asta is your **Markdown & Content Assistant**. It lives in the editor, helping you draft blog posts, documentation, and articles with a click. When you're ready, a simple button publishes the page as a blog post.

### 🎨 Aina: The Architect
Aina is your **Site Builder & Designer**. She understands your website's structure and helps you build complex, interactive pages safely.

<img width="1919" height="906" alt="Aina, the Architect AI" src="https://github.com/user-attachments/assets/a457de07-a322-4102-9060-ea439a541856" />

*   **Context Aware:** Using simple dropdowns, you can "inject" context for Aina—tell her which forms, media, or API routes she should use.
*   **Secure Code Generation:** Describe the page you want, and Aina generates **sanitized HTML/CSS** and uses the **HikarinJS API** with **Alpine.js** to create interactivity. She cannot write arbitrary Javascript, keeping your site secure.
*   **Transparent Prompts:** Want to skip the API costs or use your own model? The exact prompt Aina uses is always visible. Just copy, paste, and run it anywhere you like.

---

## 🛡️ Security First

### 🎭 Attribute-Based Access Control (ABAC)
*   **Discord-Flavored Roles:** Anita uses a flexible ABAC system. Instead of a rigid hierarchy, you create roles (e.g., "Editor," "Designer," "Marketer") and assign a combination of specific permissions (attributes) to each.
*   **Granular Permissions:** Assign rights for actions like `page:update`, `forms:read`, `media:create`, and more.
*   **Admin Supremacy:** Only users with the `System Administrator` role can create, modify, or assign roles to other users, ensuring centralized control.

---

## 🛠️ The Power Feature: Dynamic Forms

Anita treats "Forms" as more than just a way to collect emails. **Forms are your No-Code Backend.**

When you create a Form in Anita, you are instantly creating a database schema **and** a corresponding API endpoint. This is no-code wizardry that lets you build complex data structures without writing a single line of Python or SQL.

**What can you build?**
*   **☕ Cafe Menu:** A form with `dish_name`, `price`, and `photo` fields.
*   **🎨 Portfolio:** A form with `project_title`, `client`, and `gallery_images` fields.
*   **📅 Events:** A form with `date`, `location`, and `rsvp_link` fields.

Once created, **Aina** can access the Form's API route to generate dynamic galleries, lists, and tables automatically. Plus, each form has its own granular access controls (e.g., `any:create`, `moderator:read`), which can be configured or overridden by global user roles.

---

## 🚀 Installation

### Windows (One-Click)
1.  Download the `anita_installer.bat` file from the Release Page.
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

# Once running, access your dashboard at:
# http://127.0.0.1:5469/admin
# Follow the on-screen instructions for initial setup.
```
---

## 🤝 Contributing

Anita is open-source software. We welcome contributions!
*   **Frontend:** HTML/JS/CSS (located in `static/`). The stack is primarily **HTMX** and **Alpine.js**.
*   **Backend:** Python/FastAPI (located in `routes/`, `services/`, and `data/`).

Please feel free to open issues or submit Pull Requests.

---

## 📄 License

Anita CMS is licensed under **AGPL-3.0**.
*   **Free to use.**
*   **Free to modify.**
*   **Open source forever.**
