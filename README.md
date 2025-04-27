# CollabToDo

CollabToDo is a real-time collaborative task management application built using Django, Django Channels, HTMX, Tailwind CSS, and WebSockets.  
It allows small teams to manage tasks together with live updates, team invites, and a clean, responsive UI.

---

## Features

- Create and manage teams
- Invite users to join teams
- Create, assign, and update tasks
- Real-time updates using WebSockets
- Mobile-friendly design with Tailwind CSS
- Secure user authentication

---

## Setup Instructions

Follow these steps to run CollabToDo locally:

### 1. Clone the Repository

```bash
git clone https://github.com/silt/collabtodo.git
cd collabtodo
```

### 2. Set Up a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install Django>=5.1,<5.2 channels>=4.0,<5.0 daphne>=4.0,<5.0 asgiref>=3.7,<4.0 django-tailwind>=3.5,<4.0 django-browser-reload>=1.11,<2.0
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Collect Static Files (optional for production)

```bash
python manage.py collectstatic
```

### 6. Run the Server

Since the application uses WebSockets (Django Channels), you must run the server using Daphne instead of Django's default development server:

```bash
daphne collabtodo.asgi:application
```

This will start the server at:

```
http://127.0.0.1:8000/
```
