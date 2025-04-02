# Flask Portfolio API

This is a Flask-based backend API for managing a portfolio system. The application handles authentication, user management, company-related data, investments, and notifications. It also integrates with Stripe for payment processing and Gmail for email notifications.

## Features

- User authentication (JWT-based)
- Company data management
- Investment tracking
- Notification system
- Stripe payment integration
- Secure email handling with Gmail
- Structured middleware for token verification and error handling

## Folder Structure

```
/alx-portfolio-server
│── README.md             # Documentation
│── app.py                # Main application entry point
│── alembic.ini           # Alembic configuration for database migrations
│── engine/               # Database storage logic
│   ├── __init__.py
│   ├── db_storage.py
│── middlewares/          # Middleware for handling errors and authentication
│   ├── __init__.py
│   ├── error_handler.py
│   ├── verify_token.py
│── models/               # ORM models for database tables
│   ├── __init__.py
│   ├── company.py
│   ├── company_docs.py
│   ├── company_growth_rate.py
│   ├── company_owners.py
│   ├── investment_deal.py
│   ├── notification.py
│   ├── user.py
│── routes/               # API route handlers
│   ├── __init__.py
│   ├── auth_route.py
│   ├── user_route.py
│   ├── company_route.py
│   ├── company_rates.py
│   ├── company_docs.py
│   ├── notification_route.py
│   ├── investment_route.py
│── utilies/              # Utility functions
│   ├── __init__.py
│   ├── company_utils.py
│   ├── mail_helper.py
│   ├── stripe_utilies.py
│── validation/           # Validation logic
│   ├── __init__.py
│   ├── auth_validator.py
│   ├── company_validation.py
│── migrations/           # Database migration files
│── .env                  # Environment variables (Not included in repo)
```

## Installation

### Prerequisites

- Python 3.8+
- MySQL
- Virtual environment (optional but recommended)

### Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/alx-portfolio-server.git
   cd alx-portfolio-server
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```sh
   python3 -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate      # On Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Configure the `.env` file:
   ```sh
   cp .env.example .env  # Then edit with your credentials
   ```

## Running the Application

1. Ensure your MySQL database is running.
2. Run database migrations:
   ```sh
   flask db upgrade
   ```
3. Start the Flask server:
   ```sh
   python3 app.py
   ```
   The application runs on `http://localhost:8000` by default.

## API Endpoints

| Method | Endpoint               | Description              |
| ------ | ---------------------- | ------------------------ |
| POST   | `/api/auth/login`      | User login               |
| POST   | `/api/auth/register`   | User registration        |
| GET    | `/api/users/me`        | Get current user details |
| GET    | `/api/companies`       | Get list of companies    |
| POST   | `/api/investments`     | Create a new investment  |
| GET    | `/api/notifications`   | Fetch user notifications |
| POST   | `/api/payments/stripe` | Process Stripe payment   |

## Environment Variables

The application requires an `.env` file with the following variables:

```
PORT=8000
HOST=0.0.0.0
SQLALCHEMY_DATABASE_URI=mysql+pymysql://username:password@localhost:3306/portfolio_DB

# JWT Information
JWT_KEY=your_jwt_secret_key
JWT_ALG=HS256

# Gmail App Password
GMAIL_USER=your_email@gmail.com
GMAIL_PASS=your_app_password

# Encryption details
FERNET_KEY=your_fernet_key

# Stripe info
STRIPE_PUPLISH_KEY=your_stripe_publish_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

## Security Considerations

- **Never commit your ****`.env`**** file** to version control.
- Use **secure and strong JWT keys** for authentication.
- Set up **database backups** to prevent data loss.
- Enable **HTTPS** in production to secure data transfers.

## Contributing

1. Fork the repository.
2. Create a feature branch:
   ```sh
   git checkout -b feature-branch
   ```
3. Commit your changes:
   ```sh
   git commit -m "Add new feature"
   ```
4. Push to GitHub:
   ```sh
   git push origin feature-branch
   ```
5. Create a Pull Request.

## License

This project is licensed under the **MIT License**.

---

Made with ❤️ by Martin Mostafa
