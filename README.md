# 📘 SmartStudy AI

**Student Productivity & Learning System** — a lightweight web app that helps students plan their study time, track subjects and tasks, spot their weak areas, and get AI-powered study advice.

Built as a simple, self-contained project: no heavy frameworks, no paid infrastructure required — just Python, Flask, and MySQL (via XAMPP).

---

## ✨ Features

- 🔐 **Student Login / Signup** — secure password hashing (Werkzeug)
- 📊 **Personal Study Dashboard** — progress %, today's plan, today's tasks, weak subjects, at a glance
- 📅 **Daily Study Planner** — schedule study slots per date/time
- 📚 **Subjects Management** — add subjects with a self-rated confidence level
- 📝 **Notes / Learning Material** — save notes, optionally linked to a subject
- ✅ **Tasks & Goals Tracking** — due dates, subject linking, mark done/goal
- 📈 **Progress Analytics** — subject-wise completion table + overall progress bar
- ⚠️ **Weak Subject Detection** — automatic scoring based on task completion + confidence
- 🤖 **AI Study Assistant** — powered by the OpenAI API, with a built-in fallback so it always works, even without a key
- 💬 **Motivational Quotes** — built-in quote list on the dashboard, no external API needed

> Google Calendar and OpenWeather integration are left as optional future additions (see [Roadmap](#-roadmap)).

---

## 🧱 Tech Stack

| Layer      | Technology                                  |
|------------|----------------------------------------------|
| Frontend   | HTML, CSS, JavaScript (Jinja2 templates)     |
| Backend    | Python, Flask                                |
| Database   | MySQL (via XAMPP), Flask-SQLAlchemy ORM      |
| AI         | OpenAI API (optional, with local fallback)   |
| Auth       | Flask sessions + Werkzeug password hashing   |

---

## 📂 Project Structure

```
smartstudy/
├── app.py                # Flask app: config, models, routes, business logic
├── requirements.txt      # Python dependencies
├── templates/            # Jinja2 HTML pages
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── subjects.html
│   ├── notes.html
│   ├── tasks.html
│   ├── planner.html
│   ├── analytics.html
│   └── ai_assistant.html
└── static/
    ├── style.css
    └── script.js
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- [XAMPP](https://www.apachefriends.org/) (for MySQL + phpMyAdmin)
- An OpenAI API key *(optional — the app works without one)*

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/smartstudy-ai.git
cd smartstudy-ai/smartstudy
```

### 2. Start XAMPP and create the database

1. Open the XAMPP Control Panel and start **Apache** and **MySQL**.
2. Go to `http://localhost/phpmyadmin`.
3. Click **New** → name the database **`smartstudy`** → **Create**.

Tables are created automatically the first time the app runs — no manual SQL needed.

### 3. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure the app

Open `app.py` — the `CONFIG` section at the top is the only place you need to edit:

```python
OPENAI_API_KEY = "PASTE-YOUR-OPENAI-API-KEY-HERE"

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = ""            # XAMPP default is empty
MYSQL_DATABASE = "smartstudy"
```

- Paste a real OpenAI key to enable AI-generated answers, or leave the placeholder to use the built-in fallback assistant.
- Default MySQL values match a standard XAMPP install — only change them if your setup differs.

### 5. Run the app

```bash
python3 app.py
```

Open **http://localhost:5000** in your browser and sign up for a new account.

---

## 🧠 How It Works

**Architecture**

```
Browser (HTML/CSS/JS)  ⇄  Flask (app.py)  ⇄  MySQL (XAMPP)
```

- Every page (`Dashboard`, `Notes`, `Tasks`, etc.) is a Jinja2 template in `templates/`, rendered by a Flask route with the relevant data.
- `static/style.css` and `static/script.js` handle styling and small client-side behavior (like auto-dismissing flash messages).

**Authentication**

Signup hashes the password with `werkzeug.security` before storing it — plaintext passwords are never saved. Login checks the hash and stores `user_id` in the session; every protected route checks that session before rendering.

**Core data model**

`Subject`, `Note`, `Task`, and `StudyPlan` are SQLAlchemy models mapped directly to MySQL tables. All create/update/delete actions go through standard Flask routes and forms — no manual SQL required.

**Weak Subject Detection**

Each subject gets a score from 0–100:

```
score = (task completion rate × 60%) + (self-rated confidence × 20 × 40%)
```

Subjects with the lowest scores are flagged as "weak" and surfaced on the Dashboard and Analytics page.

**AI Study Assistant**

If a real `OPENAI_API_KEY` is set, the assistant sends your question plus your current weak-subject context to OpenAI for a personalized answer. If no key is set, it falls back to built-in rule-based advice — the feature never crashes or blocks the rest of the app.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `Can't connect to MySQL` | Make sure MySQL is running in the XAMPP Control Panel |
| `Unknown database 'smartstudy'` | Create the database in phpMyAdmin (see Step 2) |
| `No module named 'pymysql'` | Re-run `pip install -r requirements.txt` |

---

## 🗺️ Roadmap

- [ ] Google Calendar API integration (sync the planner)
- [ ] OpenWeather API (study-environment suggestions)
- [ ] Chart.js visual analytics
- [ ] Email/notification reminders for due tasks

---

## 🤝 Contributing

Contributions are welcome. Fork the repo, create a feature branch, and open a pull request.

## 📄 License

This project is open source and available for personal or educational use.
