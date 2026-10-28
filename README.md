# CareerBridge: Student Internship & Job Placement Portal

A full-stack web portal that connects students with internships and jobs. It uses a content-based recommendation engine to rank jobs for each student and shows exactly which skills match and which are missing.


![Dashboard](screenshots/dashboard.png)
![Job match score](screenshots/match-score.png)
![Mobile view](screenshots/mobile.png)

## Features

- **Smart job matching:** TF-IDF vectorisation and cosine similarity (scikit-learn), combined with a weighted skill-overlap score. Each job shows a match score with matched and missing skills.
- **Employer verification:** unverified job postings stay hidden from students until an administrator approves them (enforced at the database query level).
- **Role-based access control:** separate students, employers and administrators. Login with username or email.
- **Admin analytics dashboard:** placement rate, application status distribution and employer activity.
- **Application tracking:** one-click apply with a cover letter, and a status timeline (Submitted, Shortlisted, Accepted or Rejected).
- **In-app messaging:** private messaging between student and employer, scoped to each application (with soft-delete).
- **Student profiles and CV upload**, and **job search** with filters (type, keyword).
- **Mobile-responsive UI**, tested down to a 360px viewport.

## Tech Stack

Python, Django, scikit-learn, Tailwind CSS, JavaScript, HTML5, SQLite (local development), PostgreSQL (deployment). Gunicorn and WhiteNoise for serving.

## Run Locally

```bash
git clone https://github.com/derrick-amako/careerbridge.git
cd careerbridge
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000

## Demo Accounts (local demo data only)

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin1234` |
| Student | `chukwuemeka` | `password123` |
| Employer | `techcorp` | `password123` |

## Project Structure

```
accounts/          users, roles, authentication
jobs/              job postings, search, verification
applications/      applications, status tracking, messaging
dashboard/         admin analytics
ml/                recommendation engine (TF-IDF + cosine similarity)
placement_portal/  project settings
templates/         HTML templates
```

## Author

**Derrick Amako**, BSc Computer Science, Chrisland University.
[LinkedIn](https://www.linkedin.com/in/derrickamako)
