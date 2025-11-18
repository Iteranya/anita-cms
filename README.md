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

Anita isn't just a CMS; it's a creative suite powered by two distinct AI personalities, Asta and Aina, who handle the writing and the building, so you can focus on the vision.

### 🖋️ **Asta: The AI-Powered Markdown Editor**

Asta is your dedicated writing assistant, perfect for crafting content-rich pages like blogs, documentation, or articles. She lives inside a clean, real-time Markdown editor designed to keep you in the flow.

*   **Effortless Content Creation**: Write and publish beautiful Markdown pages with a live preview. Tag your work as a `blog` post or save it as a draft with a single click.
*   **AI-Assisted Writing**: Asta's AI is deeply integrated into the editor to supercharge your writing process:
    *   **Continue Writing**: If you hit a block, simply ask Asta to continue your train of thought, and she'll generate the next paragraph for you.
    *   **Contextual Editing**: Highlight any sentence or paragraph, right-click, and open the "Edit with AI" modal. From there, you can ask the AI to rewrite it, expand on the idea, change the tone, or even make it funnier.
    *   **AI Notes**: A dedicated 'notes' section is always visible to the AI. Use it to provide specific instructions, tone guidelines, or context that Asta should consider while assisting you, ensuring her output is always on-brand.
*   **OpenAI Compatibility**: You're not locked into a single AI provider. Configure Anita to work with OpenAI or any other compatible service, including local models for maximum privacy.

### 🎨 **Aina: The API-Aware AI Website Builder**

Aina is the architect and visual designer of your website. Unlike other AI builders that just fill in templates, Aina is fully aware of your site's backend, routes, and APIs, allowing her to generate pages that are not only beautiful but also fully functional.

*   **True API-Aware Generation**: Aina's standout feature is her intelligence. She understands how your Anita-powered site works.
    *   Tell her, "Create a homepage that lists the three most recent blog posts," and she will generate the necessary HTML and vanilla JavaScript to fetch data from the correct `/api/posts` endpoint and display it correctly.
    *   Need a template for individual blog posts? Aina will design a page that dynamically loads the post's title, content, and metadata based on the URL.
*   **Intelligent Form Integration**: Any custom form you create in the admin panel can be seamlessly "attached" by Aina. Just ask her to "add the contact form to this page," and she will generate the code to render the form and ensure it's wired up to the forms API for submissions.
*   **Visual Control Through Conversation**: From a complex landing page to a unique `/about-us` section, you can direct Aina with conversational prompts. Aina's sidebar panel gives you granular control, allowing you to embed specific routes or reuse styles from other pages you've created, ensuring a consistent and interactive final result.
*   **OpenAI Compatibility**: Just like Asta, Aina's creative power can be fueled by your preferred OpenAI-compatible AI provider. This gives you the flexibility to choose the model that best suits your creative and budgetary needs.

> Aina builds the house, interacting with the foundation (API). Asta writes the story inside. Anita approves.

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

### **`admin`**

Any page with this tag gets served at `/{slug}`. Ideal for standalone pages like `/about`, `/projects`, or `/pricing`. But they are also protected just like the admin page~

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


---

## 💡 Why Choose Anita?

Anita is for those who value simplicity, speed, and creative freedom. If you're looking for a CMS that stays out of your way and lets you build dynamic websites without a complex backend or expensive subscriptions, you've come to the right place.

**Important Note:** Anita is deliberately *not* designed for enterprise-level scalability or handling massive data volumes. If SQLite reaches its limits, so does Anita. We're focusing on simplicity, not massive scale.

### For the **Practical Dreamers**

*   Build dynamic websites and blogs without writing a single line of backend code.
*   Let Aina handle the API interactions while you focus on the vision.
*   Stay lightweight, fast, and completely understandable.
*   **No more overkill:** Ditch the complex enterprise CMS when all you need is a simple, powerful website.

### For the **Overworked and Underpaid**

*   Create stunning, interactive client sites at lightning speed.
*   One-click publishing and editing from a simple admin panel.
*   "It just works" — even when the deadline is tomorrow.
*   **Free yourself from subscription hell:** Stop paying $20 a month just to change the color of your headers. Anita gives you full control without the recurring fees.

### For the **Vanilla JS Enjoyers**

*   No `node_modules/` nightmares.
*   A truly hackable and transparent core.
*   Embrace the simplicity and power of vanilla JavaScript for a streamlined development experience.

### For the **Artists, Small Businesses, and Freelancers**

*   Anita is your go-to CMS for building portfolios, showcasing products, and connecting with your audience.
*   Create beautiful, API-driven websites that reflect your brand without the complexities of enterprise solutions.

### **Zero Lock-In Data**

*   Your content and forms are stored in simple `pages.db` and `forms.db` files.
*   Migrating from Anita is a breeze – no vendor lock-in, no proprietary formats. Your data is always accessible and portable.

---

## 🎨 Theming Made Stupid Simple (Coming Soon™)

Anita's theming system? **It's literally just importing a `.anita` file.**

### 🎭 How It Works

1.  **Drop the `.anita` file** into Anita
2.  **Boom.** All the theme's pages and assets appear right in your admin panel
3.  **Mix, match, and mashup** — Use Aina to combine elements from different themes or customize them to your heart's content

No build steps. No configuration hell. Just pure, unadulterated theme goodness delivered straight to your CMS.

### 🧩 What's Inside a `.anita` File?

*   **Complete page layouts** — Ready-to-use designs for home, about, contact, blog templates, you name it
*   **Assets** — Images, fonts, custom CSS, all bundled together
*   **Instant preview** — See everything in your admin panel before you commit
*   **Aina-friendly** — Ask Aina to help you adapt, combine, or extend any imported theme elements

Think of it as a theme capsule. Pop it open, and all the goodies spill into your workspace.

---

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

*   [ ] Indie Web Standard Integration
*   [ ] Working Theme And Official Theme Marketplace
*   [ ] Plugin System~
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
