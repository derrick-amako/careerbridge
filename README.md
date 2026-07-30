# CareerBridge - Student Internship & Job Placement Portal
**Chrisland University, Abeokuta | Developer: Derrick Amako | Supervisor: Prof. Isaac Odun-Ayo**

---

## ▶ How to Run (3 steps)

### Step 1: Install Python dependencies
Open your terminal/command prompt and run:
```
pip install django scikit-learn numpy
```

### Step 2: Start the server
Navigate into the project folder and run:
```
cd careerbridge
python manage.py runserver
```

### Step 3: Open your browser
Go to: **http://127.0.0.1:8000**

That's it. The app is live.

---

## 🔑 Demo Accounts (already loaded, ready to use)

| Role | Username | Password |
|------|----------|----------|
| Career Services Admin | `admin` | `admin1234` |
| Student | `chukwuemeka` | `password123` |
| Student | `adaeze` | `password123` |
| Student | `tunde` | `password123` |
| Employer (TechCorp) | `techcorp` | `password123` |
| Employer (GTBank) | `gtbank` | `password123` |
| Employer (Andela) | `andela` | `password123` |

---

## ✅ Features
- Student registration, profile creation, CV upload
- Employer registration and job posting
- AI job matching (TF-IDF + Cosine Similarity via scikit-learn)
- Job search with filters (type, keyword)
- One-click job application with cover letter
- Application status timeline (Submitted → Shortlisted → Accepted/Rejected)
- In-app messaging between student and employer per application
- Employer application management dashboard (update status)
- Admin analytics dashboard (placement rates, charts, recent apps)

## 🛠 Tech Stack
Python · Django · scikit-learn · SQLite · HTML5 · Tailwind CSS · JavaScript
