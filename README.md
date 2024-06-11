# SmartLight Control System

## Overview

This project implements an intelligent lighting control system using artificial intelligence. The system includes a cloud-based web application, a PostgreSQL database, and integration with Home Assistant for managing lighting devices. Users can control the brightness, color, and state of their lights through the application. The system also collects user data to train AI models for automating lighting control based on user behavior patterns.

## Features

- User authentication and profile management
- Integration with Home Assistant for controlling smart lights
- Data collection of user interactions for AI model training
- AI-driven predictions for automated lighting control
- Web-based interface for managing lighting devices

## Technologies Used

- **Backend**: Django, PostgreSQL
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **AI/ML**: XGBoost, RandomForestRegressor
- **Integration**: Home Assistant API, Nabu Casa cloud service

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Home Assistant setup with Nabu Casa subscription

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/nillovych/SmartLight-Control-System.git
   cd SmartLight-Control-System
   ```

2. **Set up the virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. **Install the dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure PostgreSQL**
   - Create a PostgreSQL database and user
   - Update `settings.py` with your database credentials

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```
   
6. **Run the server**
   ```bash
   python manage.py runserver
   ```

## Usage

1. **Register and log in**
   Create an account and log in to access the lighting control interface.

2. **Connect to Home Assistant**
   Enter your Home Assistant domain and long-lived access token in the profile settings.

3. **Manage lights**
   View and control your connected lights from the main dashboard. Adjust brightness, color, and state.

4. **Enable data collection**
   Opt-in to data collection to allow the system to record your interactions and train AI models.

5. **Train AI model**
   Once sufficient data is collected, train an AI model to automate lighting control based on your behavior.

## Contributing

1. **Fork the repository**
2. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a pull request**

## Contact

For any inquiries or feedback, please contact [danykyurkevych@gmail.com].
