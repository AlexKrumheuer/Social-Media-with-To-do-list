
# Task & Friend Manager Web App

This is a full-stack web application built using **Flask (Python)** for the backend and **HTML/CSS/JavaScript** for the frontend. The platform allows users to manage personal tasks, maintain friendships, and communicate via a simple chat system.

---

## Features

### User Authentication
- Secure login and registration using password hashing
- **Forgot Password** and **Reset Password** functionality  
  **Note:** To enable the "Forgot Password" feature, you need to configure an email service.  
  This involves setting up an email account (e.g., Gmail) and generating an **App Password** or enabling "less secure app access" depending on your email provider.  
  You must add these email credentials (email address and app password) to your application's configuration so that password reset emails can be sent successfully.

### User Profile Management
- Edit firstname, lastname, username, and profile picture
- Manage user preferences

### Task Management
- Create, edit, and delete personal tasks
- Tasks are private and stored per user

### Friends System
- Send and accept friend requests
- View and manage friends list

### Messaging
- Real-time direct messaging with friends
- Chat interface with fetch-based message sending/receiving

---

## Tech Stack

### Backend
- **Python + Flask**
- SQLite (default, can be adapted)
- Jinja2 for templating

### Frontend
- HTML5
- CSS3 (custom styling)
- JavaScript (DOM manipulation and fetch API)

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. **Create a virtual environment (Windows):**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install the required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
