# **PROJECT SPECIFICATION: MAIL CLIENT (SPA)**

---

# **A. PROJECT OVERVIEW**

* **App Name**: Mail
* **Project Structure**: Django project with a single application (mail).
* **Core Architecture**: Single-Page Application (SPA).
* **Primary Technologies**: Django (Backend), JavaScript, Bootstrap (Frontend).

---

# **B. GETTING STARTED**

1. Download the distribution code from https://cdn.cs50.net/web/2020/spring/projects/3/mail.zip and unzip it.
2. In your terminal, `cd` into the `mail` directory.
3. Make migrations for the `mail` app
```bash
python manage.py makemigrations mail
```
4. Apply migrations to your database
```bash
python manage.py migrate
```
5. Start the web server
```bash
python manage.py runserver.
```

---

# **C. UNDERSTANDING**
## **I. USER INTERFACE STRUCTURE (HTML)**
The application operates on a single template: `mail/inbox.html`. It contains the following key elements:

### **1. Navigation Header**
* Displays the user's email address in an `<h2>` element.
* Provides a sequence of buttons to toggle between various application views.
    * `Inbox`
    * `Compose`
    * `Sent`
    * `Archived`
    * `Log out`

### **2. View Containers (DIVs)**
The interface is divided into two primary sections controlled by JavaScript:
* `emails-view`: Container for mailbox content (initially empty).
* `compose-view`: Container for the email composition form.

---

## **II. FUNCTIONAL SPECIFICATIONS (JAVASCRIPT)**
All client-side logic is handled by `mail/static/mail/inbox.js`.

### **1. Event Handling**
* Listeners are attached to buttons upon `DOMContentLoaded`.
* Navigation is handled by selectively showing and hiding `div` elements via the `style.display` property (`block` vs `none`).

### **2. View: Compose Email (`compose_email`)**
* **Visibility**: Hides `emails-view`, shows `compose-view`.
* **Data Reset**: Clears all input fields (`recipients`, `subject`, `body`) to an empty string `''` every time the view is accessed.

### **3. View: Load Mailbox (`load_mailbox`)**
* **Visibility**: Shows `emails-view`, hides `compose-view`.
* **Parameters**: Accepts an argument: `inbox`, `sent`, or `archive`.
* **UI Update**: Updates the `innerHTML` of `#emails-view` to display the capitalized name of the active mailbox.

### **4. User Registration**
* **Data Integrity**: All emails are stored entirely in the local database. Real-world email credentials are not required; any email format (e.g., `foo@example.com`) is acceptable.

---

## **III. TECHNICAL CONSTRAINTS & REQUIREMENTS**
* **No Page Reloads**: Switching between `Inbox`, `Sent`, `Archive`, and `Compose` **must not** trigger a **new route** or a **full web request**.
* **State Management**: JavaScript is responsible for controlling the user interface and clearing form data.

---

## **IV. PENDING IMPLEMENTATIONS (TODO)**
The current distribution code is a skeleton. The following logic must be developed:

* **Mailbox Population**: Fetch and display **actual emails** in the `emails-view`.
* **Email Detail View**: Create a mechanism to see the full content of an email.
* **Mail Submission**: Implement the "Send" logic to handle form submissions via the API.

---

# **D. API**
https://cs50.harvard.edu/web/projects/3/mail/#api

---

# **E. SPECIFICATION**
https://cs50.harvard.edu/web/projects/3/mail/#specification
