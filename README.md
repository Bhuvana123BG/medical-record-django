# 🩺 Medical Record Management System (Django)

A Django-based web application to manage patient medical records securely and efficiently.

## 🚀 Features

- User registration and login
- Add, view, edit, and delete medical records
- Group records by doctor
- Prescription PDF uploads (stored via Supabase)
- Automatic summary generation of prescriptions using a ML model
- Profile page with user details
- Disease prediction from symptoms
- Search and filter records
- Responsive Bootstrap UI with dark mode and sidebar navigation

## 🛠 Tech Stack

- **Backend**: Django 5.2.3
- **Frontend**: HTML, CSS, Bootstrap (Dark UI)
- **Database**: MySQL
- **File Storage**: Supabase Storage
- **ML Model**: BART (Hugging Face - for summarization)

## 📦 Setup Instructions

```bash
git clone https://github.com/Bhuvana123BG/medical-record-django.git
cd medical-record-django
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env 
python manage.py migrate
python manage.py runserver
