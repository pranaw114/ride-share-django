# Ride Sharing – Django

A ride‑sharing backend system built with Django and Django REST Framework. It supports riders creating ride requests, drivers accepting and tracking rides, and basic matching logic.

## Features

- Rider & driver signup / signin  
- Ride creation and management  
- Ride status updates  
- Driver location updates & real‑time tracking simulation  
- Nearest‑driver matching logic  
- Test coverage for models and API endpoints  

---

## Setup Instructions

1. **Clone the repository**  
   ```bash
   
   git clone https://github.com/pranaw114/ride-share-django.git
   cd rideshare

2. **Create and activate a virtual environment**
   ```bash
   
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**
   ```bash
   
   pip install -r requirements.txt

4. **Apply migrations**
   ```bash
   Apply migrations

5. **Run the server**
   ```bash
   
   python manage.py runserver

6. **Run tests**
   ```bash
   
   python manage.py test

## API Endpoints
### Authentication
- **POST** `/register` – Register a new user
- POST /login – User signin
### Ride
- **POST** `/create-ride-request` – Create ride request
- **GET** `/list-rides` – List rides
- **GET** `/ride-details/<int:id>/` – Get ride details
- **PATCH** `/update-ride-status/<int:pk>` – Update ride status
- **POST** `/update-location` – Update current location of a driver on a ride
- **POST** `/find-driver` – Find a driver to ride
- **POST** `/accept-ride/<int:pk>` – Driver accepts ride 


