# Cygree

Cygree is a Django-based backend for managing the collection and recycling of plastic waste. This system helps users reduce plastic usage by offering incentives such as gift coupons or offers based on the amount of plastic they recycle.

## Features
- User registration and login system
- Plastic collection tracking
- Incentive-based system for recycling
- Backend powered by Django

## Setup Instructions

### Prerequisites
Ensure you have the following installed:
- [Python 3.x](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)

### Step 1: Change current directory

Assuming you are already in cygree repo
```bash
cd CyGree-Backend
```

### Step 2: Create a Virtual Environment

Create a virtual environment to isolate your project dependencies.

```bash
python -m venv venv
```

Activate the virtual environment:

- On Windows:
  ```bash
  venv\Scripts\activate
  ```

- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### Step 3: Install Dependencies

Make sure you are in the project directory and install the required packages:

```bash
pip install -r requirements.txt
```

### Step 4: Apply Migrations

Before running the project, apply the necessary migrations:

```bash
python manage.py migrate
```

### Step 5: Create a Superuser (Optional)

To access the Django admin panel, create a superuser account:

```bash
python manage.py createsuperuser
```

### Step 6: Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

You can now access the project at `http://127.0.0.1:8000/`.

## Contribution

Feel free to submit issues or pull requests to help improve this project.

## License

This project is licensed under the MIT License.
