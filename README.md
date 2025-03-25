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

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the Django server:
   ```bash
   python manage.py runserver
   ```

Django is now running at: [http://localhost:8000](http://localhost:8000).

7. Configure Categories:

   Access the Django admin panel to set up a category:

   1. Open [http://localhost:8000/admin](http://localhost:8000/admin) in your browser.
   2. Log in using the superuser credentials.
   3. Navigate to the **Categories** section.
   4. Add a new category (e.g., **"default"**) and save it.

   > **Note:** This is necessary because creating posts requires selecting a category. Ensure **at least one category** exists before proceeding.

8. **Proceed to Frontend Setup**:

   Open a new terminal window and follow the instructions for setting up the frontend.

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

## App Usage

### Login and Registration

- **Login with Superuser**: Use the superuser credentials you created during setup to log in.
- **Register a New User**: If you prefer, you can register a new user with a unique username and password and log in using those credentials.

### Logout

- To log out, click the **"Log Out"** button in the header. You will be redirected to the login page where you can log in again if needed.

### Posting

- **Create a New Post**: Select a category from the dropdown menu, enter your content in the post form, and click **"Post"** to submit it.

### Post Details

- **View Post Details**: Click on any post to open a dedicated page displaying the post's full details.

### Commenting

- **Add a Comment**: Open the post you want to comment on, write your comment in the input field at the bottom of the post, and click **"Post"** to submit it.

### Liking

- **Like a Post**: Click the **"Like"** button below a post to like it.
- **Unlike a Post**: If you've already liked a post, you can click **"Unlike"** to remove your like.

### Updating a Post

- **Edit Your Post**: You can only update posts that you own.
  1. Open the post you want to update.
  2. Click the **"Update"** button.
  3. On the new page, you can choose a different category and edit the post content.
  4. Click **"Save"** to update the post.

### Deleting a Post

- **Remove Your Post**: You can only delete posts that you own.
  1. Open the post you want to delete.
  2. Click the **"Delete"** button.
  3. The post will be permanently removed, and you will be redirected to the main page.

---

## Known Issues

### Session Expiry

- **Issue**: After approximately 10 minutes, your authentication may expire, causing API calls to fail.
- **Temporary Solution**: Click **"Log Out"** in the header and log back in to restore access.

> This issue requires further investigation and a permanent fix in future updates.

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