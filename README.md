# Gym Management System

A Django web application to manage a gym. It has an admin side for gym staff and a member side where members can view their own details.

## Technologies Used
- Python 3.11
- Django 5.2
- SQLite
- HTML, CSS, JavaScript

## Features

**Admin**
- Login and change password
- Manage members, plans and equipment
- Manage enquiries and contact messages
- Mark attendance and record payments
- Income report

**Member**
- Login
- Dashboard with plan, visits and payment summary
- View attendance and payment history
- View plan details and equipment list
- Send a message to the gym
- Edit profile and change password

## How to Run

1. Install Django:
   ```
   pip install django
   ```
2. Set up the database:
   ```
   python manage.py makemigrations gym
   python manage.py migrate
   ```
3. Create an admin user:
   ```
   python manage.py createsuperuser
   ```
4. Start the server:
   ```
   python manage.py runserver
   ```
5. Open http://127.0.0.1:8000/ in the browser.

## Login Pages
- Admin: `/admin_login`
- Member: `/member_login`
