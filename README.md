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

6. Open the [http://localhost:8000/admin](http://localhost:8000/admin). There you must:
- Open the 'Categories' model
- Add a single entry. For example: 'default'
- Save it.

This is done because making posts requires selecting a category of the post.

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

## App usage

### Login and registration

You can use the superuser you created to login into the app.

Or you can register a user with a different name and login as him.

### Log out 
You can log out by pressing 'log out' in the header. You will be redirected to the login page where you can login again.

### Posting
To make a new post choose a category from the dropdown, write something in a post form and click "Post"

### Post details
To look at the post details click on the post and a separate page wiht post details will open

### Commenting
To leave a comment, open the post you want to comment under and write the comment into the form in the lower part of the post and click 'Post'

### Liking
You can like a post by pressing the 'Like' button under it. You can also remove it by pressing 'unlike'.

### Updating a post
To update a post you need to be an owner of that post. To do it open the post, clik on the 'update' button. A new page will appear where you can choose a different category and write new text into the form. To save it click 'save'

### Deleting a post
To update a post you need to be an owner of that post. To do it open the post, clik on the 'delete' button. The post will be deleted an you will be returned to the main page.

---


## Known issues

### Session expiry
For some reason after around 10 minutes after login you are no longer authenticated and the API calls are unsuccessful. To solve it press 'log out' in the header and login again. Needs to be solved later.

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