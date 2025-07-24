# Task & Friend Manager Web App

This is a full-stack web application built using **Flask (Python)** for the backend and **HTML/CSS/JavaScript** for the frontend. The platform allows users to manage personal tasks, maintain friendships, and communicate via a simple chat system.

---

## Features

### User Authentication
- Secure login and registration using password hashing
- "Forgot Password" and "Reset Password" functionality

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

- ## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name

 2. **Create a virtual environment (Windows)
    ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

   3. **Install the required Python packages
   ```bash
   pip install -r requirements.txt
   ```

   4. And finally, to run the application
   ```bash
   python app.py
   ```
