# 📘 SmartStudy AI — Student Productivity & Learning System

Simple, working version — Login/Signup, Dashboard, Study Planner, Subjects,
Notes, Tasks/Goals, Progress Analytics, Weak-Subject detection, aur AI
Study Assistant, sab kaam kar rahe hain.

Ye version **XAMPP ka MySQL** use karta hai (SQLite nahi) aur API key
seedha code ke andar ek jagah paste karni hoti hai — demo/college-project
style, taake aap sirf 2 cheezein daal kar turant chala saken.

---

## 🟢 Step 1 — XAMPP start karein

1. XAMPP Control Panel kholein.
2. **Apache** aur **MySQL** dono ko **Start** karein.
3. Browser mein `http://localhost/phpmyadmin` kholein.
4. "New" par click karein → database ka naam type karein: **`smartstudy`**
   → Create.
   (Bas khali database banani hai, andar tables khud ban jaayenge —
   app pehli baar run hote hi automatically bana deta hai.)

---

## 🟢 Step 2 — Project setup karein

```bash
cd smartstudy
python3 -m venv venv
source venv/bin/activate        # Windows par: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🟢 Step 3 — `app.py` ke top par apni values daalein

`app.py` file kholein, sabse upar ek `CONFIG` section milega:

```python
OPENAI_API_KEY = "PASTE-YOUR-OPENAI-API-KEY-HERE"

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = ""            # XAMPP mein default khali hota hai
MYSQL_DATABASE = "smartstudy"
```

- **OPENAI_API_KEY** → apni OpenAI key yahan paste karein (quotes ke andar).
  Agar key nahi dalni to yun hi rehne dein — app khud fallback advice dega,
  crash nahi hoga.
- **MYSQL_...** values agar aapne XAMPP standard tareeke se install kiya
  hai (username `root`, password khali) to inhe change karne ki zaroorat
  **nahi** — bas database ka naam `smartstudy` hi match hona chahiye jo
  Step 1 mein banaya tha.

---

## 🟢 Step 4 — App run karein

```bash
python3 app.py
```

Browser mein kholein: **http://localhost:5000**

Pehli dafa run hote hi Flask, XAMPP ke `smartstudy` database ke andar
saari tables (User, Subject, Note, Task, StudyPlan) khud bana lega —
aapko manually kuch banana nahi.

---

## 🧠 Ye kaam kaise karta hai — poori samajh

**1. Architecture (structure):**
```
Browser (HTML/CSS/JS)  ⇄  Flask (app.py)  ⇄  XAMPP MySQL Database
```
- Jo bhi page dikhta hai (Dashboard, Notes, wagera) wo `templates/`
  folder ki HTML files hain — Flask unhe data ke sath bhar (fill) kar
  browser ko bhejta hai (isko "Jinja2 templating" kehte hain).
- `static/style.css` aur `static/script.js` sirf design aur chhoti
  interactivity ke liye hain.

**2. Login/Signup kaise kaam karta hai:**
- Signup form se name/email/password aata hai → password ko
  `werkzeug.security` se hash (encrypt jaisa) karke MySQL ke `user`
  table mein save kiya jaata hai — plain password kabhi save nahi hota.
- Login par password match check hota hai, sahi hone par
  `session['user_id']` set hota hai — yehi session batata hai ke user
  logged in hai, jab tak Logout na kare.

**3. Subjects, Notes, Tasks, Planner:**
- Ye sab simple **CRUD** hain (Create, Read, Update, Delete) — form
  submit hota hai → Flask route us data ko MySQL table mein insert/
  update/delete karta hai → page refresh hoke naya data dikhata hai.
- Har cheez (`Subject`, `Note`, `Task`, `StudyPlan`) `app.py` mein ek
  Python class ("model") hai jo seedha MySQL table se map hoti hai —
  aapko khud SQL likhne ki zaroorat nahi, SQLAlchemy ye kaam karta hai.

**4. Weak Subject Detection (AI-jaisi analytics, bina API ke):**
- Har subject ke liye ek **score (0–100)** calculate hota hai:
  - 60% weight → us subject ke tasks kitne % complete huye
  - 40% weight → aapne subject add karte waqt jo "confidence" (1–5)
    diya tha
- Sabse **kam score** wale subjects = weak subjects → Dashboard aur
  Analytics page par sabse upar dikhte hain.

**5. AI Study Assistant:**
- Agar aapne real `OPENAI_API_KEY` daali hai → sawaal + aapke weak
  subjects ka context OpenAI ko bheja jaata hai, wahan se personalized
  jawab aata hai.
- Agar key nahi daali (placeholder wahi rehne diya) → app khud
  built-in rule-based jawab deta hai (weak subject ke naam ke sath
  study tips) — is se app kabhi crash nahi hota, sirf jawab simple
  hota hai.

**6. Motivational Quotes:**
- Koi external API use nahi ki — 10 quotes ki list code mein hi hai,
  Dashboard har baar random ek dikhata hai.

---

## 📁 Project Structure

```
smartstudy/
  app.py                 # Sara backend logic: routes, database models,
                          # weak-subject calculation, AI helper — CONFIG top par
  requirements.txt
  templates/              # HTML pages (login, dashboard, notes, tasks, etc.)
  static/
    style.css
    script.js
```

---

## ⚠️ Agar error aaye

- **"Can't connect to MySQL"** → XAMPP mein MySQL service start hai ya
  nahi check karein.
- **"Unknown database 'smartstudy'"** → phpMyAdmin mein database banana
  bhool gaye — Step 1 dobara karein.
- **"No module named 'pymysql'"** → `pip install -r requirements.txt`
  dobara chalayein.

---

## 🔮 Aage add ho sakta hai (optional, is version mein nahi)

- Google Calendar API integration
- OpenWeather API
- Charts (Chart.js) analytics ke liye visual graphs
