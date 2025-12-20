
<details>
<summary><strong>Prologue: Are we live?</strong></summary>
<br>

<table>
<tbody>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Are we live?
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Live as in read me? Yes. Live as in production? No.
    </td>
  </tr>
    <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Okay, okay, deep breath...
    </td>
  </tr>
</tbody>
</table>

</details>

---

    
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
- She helps with the Frontend: She includes an AI Page Builder (Aina) and Markdown Editor (Asta).

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

Anita automatically generates the database table inside anita.db and creates a secure API endpoint. The AI is now aware of the api route and you can ask the AI to create a working menu page. Or you can simply code your own front end with Alpine and Tailwind.


<details>
<summary><strong>Chapter 1: The Introduction</strong></summary>
<br>

<table>
<tbody>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Hi Hi! I am Anita, your brand new Content Management System.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      I'm the dev.
    </td>
  </tr>
    <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Yep! And as you can see, I am way, way different from most CMS out there. Without NodeJS overhead or node modules... I'm designed to be super light, secure, and efficient!
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      And out of spite of the last 10 years of Software Development.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Artes! We can't say that on the github repo!
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Ahem, what Artes means is that, he created me as an effort to save the internet! To create a place made for the people, but they people! No longer shackled by-
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      I don't give a shit about saving the Internet, I just want to see Wordpress and NodeJS Dead
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      WE CAN'T SAY THAT ON A PUBLIC REPO!!! Cut, Cut!
    </td>
  </tr>
</tbody>
</table>

</details>

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

In a sense, yes. It is designed to be a safer alternative to Wordpress, with lots and lots of safeguards, performance and optimizations, and responsible AI use (more on that later).

---

<details>
<summary><strong>Chapter 2: The Pitch</strong></summary>
<br>

<table>
<tbody>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      As you can see, my use case is the exact same as Wordpress!!!
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Without plugins, or the ecosystem, or the bus factor.
    </td>
  </tr>
    <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Okay, okay, hush! You're scaring our user!<br/><br/>
      Listen, listen, you want a nice secure modern website with a simple core and security and performance first architecture? I'm your girl! Yes, you'll be an early adopter, but hey! I'm worth the investment, I promise!<br/><br/>
      Now then, architecture!
    </td>
  </tr>
</tbody>
</table>

</details>

---

## Architecture

Anita is designed with a simple, foundational architecture in mind. No black box, no magic, what you code is what you get.

| Layer      | Technology                                    |
| :--------- | :-------------------------------------------- |
| **Backend**  | FastAPI & SQLAlchemy                          |
| **Frontend**   | Tailwind, AlpineJS & HTMX                     |
| **Utility**   | Hikarin Framework                   |

Yes, that's all of them, seriously... 

Checkout requirements.txt if you want to see more.

---
<details>
  <summary> The Tech Stack </summary>
<table>
<tbody>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      See that? My frontend runs on AlpineJS, my SPA Admin Page uses HTMX, and everything uses the Hikarin Framework
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/hikarin_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Hikarin Avatar"/>
    </td>
    <td>
      <strong>Hikarin</strong><br/>
      Hello~ I'm not a framework
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Hikarin-senpai! Hi! So yes, Hikarin is a Web Development Framework / Paradigm that the dev is working on.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/hikarin_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Hikarin Avatar"/>
    </td>
    <td>
      <strong>Hikarin</strong><br/>
      Hi, that's a misunderstanding Technically speaking, it is an Application Entry Point (Bootstrapper) that implements a Service Layer pattern. Just a folder with JS in it and the web framework thing is still under work, which is different?
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Indeed! As for the Backend it uses FastAPI with strict Pydantic schemas and SQLAlchemy ORM. Data Integrity is paramount see? So no worries about SQL Injection, all your data is safe with me!
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/hikarin_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Hikarin Avatar"/>
    </td>
    <td>
      <strong>Hikarin</strong><br/>
      And... you're not listening to me... okay then... not hurt or anything...
    </td>
  </tr>
</tbody>
</table>

</details>

---

##  Is it Safe?

Short answer: Yes. 
Long answer: We have trust issues.

- Transparent Architecture: No hidden binaries. What you see in main.py is what runs.
- Input Sanitization: We use Ammonia (Rust-based) to scrub every input.
- Discord-Style Permissions: We use ABAC. You can set exactly who can see or edit your cafe-menu.
- No <script> Tags: We bleach anything resembling script *before* they touch the database.

<details>
  <summary> About Security </summary>
<table>
<tbody>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Nee... Artes, don't you think the current security policy a little bit... Excessive? 
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Alpha, remember?
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      You bleached the json keys... ***The Keys***
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      I'll make it optional and configurable per-form and per-submission
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      That's not... Recursively go through the custom json field and nuking every html object is *not* security, that's a cry for help
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Should I escape string instead??
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Well... Look... Why's the paranoia? Who hurt you dev?
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Aina, Aina hurt me, I don't trust Aina to write a secure HTML
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      And you think bleaching the database is the right move?
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      It's temporary, don't worry, I'll figure out per-page CSP and Form/Submission security through Hikarin. Oh and drag and drop website builder with GrapeJS.
    </td>
  </tr>
</tbody>
</table>

</details>

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
<em>Oh you think this is for a contact form? Nyahaha~ It's a misnomer see? These are 'Collections', the no-code backend part of all this. You can make `contact-form`, but you can also make `cafe-menu`, `art-gallery`, and more, with role based permissions! Anita will create an entire GET/POST/PUT/DELETE route endpoint that accesses these forms you made!</em>

#### Media & Files
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-media.png" alt="Admin UI Media" width="700"></p>
<em>Tired of Orphan media? Worry not! Anita Keeps Track of Everything!</em>

#### Users & Roles
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/admin-ui-user-and-roles.png" alt="Admin UI User And Roles" width="700"></p>
<em>The heart of security!!! Inspired by Discord, you can create roles with fine-grained permissions.</em>

---

<details>
<summary><strong>Chapter 4: The Gallery Review</strong></summary>
<br>

<table>
<tbody>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Ahhh~ It looks so cool! Look at that! Look at that! It's Gorgeous!!! Aaaahh~ I love it!
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      It's all AI Generated by Aina, I don't do front end.
    </td>
  </tr>
    <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      I don't care! It looks amazing!!! 
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Right, right... Still, hmm...
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Nyaaa~ No worries Artes! It's great! It's great! Really!
    </td>
  </tr>
</tbody>
</table>

</details>

---

## The AI Part...

Okay, look, listen, I hate AI slop as much as you do. But until the Hikarin Web Builder is finished, we have to do with what we got. Or if you're comfortable, you can code AlpineJS and Tailwind from scratch.

#### Aina AI Page Builder
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/aina-ai.png" alt="Aina AI" width="700"></p>
<em>You see that??? No hallucinating routes, no hallucinating stock images. You pick what data you want AI to access. You pick what media you want AI to add. The prompt result is right there. You can use the API integration or just copy that prompt and use any other AI you like.</em>

#### Asta Markdown Editor
<p align="center"><img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/asta-markdown-editor.png" alt="Asta Markdown Editor" width="700"></p>
<em>It's a markdown Editor. ... Might remove AI later and replace it with git for versioning and proper ctrl+z.</em>

---

<details>
<summary><strong>Chapter 5: The AI Debate</strong></summary>
<br>

<table>
<tbody>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Okay, AI is no longer a first-class citizen, this is good, phew.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Hmm... You know if this were any other project, being AI Powered is a selling point.
    </td>
  </tr>
    <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      It's not! Shut up! We need to get the Hikarin Web Builder ready ASAP.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      I'm still gonna use AI...
    </td>
  </tr>
</tbody>
</table>

</details>
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
- 
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

<details>
<summary><strong>Chapter 6: The Reality Check</strong></summary>
<br>

<table>
<tbody>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Looks simple enough~
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Oh we should add docker integration!
    </td>
  </tr>
    <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Maybe after you matured a little bit? All essential features up and running.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      I'm ready!!! What do you mean??? All features implied and explained here exist! I'm secure! My database is performant and ready!
    </td>
  </tr>
    <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Dark Mode.
    </td>
  </tr>
    <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      I am... *almost* ready!!!
    </td>
  </tr>
</tbody>
</table>

</details>

---

## Roadmap

- ~~Editing HTML should be exclusive to Aina~~
- ~~Editing Markdown should be exclusive to Asta~~
- Mitochondria Is The Powerhouse of Cell
- ~~Bleach Is Not Implemented Properly Yet~~ Done! (With ammonia, bleach is deprecated)
- CSP Configuration Is Still Globally Strict (should be configurable per-page basis)
- HikarinJS Is Still Opt-in (should be default for all ai generated site)
- Default Pages Still Uses <script> (Should use HikarinJS Instead)
- ~~System Page Tags Are Still Manual (Should be abstracted with switches / panel)~~ Done! Made new panel for Structure
- ~~Form Page Tags Are Still Manual (Should be abstracted with switches / panel)~~ Done! With amazing RBAC Panel
- ~~User Roles and Perms Are Still Manual (Should be abstracted with switches / panel)~~ Done! Discord Flavored ABAC Panel~
- No Tags and Sort Filter Yet
- No Darkmode Yet (seriously?)
- ~~Submission Sanitization not yet implemented~~ Done! (With ammonia, bleach is deprecated)
- Pay Yozzun For Anita's Artwork
- Asta and Aina doesn't save their own prompt/configuration
- Better test coverage
- More graceful Form Seeding (currently don't exist, actually, only page, roles and config for now)
~~- Category and Tags are the same (should be separated)~~ Cats and Tags, see below
- Sandbox Aina properly (Dummy Browser, Dummy Database, Dummy Dynamic API... Goddammit, I'll add disclaimers for now)
- ~~Add the cats~~
- ~~Get rid of the cats and refactor the entire fucking database to have label (system) and tag (public) instead of tag (system) and cat(public)~~ (won't fix, weird naming convention, deal with it)

Terrible Ideas That Won't Go Away

- Let Every User Bring Their Own Admin Page (:skull:)
- Anita AI Chatbot on Dashboard
- Rewrite Everything In Go
- Rewrite Everything In Rust
- Export to SSG Button (HOW!?!?)
- Let Every User Bring Their Own API Key (The least terrible idea honestly, I should put it up there)
- Hikarin Website Builder To Replace Aina (Note: Hikarin Website Builder Does Not Exist Yet)
- Discord Integration (For... I'm not sure for what... But it'll be cool)
- Make Domain Specific Language For Themes and Plugins (Lol, Lmao, Pffft)

---

<details>
<summary><strong>Epilogue: The Future</strong></summary>
<br>

<table>
<tbody>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      See? Long ways to go~
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Wait! Okay, look, let's focus on umm... CSP Header Control and Finetuned Bleach Control.
    </td>
  </tr>
    <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Well someone's security conscious.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Oh no, it just looks really cool in the UI and is technically impressive.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      What about prompt engineering on Aina?
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      *shrug*
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      You have a good AI integration, be proud of it.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Bad marketing, people hate AI and I put all my cards on the Hikarin Website Builder. Actually, why not build Hikarin on top of Grape?
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      I tried, they fought for DOM control, Hikarin is closer to Gridstack.js than Grape.js in terms of building technique, I'll have to code Hikarin from scratch or build it on top of GradeJS
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Why don't you pull up standard GrapeJS integration??
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      I... Don't feel like adding feature that I myself can't even use.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Huh??
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      I never get the hang of... Well, Website builder, I don't find them intuitive, it feels... I dunno, weird... Boxes jumping around... I don't like em... I can't implement it because I don't know what the 'correct' implementation would be like, since I myself can't even use  Wix/Gutenberg/Elementor/Squarespace properly... 
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Wow... Huh... That's... really cool actually... What makes Hikarin different from GrapeJS? Why Gridstack?
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Layers, I want to make a website builder where you drag component and you have layer, instead of putting component inside one another. Also bento-box layout, but freedom of overlapping. So it's closer to Aseprite. Nothing forces you to put component somewhere. We have Z-index. GrapeJS won't let me do that easily.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Because...
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Gutenberg/Elementor like editor confuses me
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      Right...
    </td>
  </tr>
</tbody>
</table>

</details>

---

## License: AGPL-3.0

AGPL-3.0 - Free To Use, No Gatekeep Allowed.

<details>
<summary><strong>...</strong></summary>
<br>

<table>
<tbody>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/artes_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Artes Avatar"/>
    </td>
    <td>
      <strong>Artes</strong><br/>
      Have fun then.
    </td>
  </tr>
  <tr>
    <td width="52" valign="top" style="padding-right: 10px;">
      <img src="https://raw.githubusercontent.com/iteranya/anita-cms/main/docs/anita_avatar.png" width="48" height="48" style="border-radius: 50%;" alt="Anita Avatar"/>
    </td>
    <td>
      <strong>Anita</strong><br/>
      See ya! Thanks for visiting!
    </td>
  </tr>
</tbody>
</table>

</details>
