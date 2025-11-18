# 🌳 GHG Protocol Emissions Calculator
🌳 *Enterprise GHG Protocol Emissions Calculator*
<img width="951" height="413" alt="ghg=register" src="https://github.com/user-attachments/assets/8005bea0-cf11-4f06-94b0-f6b1e81899ae" />

<img width="948" height="410" alt="ghg-activity" src="https://github.com/user-attachments/assets/402a82c7-505d-41fd-a7d8-7fd2e219b5dc" />

<img width="929" height="422" alt="ghg-Dashboard" src="https://github.com/user-attachments/assets/88a331b7-60d6-481a-92ef-218fb979e80d" />

<img width="943" height="421" alt="GHG-REPORTS" src="https://github.com/user-attachments/assets/92be0ab6-f566-47a7-8228-fc19a51c3175" />

<img width="1194" height="757" alt="Screenshot 2025-11-17 150251" src="https://github.com/user-attachments/assets/377d6e5a-e09c-4b5e-8c15-6a3806e7875b" />



1. Overview
 This project is a full-stack, enterprise-grade web application designed for sustainability managers to calculate, track, and report greenhouse gas (GHG) emissions. It strictly adheres to the GHG Protocol standards, covering Scope 1, Scope 2, and Scope 3 emissions.The application features a Python/Flask backend with a Pandas & Pint calculation engine for robust unit conversions, and a React frontend with Plotly visualizations and PDF/CSV reporting capabilities.
2. Features
   
 GHG Protocol Alignment: Categorizes data into Scope 1 (Direct), Scope 2 (Energy), and Scope 3 (Indirect).
Smart Calculation Engine: Automatically handles unit conversions (e.g., Gallons $\rightarrow$ Liters, MWh $\rightarrow$ kWh) before calculating CO₂e.Interactive Dashboard: Real-time visualization of emissions by scope and over time using Plotly.js.Reporting: Generate historical reports with date ranges and export data to PDF and CSV.Secure Authentication: JWT-based user authentication (Login/Register).Containerized: Fully Dockerized (Frontend, Backend, Database, Adminer) for consistent development and deployment.

4. Technology
StackFrontend: React.js, Formik, Axios, Plotly.js, jsPDF (for exports).Backend: Python 3.10, Flask, SQLAlchemy, Pandas, Pint.Database: PostgreSQL 15.Deployment: Docker, Docker Compose, Render (PaaS).4. Local Development (Docker Method)The easiest way to run this application is using Docker.PrerequisitesDocker and Docker Compose installed.
Step 1: ConfigurationNavigate to /backend.Copy .env.example to .env.Ensure DATABASE_URL is set to the internal Docker DNS:Code snippetDATABASE_URL=postgresql://ghg_user:ghg_password@db:5432/ghg_db
Step 2: Build and RunFrom the root directory, run:Bashdocker-compose up --build
Frontend: http://localhost:3000Backend API: http://localhost:5000Database GUI (Adminer): http://localhost:8080 (System: PostgreSQL, Server: db, User: ghg_user, Pass: ghg_password, DB: ghg_db)Step 3: Initialize Database (First Run Only)Open a new terminal window and run these commands to set up the database tables and seed data:Bash# 1. Create the migrations folder (if it doesn't exist)
docker-compose exec backend flask db init

# 2. Create the migration script
docker-compose exec backend flask db migrate -m "Initial setup"

# 3. Apply the migration (Create tables)
docker-compose exec backend flask db upgrade

# 4. Seed the database with emission factors
docker-compose exec backend flask seed_db
5. Deployment Guide (Render.com)

This application is configured for easy deployment on Render's free tier.5.1. Database (PostgreSQL)Create a new PostgreSQL database on Render.Copy the Internal Connection String (e.g., postgresql://user:pass@hostname/db).5.2. Backend (Web Service)Create a new Web Service connected to your repo.Root Directory: backendRuntime: Python 3Build Command:Bashpip install -r requirements.txt && flask db upgrade && flask seed_db
Start Command:Bashgunicorn run:app --bind 0.0.0.0:$PORT
Environment Variables:DATABASE_URL: (Paste connection string from Step 5.1)SECRET_KEY: (Any random string)PYTHON_VERSION: 3.10.13 (Required for Pandas compatibility)FLASK_APP: run.py5.3. Frontend (Static Site)Create a new Static Site connected to your repo.Root Directory: frontendBuild Command: npm run buildPublish Directory: buildRedirects/Rewrites (Crucial):Source: /api/* $\rightarrow$ Destination: https://your-backend.onrender.com/api/* $\rightarrow$ Action: RewriteSource: /auth/* $\rightarrow$ Destination: https://your-backend.onrender.com/auth/* $\rightarrow$ Action: RewriteSource: /* $\rightarrow$ Destination: /index.html $\rightarrow$ Action: Rewrite6. API EndpointsEndpointMethodDescriptionAuth/auth/registerPOSTRegister a new user./auth/loginPOSTLog in and retrieve JWT.Data/api/factorsGETGet emission factors (Scope 1, 2, 3)./api/inputsPOSTSubmit activity data (calculates CO₂e)./api/dashboard/summaryGETGet aggregated dashboard stats./api/reportsPOSTGenerate a new report.7. Troubleshooting502 Bad Gateway (Render): Ensure your Backend Start Command includes --bind 0.0.0.0:$PORT.Metadata Generation Failed (Pandas): Ensure PYTHON_VERSION is set to 3.10.13 on Render.Duplicate Key Error (500): If you manually inserted data, the SQL sequence might be out of sync. Run this SQL command:SQLSELECT setval('users_id_seq', (SELECT max(id) FROM users) + 1);
