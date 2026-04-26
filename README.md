# Paw-Gress | Gamified Productivity Engine

Paw-Gress is a full-stack, multi-user productivity platform built to bridge the gap between task management and habit formation through gamification. Unlike standard habit trackers, this system implements a real-time state machine for pet evolution and rigorous database-level security.

## 🏗 System Architecture

The application is built on a "Lean Frontend - Heavy Security" model:

*   **Logic Layer**: Python-based state management handling the pet life cycle, hunger decay, and xp-scaling.
*   **Database**: PostgreSQL (via Supabase) with Row Level Security (RLS) policies enforced.
*   **Security Protocol**: Adaptive JWT injection. The system utilizes an internal switching mechanism that elevates client privileges based on authentication state, ensuring 1:1 data isolation.

## 🛠 Technical Implementation

### Core Modules
- **State Controller (`models/user.py`)**: Manages the transitions between pet stages (Egg, Baby, teen, Adult) and calculates decay based on timestamp differentials.
- **Database Engine (`database.py`)**: A session-aware middleware that handles authenticated persistent clients.
- **Auth Flow (`auth.py`)**: Custom OTP-based verification system with SMTP integration.

### Security Highlights
This project solves the "Direct API Access" vulnerability by moving security from the application layer to the database layer. 
- **RLS Enforcement**: SQL Policies ensure `auth.uid() = user_id`.
- **Credential Management**: Full environment variable isolation via `.env` and Streamlit Secrets.

## 💻 Local Development

### Configuration
1.  Initialize a Python virtual environment.
2.  Install dependencies: `pip install -r requirements.txt`.
3.  Configure `.env` with the following schema:
    ```ini
    SUPABASE_URL=...
    SUPABASE_KEY=...
    SUPABASE_SERVICE_KEY=...
    GMAIL_EMAIL=...
    GMAIL_APP_PASSWORD=...
    ```

### Execution
```bash
streamlit run app.py
```

## ⚙️ Project Structure
```text
├── app.py                # Main Entry Point & Routing
├── auth.py               # Authentication Controller (Login/Signup/OTP)
├── database.py           # Secure Database Layer (Supabase + RLS Logic)
├── config.py             # Global Constants & Asset Pathing
├── email_utils.py        # SMTP / Gmail Notification Engine
├── badges.py             # Badge Definitions & Achievement Logic
├── tasks.py              # Points Mapping & Task Catalog
├── requirements.txt      # Dependency Manifest
├── assets/
│   ├── logo.png          # App Branding
│   └── pets/             # Pet State Lottie Animations (JSON)
├── models/
│   ├── analytics.py      # Data Visualization & Chart Logic
│   ├── pet.py            # Pet State & Leveling Logic
│   └── user.py           # User Profile & Activity Logic
└── pages/
    ├── home.py           # Main Dashboard & Pet Interaction
    ├── stats.py          # Productivity Metrics & Charts
    ├── task_logger.py    # Task Submission Interface
    ├── achievements.py   # Badge Gallery & Earned Milestones
    ├── logbook.py        # Historical Activity Log
    └── profile.py        # Account Settings & Security
```