# 🌸 Anita CMS

*"Amiya, Aina, and Asta walk into a codebase..."*

<div align="center">
  <img src="https://github.com/user-attachments/assets/f3ab4ac9-853b-4be9-be92-560f0948caaf" alt="Anita" width="557" height="557" style="border: 2px solid #f0f0f0; border-radius: 8px; padding: 5px;" />
</div>

**Anita CMS** is a lightweight, AI-assisted, hybrid content management system that combines:

*   **Amiya's** clean admin power 💼
*   **Aina's** visual, API-aware web generation 🎨
*   **Asta's** markdown mastery 🖋️

All running on **FastAPI + SQLite**, with **zero Node.js dependency** and pure **vanilla JS** magic.
*(Yes, it's actually fast. Like, under-50ms fast.)*

---

## 🌟 What's Inside Anita?

Anita isn't just a CMS; it's a creative suite powered by two distinct AI personalities, Asta and Aina, who handle the writing and the building, so you can focus on the vision.

### 🖋️ **Asta: The AI-Powered Markdown Editor**

Asta is your dedicated writing assistant, perfect for crafting content-rich pages like blogs, documentation, or articles. She lives inside a clean, real-time Markdown editor designed to keep you in the flow.

*   **Effortless Content Creation**: Write and publish beautiful Markdown pages with a live preview. Tag your work as a `blog` post or save it as a draft with a single click.
*   **One-Shot AI Assistance**: Asta's AI integration is designed for maximum flexibility and speed:
    *   **Perfect Prompt Engineering**: Click the magic button to copy expertly crafted prompts that you can feed into any AI service—ChatGPT, Claude, local models, whatever works for you.
    *   **Media-Aware Prompts**: Use the media panel to inject images directly into your prompt. Asta will include them in the generated prompt engineering text, so the AI can reference your visuals when writing.
    *   **One-Shot Workflow**: No back-and-forth conversation needed. Generate your prompt, get your content, paste it back. Clean, fast, and distraction-free.
    *   **AI Notes**: A dedicated 'notes' section helps you provide specific instructions, tone guidelines, or context that you want included in the generated prompt.
*   **Bring Your Own AI**: No API keys required unless you want them. Use web-based AI services, local models, or configure an OpenAI-compatible endpoint if you prefer automation. The choice is always yours.

### 🎨 **Aina: The API-Aware AI Website Builder**

Aina is the architect and visual designer of your website. Unlike other AI builders that just fill in templates, Aina is fully aware of your site's backend, routes, and APIs, allowing her to generate pages that are not only beautiful but also fully functional.

*   **True API-Aware Generation**: Aina's standout feature is her intelligence. She understands how your Anita-powered site works.
    *   Tell her, "Create a homepage that lists the three most recent blog posts," and she will generate the necessary HTML and vanilla JavaScript to fetch data from the correct `/api/posts` endpoint and display it correctly.
    *   Need a template for individual blog posts? Aina will design a page that dynamically loads the post's title, content, and metadata based on the URL.
*   **Intelligent Form Integration**: Any custom form you create in the admin panel automatically creates a new API route. Aina knows about these routes and can generate the code to render forms, fetch data from them, or wire up submissions.
*   **One-Shot Creation**: Like Asta, Aina works in a single generation pass. Click to generate your perfectly engineered prompt, complete with media references from the media panel, then feed it to your AI of choice. The result? Production-ready HTML and JavaScript that just works.
*   **Superior UI**: Aina's prompt engineering panel makes it ridiculously easy to specify exactly what you want. Attach images, reference existing routes, set the tone—all in a clean interface that respects your workflow.
*   **Bring Your Own AI**: No forced subscriptions. Copy the prompt and use any AI service you prefer, or configure an OpenAI-compatible endpoint for direct integration. Freedom is the point.

> Aina builds the house, interacting with the foundation (API). Asta writes the story inside. Anita approves.

---

### 💌 Mail System (via Resend)

A modern CMS needs a reliable way to communicate.

*   Simplified mail configuration under **Admin → Config → Mail**.
*   Built on Resend for high deliverability and ease of use.
*   Power your contact forms, user notifications, and more without complex setups.

---

### 🧾 Forms: Your Secret Weapon for Custom Functionality

Anita's form system isn't just about contact pages—it's a backdoor to building custom databases and admin panels without touching a line of backend code.

#### **How It Works**

When you create a custom form in the admin panel, Anita automatically:

*   **Generates a new API route** for that form (e.g., `/api/forms/cafe-menu`)
*   **Creates a dedicated database table** to store submissions
*   **Exposes full CRUD operations** (Create, Read, Update, Delete) via the API

#### **Granular Security Control**

Each form has separate permission settings for admin and guest users:

*   **Admin permissions**: Full control (CRUD) from the admin panel
*   **Guest permissions**: What public visitors can do
    *   `READ` only: Perfect for displaying data (like a cafe menu carousel)
    *   `WRITE` only: Perfect for accepting submissions (like a contact form)
    *   Mix and match as needed

#### **Real-World Magic**

*   **Cafe Menu**: Create a "Menu Items" form with fields like `name`, `price`, `description`, `image`. Set guest permissions to `READ` only. Now Aina can generate a beautiful menu page that fetches from `/api/forms/menu-items`.
*   **Contact Form**: Standard contact form with `WRITE` permissions for guests. Submissions go straight to your admin panel.
*   **Event Planner**: Create an "Events" form with date, location, and description fields. Build a public events calendar that reads from the API and an admin panel where you manage entries.

#### **Build Custom Admin Panels**

Tag a page with `admin` and have Aina generate a "Menu Management Panel" that lets you edit your cafe's offerings through a beautiful interface—all powered by your custom form's API. No backend coding required.

*   View all submissions in one place
*   **Export as CSV** for use in spreadsheets or other tools
*   Create, edit, and delete entries with a few clicks

**The genius**: Forms are secretly custom databases with instant API access. Your imagination is the only limit.

---

### 🔐 Security

Simple, robust, and secure by default.

*   **JWT + Cookies + Admin authentication** ensures your management panel is protected.
*   **Granular form permissions** let you control exactly who can do what with your custom databases.
*   Secure defaults are baked in, so you can focus on creating.

---

## 🏷️ Important Tags

Anita uses tags to assign special roles to pages, unlocking automatic routing and functionality.

### **`home`**

The chosen one. The page with this tag becomes your site's landing page at `/`.

### **`blog`**

Pages with this tag are automatically listed on your blog homepage.

### **`blog-home`**

Marks a page as the main blog listing, served at `/blog`.

### **`blog-template`**

The layout for individual blog posts, rendered at `/blog/{slug}`. Aina can generate a design for this that correctly fetches and displays post content.

### **`main`**

Any page with this tag gets served at `/{slug}`. Ideal for standalone pages like `/about`, `/projects`, or `/pricing`.

### **`admin`**

Pages with this tag get served at `/{slug}` but are protected behind authentication. Perfect for custom admin panels like your "Menu Management Dashboard."

---

## ⚙️ Tech Stack

| Component | Technology |
| :--- | :--- |
| Backend | FastAPI + SQLite |
| Frontend | Vanilla JS |
| Markdown Editor | Asta Editor |
| HTML Generator | Aina System |
| AI Layer | Bring Your Own (or OpenAI-compatible) |
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
3.  Build custom forms to create instant APIs and databases for your specific needs.
4.  Tag your homepage, blog pages, and other main pages.
5.  Publish and brag about building a fully functional, API-driven site in under an hour.

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

*  Use Aina-chan's integrated form API to create a dashboard to edit your cafe menu
*  Build a form-powered portfolio system with filterable projects and categories
*  Create a custom event management system with booking capabilities

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
*   [ ] "That's not a bug, it's a feature" mode

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
*   Tell Anita she's doing great (she thrives on validation)

---

## 📜 License

**AGPL-3.0** — because open source should stay open 💖
