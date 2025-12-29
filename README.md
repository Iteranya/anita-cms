   
<p align="center">
  <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anitacms.png" alt="Anita CMS Logo" width="512">
  <br><br>
  <a href="https://www.gnu.org/licenses/agpl-3.0">
    <img src="https://img.shields.io/badge/License-AGPL_v3-blue.svg" alt="License: AGPL v3">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.10+-yellow.svg" alt="Python">
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/Framework-FastAPI-009688.svg" alt="FastAPI">
  </a>
  <a href="https://www.sqlalchemy.org/">
    <img src="https://img.shields.io/badge/ORM-SQLAlchemy-red.svg" alt="SQLAlchemy">
  </a>
</p>
<h1 align="center">Anita CMS - The No-Code Hybrid Content Management System</h1>
<h3 align="center">Alpha Release: Here Be Dragons</h2>

---

## What Is Anita?

Anita is a tool you use to create a website.

Anita is a self-hosted, hybrid CMS designed to be the "lite" alternative to WordPress/Wix/Squarespace/Drupal/Joomla/Directus/EveryCMSUnderTheSun. She is built for people who want a portfolio, a gallery, a shop, or a blog, but don't want to deal with complex databases or expensive server costs. 

(Note: She still can't replace SSG, sorry)

I call Anita Hybrid because:

- She handles the Backend: You define the data, she builds the API.
- She helps with the Frontend: She includes an Integrated IDE (Aina) and Markdown Editor (Asta).

## The "One-File" Wonder

*The ultimate portable CMS.*

Most CMSs require a database server, a file server, and a config file. Moving them is a nightmare.

Anita stores EVERYTHING in a single file.

- Want to backup your site? Copy anita.db to Google Drive.
- Want to move servers? git pull the repo, paste your anita.db, and you're live.
- Need to scale? Since it uses SQLAlchemy, you can switch to PostgreSQL with one config change if you ever hit 1 million users (but for 99% of us, SQLite is faster).

This is *not* an exaggeration, yes, your entire site, this includes your custom home page and blog page and everything in between. Your configurations, your users, your roles, it's all in a single .db file.

## Runs on a Potato

*I'm broke so I know what 'broke hosting' is like*

Because Anita is built on FastAPI (Python), it's comical how lightweight she is
- Low RAM Usage: Unlike Java or Node apps, she sips memory.
- Low CPU Usage: Ideal for the cheapest VPS tier ($3-5/mo) or even a Raspberry Pi.
- No Build Step: No compiling assets on the server. Just run and go.
- No Database Overhead: SQLite runs natively in Python and it's literally just a single file

If you're a freelancer, you can host a dozen instance of Anita in a single server. (Given you handle CI/CD yourself, but that's another thing entirely)

## The "No-Code" Backend

The coolest part. No black magic, just logic.

Usually, if you want a dynamic "Menu" page for a restaurant, you have to code a database model and an API route.

With Anita, you just do this:
- Open the Dashboard: Go to the "Collections" tab.
- Create a Form: Name it cafe-menu.
- Add Fields: Add a "Text Field" for the Dish Name and a "Number Field" for the Price.
- Check the boxes for access permissions
- Done.

Anita automatically generates a secure API endpoint. The IDE is now aware of the api route and you can easily inject the required scripts (no code required), then you can simply code your own front end with Alpine and Tailwind through Aina IDE.

---

## Why Anita?

The better question is, 'When is Anita'?

-   When you want a portfolio website
-   A little corner of the web that is yours
-   A neat shop, catalogue, or gallery page
-   Information Page for Local School or even City
-   Low to Medium Traffic Website
-   Literally Anything Wordpress Can Offer You
-   Okay maybe wordpress without the ecosystem

**Is Anita designed to replace wordpress?**

In a sense, yes. It is designed to be a safer alternative to Wordpress, with lots and lots of safeguards, performance and optimizations.

---

## Architecture

Anita is designed with a simple, foundational architecture in mind. No black box, no magic, what you code is what you get.

| Layer      | Technology                                    |
| :--------- | :-------------------------------------------- |
| **Backend**  | FastAPI & SQLAlchemy                          |
| **Frontend**   | Tailwind, AlpineJS & HTMX                     |

Yes, that's all of them, seriously... 

Checkout requirements.txt if you want to see more.

---

##  Is it Safe?

Short answer: Yes. 
Long answer: We have trust issues.

- Transparent Architecture: No hidden binaries. What you see in main.py is what runs.
- Input Sanitization: We use Ammonia (Rust-based) to scrub every input.
- Discord-Style Permissions: We use ABAC. You can set exactly who can see or edit your cafe-menu.

## The Admin Page

You know what they say, a picture is worth a thousand words...

#### Dashboard
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-dashboard.png" alt="Admin UI Dashboard" width="700"></p>
<em>Honestly not that impressive, but hey, it's a dashboard~ No worries, Page Metric Feature Coming Up Real Soon!</em>

#### Pages
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-pages.png" alt="Admin UI Pages" width="700"></p>
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-pages-setting.png" alt="Admin UI Pages Setting" width="700"></p>
<em>Is it too simple? That's a compliment. Does it work? Hell yes. This is where you look for and modify pages you see? Mark page as html or markdown, change title and description and more!</em>

#### Structures
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-structure.png" alt="Admin UI Structures" width="700"></p>
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-structure-setting.png" alt="Admin UI Structure Setting" width="700"></p>
<em>You want to separate projects, blogs, and gallery sections of your site??? Well with Anita it's a drag and drop interface~ You can set any page as home, as template, as the head of any top level navigation, and more! Comes with Access Control too!</em>

#### Forms (aka Collections)
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-forms.png" alt="Admin UI Forms" width="700"></p>
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-forms-setting.png" alt="Admin UI Form Settings" width="700"></p>
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-forms-creation.png" alt="Admin UI Form Creation" width="700"></p>
<em>Oh you think this is for a contact form? It's a misnomer see? These are 'Collections', the no-code backend part of all this. You can make `contact-form`, but you can also make `cafe-menu`, `art-gallery`, and more, with role based permissions! Anita will create an entire GET/POST/PUT/DELETE route endpoint that accesses these forms you made!</em>

#### Media & Files
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-media.png" alt="Admin UI Media" width="700"></p>
<em>Tired of Orphan media? Worry not! Anita Keeps Track of Everything!</em>

#### Users & Roles
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-user-and-roles.png" alt="Admin UI User And Roles" width="700"></p>
<em>The heart of security!!! Inspired by Discord, you can create roles with fine-grained permissions.</em>

---

## The AI Part... SIKE! THERE IS NO AI!!!

While Aina used to be a Deepsite Clone, this is no longer the case!

Introducing, Aina Integrated Web IDE!!!

#### Aina Backend Generator
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/aina-generator.png" alt="Aina Backend Generator" width="700"></p>
<em>Browse through the libraries of pre-made alpine component and integrated it into your website! Everything is toggleable with just a click  *and* it is completely safe! The alpine components are designed to interact with Aina Database, aware of all your pages and custom collections too!</em>

#### Aina Frontend Generator
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/aina-editor.png" alt="Aina Frontend IDE" width="700"></p>
<em>Forget about coding logic and focus on UI and presentation! With Tailwind, Awesome Fonts, and AlpineJS baked in, you have everything you need to create a gorgeous site!</em>

---

## For Freelancers: The "Client-Proof" CMS

*Give them the keys to the car, but weld the hood shut.*

Look, client clicking a glowing 'update all' button is what kept us all up at night. Or maybe even clicking the theme thinking they can change the site without you knowing. We've all been there.

Anita, however, allows you to "Client-Proof" the delivery.

Using our strict Attribute-Based Access Control (ABAC) and Security Matrix, you can curate the exact experience your client needs—and nothing more.

- The "Menu Updater" Role: Does the restaurant owner only need to change prices? Create a role that has UPDATE permission on the cafe-menu collection, but NO ACCESS to Pages, Settings, or Media. They won't even see the other buttons.
- The "Blog Writer" Role: Give them access to Asta (Markdown) to write news, but block access to Aina (Builder) so they can't break the layout.
- System Locks: Critical pages (like Home or 404) are protected by System Tags. Even if you give a client "Delete Page" permissions, Anita will refuse to delete a System-Tagged page.
- Advanced: Create your client their very own custom admin page that they can use to update their menu without touching the admin panel

Result: They feel empowered to update their content. You sleep soundly knowing they can't nuke the database.

---

## Installation

#### Windows (One-Click)
1.  Download the `anita_installer.bat` file from the Release Page.
2.  Double-click to install.
3.  Launch via the desktop shortcut.

#### Mac / Linux / Manual Setup
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

## Roadmap

- ~~Editing HTML should be exclusive to Aina~~
- ~~Editing Markdown should be exclusive to Asta~~
- Mitochondria Is The Powerhouse of Cell 
- ~~Bleach Is Not Implemented Properly Yet~~ Done! (With ammonia, bleach is deprecated)
- ~~CSP Configuration Is Still Globally Strict (should be configurable per-page basis)~~ Done! Per-page CSP Implemented!
- ~~HikarinJS Is Still Opt-in (should be default for all ai generated site)~~ Done! Hikarin JS is first class citizen now~
- ~~Default Pages Still Uses script (Should use HikarinJS Instead)~~ Done! Script exists, but it uses Hikarin middleware now~
- ~~System Page Tags Are Still Manual (Should be abstracted with switches / panel)~~ Done! Made new panel for Structure
- ~~Form Page Tags Are Still Manual (Should be abstracted with switches / panel)~~ Done! With amazing RBAC Panel
- ~~User Roles and Perms Are Still Manual (Should be abstracted with switches / panel)~~ Done! Discord Flavored ABAC Panel~
- No Tags and Sort Filter Yet
- No Darkmode Yet (seriously?)
- ~~Submission Sanitization not yet implemented~~ Done! (With ammonia, bleach is deprecated)
- Pay Yozzun For Anita's Artwork
- Fediverse/ActivityPub Implementation (I really, really want this but god this is HARD)
- ~~Asta and Aina doesn't save their own prompt/configuration~~ Done! They save now!
- ~~Remove AI Integration~~ Done! Aina is an IDE now~ 
- Implement Milkdown / Crepe to Asta
- Better test coverage
- More graceful Form Seeding (currently don't exist, actually, only page, roles and config for now)
- Category and Tags are the same (should be separated)
- Sandbox Aina properly (Dummy Browser, Dummy Database, Dummy Dynamic API... Goddammit, I'll add disclaimers for now)


Terrible Ideas That Won't Go Away

- ~~Let Every User Bring Their Own Admin Page (Actually good idea, but like, CUSTOM Admin Page, not replacing Dashboard)~~ Actually implemented, lmao
- Anita AI Chatbot on Dashboard
- Rewrite Everything In Go
- Rewrite Everything In Rust
- Export to SSG Button (HOW!?!?)
- Let Every User Bring Their Own API Key (The least terrible idea honestly, I should put it up there)
- Hikarin Website Builder To Replace Aina (Note: Hikarin Website Builder Does Not Exist Yet)
- Discord Integration (For... I'm not sure for what... But it'll be cool)
- Make Domain Specific Language For Themes and Plugins

---

## License: AGPL-3.0

AGPL-3.0 - Free To Use, No Gatekeep Allowed.
