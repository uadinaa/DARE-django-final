# Training Social Platform

This project includes an Angular frontend and a Django backend.

## 📥 Prerequisites

Ensure the following are installed:

- Python (≥ 3.10)
- Node.js (≥ 18.x) & npm
- Angular CLI: `npm install -g @angular/cli`
- Git

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/uadinaa/DARE-django-final.git
```

### 2. Backend (Django)

1. Go into the backend folder:
    ```bash
    cd backend
    ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

5. Run the Django server:
   ```bash
   python manage.py runserver
   ```

Django is now running at: [http://localhost:8000](http://localhost:8000).

Now open a new terminal window and proceed with frontend setup.

---

### 3. Frontend (Angular)

1. Navigate to the Angular directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Run the Angular development server:
   ```bash
   ng serve
   ```

Angular is now running at: [http://localhost:4200](http://localhost:4200)

---

## 🧹 Cleanup & Deactivation

- Stop servers: `CTRL + C`
- Deactivate virtual environment:
  ```bash
  deactivate
  ```

---

## 📋 **4. Keep Requirements Updated**
When you add new packages:

1. **Django**:  
   After installing a new package, update the `requirements.txt`:
   ```bash
   pip freeze > requirements.txt
   ```

2. **Angular**:  
   Ensure `package.json` and `package-lock.json` are committed after:
   ```bash
   npm install package-name --save
   ```