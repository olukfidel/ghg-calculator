# 🌳 GHG Protocol Emissions Calculator

## 1. Overview

This project is an enterprise-grade, full-stack web application designed for sustainability managers to calculate greenhouse gas (GHG) emissions. It strictly adheres to the **GHG Protocol** standards, enabling the tracking, calculation, and reporting of emissions across **Scope 1**, **Scope 2**, and **Scope 3**.

Users can input various business activities (e.g., fuel consumption, electricity usage, employee travel), and the system calculates the corresponding emissions in metric tons of CO₂e (Carbon Dioxide Equivalent) using a robust, unit-aware calculation engine.

## 2. Features

* **GHG Protocol Alignment:** Data is categorized and calculated according to Scope 1, Scope 2, and Scope 3.
* **Comprehensive Dashboard:** Interactive visualizations (pie charts, line graphs) powered by Plotly.js to track emissions over time and by scope.
* **Unit-Aware Calculation:** A powerful backend engine using the Pint library handles unit conversions (e.g., gallons to liters, MWh to kWh) automatically.
* **Secure Authentication:** User accounts are protected by JWT (JSON Web Tokens).
* **Dynamic Data Entry:** Forms for inputting activity data, with dynamic dropdowns for emission factors.
* **Report Generation:** Create and view historical reports, with data exportable to CSV and PDF (planned).
* **Containerized Deployment:** Fully containerized with Docker and Docker Compose for reliable, reproducible deployment.

## 3. Technology Stack

* **Backend:** Python 3.10+, Flask, SQLAlchemy, Pandas, Pint
* **Database:** PostgreSQL 15
* **Frontend:** React.js, Formik, Axios, Plotly.js, React Router
* **Authentication:** JWT (PyJWT), Bcrypt
* **Testing:** Pytest
* **Deployment:** Docker, Docker Compose, Nginx (for serving React)

## 4. System Architecture

The application follows a standard monolithic repository (monorepo) structure, with a decoupled frontend and backend.



1.  **Frontend (React)**: The user interacts with the React application. It handles user login, data input (forms), and visualization (dashboard).
2.  **Backend (Flask API)**: The frontend communicates with a RESTful API built with Flask. This API handles authentication, data validation, and business logic.
3.  **Calculation Engine (Services)**: A dedicated service layer uses Pandas and Pint to perform the core emissions calculations, including complex unit conversions.
4.  **Database (PostgreSQL)**: All data (users, factors, inputs, reports) is stored in a PostgreSQL database, managed by the SQLAlchemy ORM.

## 5. Local Development Setup

### Prerequisites

* Python 3.10+ and `pip`
* Node.js 18+ and `npm`
* PostgreSQL 15 (running locally or via Docker)

### Backend Setup

1.  **Clone the repository.**
2.  **Navigate to the backend directory:**
    ```bash
    cd ghg-calculator/backend
    ```
3.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Set up environment variables:**
    * Copy `.env.example` to `.env`.
    * Edit `.env` and set your `DATABASE_URL` and `SECRET_KEY`.
    ```
    # Example DATABASE_URL
    DATABASE_URL=postgresql://user:password@localhost:5432/ghg_db
    ```
6.  **Initialize and migrate the database:**
    ```bash
    # Ensure you have Flask-Migrate (it's in requirements.txt)
    flask db init  # (Only if migrations folder doesn't exist)
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```
7.  **Seed the database with emission factors:**
    ```bash
    flask seed_db
    ```
8.  **Run the backend server:**
    ```bash
    flask run
    # Server will run on [http://127.0.0.1:5000](http://127.0.0.1:5000)
    ```

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd ghg-calculator/frontend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Set up environment variables:**
    * Copy `.env.example` to `.env`.
    * The default `REACT_APP_API_URL` should work with the `setupProxy.js` file.
4.  **Run the frontend server:**
    ```bash
    npm start
    # App will open on http://localhost:3000
    ```

## 6. Docker Deployment

This is the recommended method for a production-like environment.

1.  **Ensure Docker and Docker Compose are installed.**
2.  **Set up environment variables:**
    * In `/backend`, copy `.env.example` to `.env`.
    * Make sure the `DATABASE_URL` in `backend/.env` points to the Docker service name:
        ```
        DATABASE_URL=postgresql://ghg_user:ghg_password@db:5432/ghg_db
        ```
    * Set a strong `SECRET_KEY`.
3.  **From the root `ghg-calculator` directory, build and run the services:**
    ```bash
    docker-compose up --build -d
    ```
4.  **Services:**
    * **Frontend:** `http://localhost:3000`
    * **Backend API:** `http://localhost:5000`
    * **Database Admin (Adminer):** `http://localhost:8080`

5.  **To run database seeding (after `up`):**
    ```bash
    docker-compose exec backend flask seed_db
    ```

6.  **To shut down:**
    ```bash
    docker-compose down -v
    ```

## 7. API Documentation

All endpoints prefixed with `/api` require a valid `Authorization: Bearer <JWT>` header.

| Endpoint | Method | Protected | Description | Payload / Query |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | | | | |
| `/auth/register` | `POST` | No | Register a new user. | `{username, email, password, company_name}` |
| `/auth/login` | `POST` | No | Authenticate and get a JWT. | `{email, password}` |
| **Emission Factors** | | | | |
| `/api/factors` | `GET` | Yes | Get a list of all emission factors. | N/A |
| `/api/factors` | `POST` | Yes (Admin) | Add a new emission factor. | `{name, category, scope, factor_value, ...}` |
| **Data Input** | | | | |
| `/api/inputs` | `POST` | Yes | Submit a new activity and calculate emissions. | `{factor_id, activity_value, activity_unit, date_period_start}` |
| `/api/inputs` | `GET` | Yes | Get historical activity inputs (paginated). | `?page=1&per_page=20` |
| **Reporting** | | | | |
| `/api/dashboard/summary` | `GET` | Yes | Get data for the dashboard (scope totals, time series). | N/A |
| `/api/reports` | `POST` | Yes | Generate a new summary report for a date range. | `{report_name, start_date, end_date}` |
| `/api/reports` | `GET` | Yes | Get a list of past generated reports. | N/A |
| `/api/reports/<id>` | `GET` | Yes | Get details for a specific report. | N/A |