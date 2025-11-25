
# 🌸 Anita: Your Creative Partner for the Web

<div align="center">
  <img src="https://github.com/user-attachments/assets/f3ab4ac9-853b-4be9-be92-560f0948caaf" alt="Anita" width="557" height="557" style="border: 2px solid #f0f0f0; border-radius: 8px; padding: 5px;" />
</div>

Tired of expensive monthly fees, complicated website builders, and templates that just don't feel like *you*?

**Anita is different.** It’s a simple, powerful tool that helps you build a beautiful, fast, and completely custom website without needing to be a tech wizard. Think of it as your own personal creative studio, powered by a friendly AI team who handles the hard stuff so you can focus on what you do best.

Best of all? **It's free.** No subscriptions, no hidden costs. Just your creativity, unleashed.

---

## 🌟 Meet Your AI Creative Team

Anita comes with two AI assistants who work together to bring your vision to life. You can use them with any AI you already love, like ChatGPT or Claude—no technical setup required!

### 🖋️ **Asta: Your AI Writing Assistant**

Asta is your personal editor and content writer. She helps you craft beautiful blog posts, articles, and pages with ease in a clean, distraction-free writing space.

*   **Focus on Your Words**: Write in a simple, clean editor with a live preview, so you always know what your page will look like.
*   **Never Face a Blank Page Again**: Stuck for words? Click the magic button, and Asta prepares a perfect request for your favorite AI. Tell her your ideas in the "notes" section, and she'll help you ask the AI to write a first draft, brainstorm ideas, or polish your text.
*   **Real Time Editing**: Easily add images from your media library. Select text and ask AI to only edit that one specific text! 

---

### 🎨 **Aina: Your AI Website Designer**

Aina is the architect who builds and designs your website. Unlike other AI builders that just fill in a template, Aina is *smart*. She understands how your website works and can create pages that are not only beautiful but truly functional.

*   **Build Pages That *Do* Things**: Want a homepage that automatically shows your three latest blog posts? Just tell Aina. She’ll build it, connecting to your content without you lifting a finger.
*   **Create Your Vision**: Need a gorgeous gallery for your portfolio? A contact page that works? A unique layout for your services? Describe what you want, add some inspirational images, and Aina will generate the code.
*   **It Just Works**: Copy the code Aina creates, paste it into a new page, and publish. It’s that simple. She builds pages that are ready to go, live on your site.

> **In short: Aina builds the house. Asta writes the stories inside. You approve the final masterpiece.**

---

## 🧾 Forms: Your Secret Weapon for Creativity

This is where Anita’s real magic shines. The "Forms" tool isn't just for contact forms—it’s a simple way to create **any custom feature you can imagine, without writing a single line of code.**

When you create a form, Anita automatically builds a mini-database just for you, ready to be used by Aina.

#### **What could you build with this?**

*   **A Cafe Menu**: Create a "Menu Item" form with fields for a dish name, price, description, and photo. Aina can then design a beautiful, interactive menu page for your customers that pulls directly from your list.
*   **A Portfolio Gallery**: Make a "Project" form with fields for a title, image, and client details. Now you have an organized portfolio you can update anytime, and Aina can build a stunning gallery page to show it off.
*   **An Events Calendar**: Create an "Event" form with a date, location, and description. Aina can design a calendar page that automatically updates whenever you add a new event.

You can manage all your entries—menu items, portfolio pieces, events—from a simple table in your admin area. You can even **export your data as a spreadsheet** with one click.

**This is your key to a truly custom website, no developer needed.**

---

## 💡 Why Choose Anita?

Anita is for creative people who value simplicity, speed, and freedom.

### **Escape Subscription Hell** 💸

Stop paying $20, $30, or more every month for a website builder. Anita is **free, forever**. It runs so efficiently you can host it on a very cheap server (we're talking a few dollars a month) or even on a computer you have at home. You own your website, completely.

### **Focus on Your Craft, Not on Code** 🎨

You're an artist, a writer, a freelancer. Your time is better spent creating, not wrestling with confusing settings or code. Anita's AI team lets you describe what you want in plain English and makes it happen.

### **A Website That's Truly Yours** ✨

No more being stuck in a rigid template. Combine Aina's design skills with the magic of forms to build a site that perfectly reflects your brand and meets your unique needs. Your data is stored in simple files, so you're never locked in. You can pack up and leave anytime, taking all your content with you.

---

## 🚀 Getting Started is Easy

We’ve made it as simple as possible, especially for Windows users.

### 💻 **The Easiest Way (for Windows)**

1.  Download the **`anita_installer.bat`** file from our [Releases page](https://github.com/Iteranya/anita-cms/releases).
2.  Double-click the file. It will automatically handle the boring technical setup and create a new "ANITA" shortcut on your desktop.
3.  Click your new shortcut to start the magic!

That's it! Your personal website studio is ready.

<details>
<summary>For Mac/Linux or technical users (Manual Setup)</summary>

```bash
# We recommend using 'uv' for a fast installation
# Create and activate a virtual environment
python -m uv venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install the needed packages
uv pip install -r requirements.txt

# Copy the example environment file
cp example.env .env
# You'll need to open .env and add a secret key. You can generate one with:
# python -c "import secrets; print(secrets.token_hex(32))"
# and paste the result after JWT_SECRET=

# Run the app!
python main.py
```
</details>

### 🎮 **How to Use It**

1.  Once it's running, go to your website and add `/admin` to the end of the address (e.g., `http://127.0.0.1:8000/admin`).
2.  Start creating! Write a blog post with Asta, or ask Aina to design your homepage.
3.  Build a custom form to manage your portfolio, products, or anything else you dream up.
4.  Publish your work and share your amazing new site with the world.

---

## 🤗 You Can Help Shape Anita!

You don't need to be a programmer to contribute. We're building Anita for people like you, so your feedback is the most important thing to us!

```text
   ╭───────────────────────────╮
   │   YOUR IDEAS ARE WELCOME  │
   │        (.づ◡﹏◡)づ.        │
   ╰───────────────────────────╯
```

**Ways you can help:**

*   **Report Bugs**: If something doesn't work right, please [let us know by opening an issue](https://github.com/Iteranya/anita-cms/issues)! Describing the problem is a huge help.
*   **Suggest Ideas**: Is there a feature you wish Anita had? We'd love to hear it.
*   **Share Your Creations**: Show us the amazing websites you build!
*   **Spread the Word**: Tell a friend who's tired of paying for their website.
*   **Star the Repo**: Clicking the ⭐️ button at the top of the page helps more people discover Anita.

*(For the coders out there: Yes, we absolutely welcome your code contributions too!)*

---

## 📜 License

Anita is licensed under **AGPL-3.0**. This basically means it will always be free and open for everyone!
