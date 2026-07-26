# 📘 SmartStudy AI — Student Productivity & Learning System

SmartStudy AI is a full-stack web application designed to help students manage their studies efficiently. It includes features like task management, subject tracking, notes, study planning, progress analytics, weak subject detection, and an AI-powered study assistant.

---

## 🚀 Features

* 🔐 User Authentication (Login/Signup)
* 📊 Dashboard with analytics
* 📚 Subject Management
* 📝 Notes System
* ✅ Tasks & Goals Tracking
* 📅 Study Planner
* 📉 Weak Subject Detection
* 🤖 AI Study Assistant (OpenAI API)
* 💡 Motivational Quotes

---

## 🛠 Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Python (Flask)
* **Database:** MySQL (XAMPP)
* **ORM:** SQLAlchemy
* **AI Integration:** OpenAI API

---

## ⚙️ Installation & Setup

### 1. Start XAMPP

* Open XAMPP Control Panel
* Start **Apache** and **MySQL**
* Open: http://localhost/phpmyadmin
* Create a new database named: `smartstudy`

---

### 2. Setup Project

```bash
cd smartstudy
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### 3. Configure `app.py`

```python
OPENAI_API_KEY = "YOUR_API_KEY"

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DATABASE = "smartstudy"
```

---

### 4. Run Application

```bash
python3 app.py
```

Open in browser:
👉 http://localhost:5000

---

## 🧠 System Architecture

```
Frontend (HTML/CSS/JS)
        ⇅
Flask Backend (app.py)
        ⇅
MySQL Database (XAMPP)
```

---

## 🔑 How It Works

### Authentication

* Passwords are securely hashed using `werkzeug.security`
* Sessions are used to maintain login state

### CRUD Operations

* Subjects, Notes, Tasks, Study Plans are fully dynamic
* Data is stored and managed using SQLAlchemy

### Weak Subject Detection

* Score = (60% task completion + 40% confidence level)
* Lowest scoring subjects are marked as weak

### AI Assistant

* Uses OpenAI API for personalised study help
* If API key is missing, fallback responses are used

---

## 📁 Project Structure

```
smartstudy/
│── app.py
│── requirements.txt
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── notes.html
│   ├── tasks.html
│
└── static/
    ├── style.css
    ├── script.js
```

---

## ⚠️ Common Errors

* MySQL not running → Start from XAMPP
* Database not found → Create `smartstudy` in phpMyAdmin
* Missing modules → Run `pip install -r requirements.txt`

---

## 🔮 Future Improvements

* Google Calendar Integration
* Weather API
* Graphs using Chart.js
* Mobile Responsive UI Enhancements

---

## 👨‍💻 Author

Zohaib Nawaz
BSCS Student | Aspiring Full Stack Developer

---

## ⭐ Project Status

✔ Completed (MVP Version)
🚧 Future enhancements planned

---

## 📌 Note

This project is built for learning and academic purposes. It demonstrates full-stack development with AI integration and database handling.
