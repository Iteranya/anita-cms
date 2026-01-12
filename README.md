<p align="center">
  <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anitacms.png" alt="Anita CMS Logo" width="512">
  <br><br>
  <a href="https://www.gnu.org/licenses/agpl-3.0">
    <img src="https://img.shields.io/badge/License-AGPL_v3-blue.svg" alt="License: AGPL v3">
  </a>
  <!-- Added Version Badge -->
  <a href="https://github.com/iteranya/anita-cms/releases">
    <img src="https://img.shields.io/badge/Version-0.38-brightgreen.svg" alt="Version 0.38">
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

- Want to backup your site? Copy anita.db and your uploads folder to Google Drive.
- Want to move servers? git pull the repo, paste your anita.db and uploads folder, and you're live.
- Need to scale? Since it uses SQLAlchemy, you can switch to PostgreSQL with one config change if you ever hit 1 million users (but for 99% of us, SQLite is faster, and Anita uses WAL by default).

This is *not* an exaggeration, yes, your entire site, this includes your custom home page and blog page and everything in between. Your configurations, your users, your roles, it's all in a single .db file. (No we don't store media file in db, we're not monsters)

## Starter Kits!

*Starting from a blank slate sucks. Anita knows this.*

Because Anita is a **"One-File Wonder"**, you can literally start by copying premade database!

When you run `main.py` for the first time (and Anita sees you don't have an `anita.db` yet), she enters **Interactive Setup Mode**.

1. She looks into the `anita-template/` folder.
2. She lists every `.db` file found there.
3. She asks: *"What are we building today?"*

You might see options like:
- `anita-blog.db`
- `anita-cafe.db` 
- `anita-art.db` 
- `anita-sass.db` 

Once you pick a number, she duplicates that template, renames it to `anita.db`, generates your security keys, and **boom**—your site is pre-populated and ready to go.

**Want to make your own Starter Kit?**
Configure a site exactly how you like it, run the 'seedmakinghelper.py', and drag the sanitized_anita.db into `anita-template/` folder, and rename it to whatever you like. Now you can reuse that setup forever.

## Runs on a Potato

*I'm broke so I know what 'broke hosting' is like*

Because Anita is built on FastAPI (Python), it's comical how lightweight she is
- Low RAM Usage: Unlike Java or Node apps, she sips memory.
- Low CPU Usage: Ideal for the cheapest VPS tier ($3-5/mo) or even a Raspberry Pi.
- No Build Step: No compiling assets on the server. Just run and go.
- No Database Overhead: SQLite runs natively in Python and it's literally just a single file

If you're a freelancer, you can host a dozen instance of Anita in a single server. (Given you handle CI/CD yourself, but that's another thing entirely)

## The "Low-Code" Backend

The coolest part. No black magic, just logic.

Usually, if you want a dynamic "Menu" page for a restaurant, you have to code a database model and an API route.

With Anita, you just do this:
- Open the Dashboard: Go to the "Collections" tab.
- Create a Collection: Name it cafe-menu.
- Add Fields: Add a "Text Field" for the Dish Name and a "Number Field" for the Price.
- Check the boxes for access permissions
- Done.

Anita automatically generates a secure API endpoint. The IDE is now aware of the api route and you can easily inject the required scripts (no code required), then you can simply code your own front end with Alpine and Tailwind through Aina IDE.

## Export To SSG

*For when you really, **really**, can't afford a hosting*

People say that trying to be good at everything is not a good idea

I agree, Anita is designed to be good at one thing and one thing only: Efficiency

Anita comes prepackaged with a simple pythons script that you can just run just like your main.py

That will create an entire dist folder containing an SSG Version of the site you made.

Current Features:

- Reflects Your Site Structure
- Reflects Your Blog/Page Listing/Search functions (if you use Aina)
- Creates a simple database of all your public page (Page must be marked as public to count)

Upcoming Probably Next Week Features:

- Creates A Reflection Your Collection Database
- Lets Your Custom Pages Display Those Collections

In other words, if you use Aina to generate your database, you can trust her that any GET public routes become accessible anywhere, even as static sites! 

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
| **Backend**  | FastAPI, SQLAlchemy                          |
| **Frontend**   | Tailwind, AlpineJS, HTMX                     |

Yes, that's all of them, seriously... 

Checkout requirements.txt if you want to see more.

---

##  Is it Safe?

Short answer: Yes. 
Long answer: We have trust issues.

- Transparent Architecture: No hidden binaries. What you see in main.py is what runs.
- Input Sanitization: We use Ammonia (Rust-based) to scrub every input.
- Discord-Style Permissions: We use ABAC. You can set exactly who can see or edit your cafe-menu. This means you don't give your intern or Karen from accounting the ability to break the website's homepage.

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

#### Collections (aka Collections)
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-collections.png" alt="Admin UI Collections" width="700"></p>
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-collections-setting.png" alt="Admin UI Collection Settings" width="700"></p>
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-collections-creation.png" alt="Admin UI Collection Creation" width="700"></p>
<em>Oh you think this is for a contact collection? It's a misnomer see? These are 'Collections', the no-code backend part of all this. You can make `contact-collection`, but you can also make `cafe-menu`, `art-gallery`, and more, with role based permissions! Anita will create an entire GET/POST/PUT/DELETE route endpoint that accesses these collections you made!</em>

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
<em>Forget about coding logic and focus on UI and presentation! With Tailwind, Awesome Fonts, and AlpineJS baked in, you have everything you need to create a gorgeous site! (Uses Ace Editor, Realtime Tailwind Update, Compiles Tailwind For You, You're Welcome)</em>

But what if I want to code in VS Code? I hear you asking. What if I want to have version control? I hear you asking.

Just use Anita headless, that works too, Hybrid, remember?

#### Asta Markdown Editor
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/asta-editor.png" alt="Aina Frontend IDE" width="700"></p>
<em>Built on top of the absolute gorgeous Milkdown Crepe, we present to you Asta Markdown Editor. A gorgeous UI to write your content with minimal fluff. You can save draft and simply publish them! And you can choose which template to use to render the post you've made!</em>

---

## For Poweruser: Headless CMS with Security Baked In

Oh so you want to code stuff in react? You want to hydrate your page with json?  Want to skip Aina and write your own Frontend froms scratch??? WELL OF COURSE YOU CAN!!!!

Anita comes with API (documentation pending) that lets you access every part of the CMS through JSON! Even the markdown contents! You can slap in any AI you like on top of Anita and it'll just work perfectly!!!

Not to mention that you still get to use the Admin Panel to manage your users, your pages security, generate all the collections and the strict ACL / RBAC control for each of those collections!!

(Also, hooks for plugin integration feature pending~)

---

## For Freelancers: The "Client-Proof" CMS

*Give them the keys to the car, but weld the hood shut.*

Look, client clicking a glowing 'update all' button is what kept us all up at night. Or maybe even clicking the theme thinking they can change the site without you knowing. We've all been there.

Anita, however, allows you to "Client-Proof" the delivery.

Using our strict Attribute-Based Access Control (ABAC) and Security Matrix, you can curate the exact experience your client needs—and nothing more.

- The "Menu Updater" Role: Does the restaurant owner only need to change prices? Create a role that has UPDATE permission on the cafe-menu collection, but NO ACCESS to Pages, Settings, or Media. They won't even see the other buttons.
- The "Blog Writer" Role: Give them access to Asta (Markdown) to write news, but block access to Aina (Builder) so they can't break the layout.
- System Locks: Critical pages (like Home or 404) are protected by System Labels. Even if you give a client "Delete Page" permissions, Anita will refuse to delete a System-Labelged page.
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
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

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
- CSRF Token (Come on... Why is this so hard???)
- ~~HikarinJS Is Still Opt-in (should be default for all ai generated site)~~ Done! Hikarin JS is first class citizen now~
- ~~Default Pages Still Uses script (Should use HikarinJS Instead)~~ Done! Script exists, but it uses Hikarin middleware now~
- ~~System Page Labels Are Still Manual (Should be abstracted with switches / panel)~~ Done! Made new panel for Structure
- ~~Collection Page Labels Are Still Manual (Should be abstracted with switches / panel)~~ Done! With amazing RBAC Panel
- ~~User Roles and Perms Are Still Manual (Should be abstracted with switches / panel)~~ Done! Discord Flavored ABAC Panel~
- No Tags and Sort Filter Yet (Come on....)
- No Darkmode Yet (seriously?)
- ~~Submission Sanitization not yet implemented~~ Done! (With ammonia, bleach is deprecated)
- Pay Yozzun For Anita's Artwork
- Add Event Bus and Background Handler
- Fediverse/ActivityPub Implementation (I really, really want this but god this is HARD. Stupid Hard.)
- Add better site audit, create snapshot of site structure, schema, role, permission, in JSON to make it possible to git diff
- ~~Asta and Aina doesn't save their own prompt/configuration~~ Done! They save now!
- ~~Remove AI Integration~~ Done! Aina is an IDE now~ 
- ~~Implement Milkdown / Crepe to Asta~~ Done! Asta is Milkdown powered!
- ~~Fix templating system to be True SSR~~ Done! Markdown Pages are now true SSR
- Give Asta (or Aina) a Search Engine Optimization capability 
- Better test coverage
- ~~More graceful Collection Seeding (currently don't exist, actually, only page, roles and config for now)~~ Done! With Starter Kit Feature!
- ~~Category and Labels are the same (should be separated)~~ Done! We have tags (public) and labels (system) now
- Sandbox Aina properly (Dummy Browser, Dummy Database, Dummy Dynamic API... Goddammit, I'll add disclaimers for now)

Terrible Ideas That Won't Go Away

- ~~Let Every User Bring Their Own Admin Page (Actually good idea, but like, CUSTOM Admin Page, not replacing Dashboard)~~ Actually implemented, lmao
- Anita AI Chatbot on Dashboard
- Rewrite Everything In Go
- Rewrite Everything In Rust
- ~~Export to SSG Button (HOW!?!?)~~ HOLY SHIT I ACTUALLY FIGURED IT OUT!!!
- Let Every User Bring Their Own API Key (The least terrible idea honestly, I should put it up there)
- Hikarin Website Builder To Replace Aina (Note: Hikarin Website Builder Does Not Exist Yet)
- Discord Integration (For... I'm not sure for what... But it'll be cool)
- ~~Make Domain Specific Language For Themes and Plugins~~ No Themes, Only Starter Kits!

---

## QnA

Q: Is this project ready for..
A: No

Q: Can I use this for...
A: Yes

Q: What if I...
A: No Gatekeeping

Q: Do I need to be good at python???
A: The admin page is designed so that you don't have to touch a single line of Python. Tailwind and Alpine experience will help you much, much more than Python knowledge.

Q: Documentation? Plugins?
A: After I implement the Event Bridge, because honestly I'll have to rewrite the documentation from scratch if I write it now.

Q: Should I just use Postgre?
A: Do you have 500 editors???

Q: I need version control!
A: Just skip Aina and bring your own Frontend... You can still use Asta for the markdown (unless you want to version control markdown??? In which case, I'll think about adding that feature to Asta). Ah but if you skip Aina you lost the Export to SSG Feature~ Well... Drawbacks, I suppose... You can theoretically version control your SSG, now that I think about it, but you can't version control Aina/Asta editor itself...

Q: Anita? Hikarin? Asta? Aina?
A: THEY'RE CUTE! FIGHT ME!!!

---

## License: AGPL-3.0

AGPL-3.0 - Free To Use, No Gatekeep Allowed.
