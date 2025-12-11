# Pip Matrix Trading Platform

## Overview
Pip Matrix is a full-stack trading and investment platform with Flask backend and PostgreSQL database for permanent data storage. The platform provides interfaces for trading various financial instruments including forex, crypto, stocks, shares, real estate, and more.

## Architecture
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (Replit built-in)
- **Frontend**: Static HTML pages with embedded styling
- **Authentication**: Flask-Login with session-based auth
- **API**: RESTful JSON endpoints

## Project Structure
```
├── app.py              # Flask application with routes
├── models.py           # SQLAlchemy database models
├── static/
│   └── js/
│       └── api.js      # Frontend JavaScript API client
├── images/
│   └── LOGO.jpeg       # Pip Matrix logo
└── *.html              # Frontend HTML pages (27 total)
```

## Database Models
- **User**: Authentication and profile data
- **Account**: User's trading accounts with balances
- **Transaction**: Deposits, withdrawals, transfers
- **Trade**: Active and historical trades
- **Investment**: Long-term investment positions
- **Loan**: Loan requests and approvals
- **ReferralProgram**: User referral tracking
- **SupportTicket**: Customer support tickets
- **TradingBot**: Automated trading configurations

## API Endpoints
### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/check` - Check auth status

### User Data
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update profile
- `GET /api/user/dashboard` - Dashboard data

### Transactions
- `GET /api/transactions` - List transactions
- `POST /api/transactions/deposit` - Make deposit
- `POST /api/transactions/withdraw` - Make withdrawal
- `POST /api/transactions/transfer` - Transfer funds

### Trading
- `GET /api/trades` - List trades
- `POST /api/trades` - Open new trade
- `PUT /api/trades/<id>` - Update trade
- `DELETE /api/trades/<id>` - Close trade

### Portfolio
- `GET /api/portfolio` - Get portfolio summary
- `GET /api/investments` - List investments

## Pages
- `INDEX.html` - Main landing page
- `LOGIN.html` - User login (connected to API)
- `SIGNUP.html` - User registration (connected to API)
- `DASHBOARD.html` - User dashboard
- `PORTFOLIO.html` - Portfolio management
- `CRYPTO.html` / `CRYPTO-INDEX.html` - Cryptocurrency trading
- `FOREX-INDEX.html` - Forex trading
- `STOCK.html` / `SHARES-INDEX.html` - Stock trading
- `REALESTATE.html` - Real estate investments
- `INDICIES-INDEX.html` - Index trading
- `EFTs-INDEX.html` - ETF trading
- `BOT.html` - Trading bot
- `DEPOSIT.html` / `WITHDRAW.html` / `TRANSFER.html` - Financial operations
- `LOAN.html` / `LOANHISTORY.html` - Loan management
- `ACCOUNTHISTORY.html` - Account history
- `PERFORMANCE.html` - Performance metrics
- `PROFILE.html` - User profile
- `SUPPORT.html` - Support page
- `REFER.html` - Referral program
- `PREMIUM.html` - Premium features
- `COPY.html` - Copy trading
- `DEMO.html` - Demo account

## Technology Stack
- **Python 3**: Flask backend
- **PostgreSQL**: Database (Replit built-in)
- **Flask-SQLAlchemy**: ORM
- **Flask-Login**: Session management
- **Werkzeug**: Password hashing
- **Tailwind CSS**: Frontend styling (CDN)
- **Alpine.js**: Frontend interactivity
- **Lucide Icons**: Icon library

## Setup & Configuration
- **Port**: 5000 (Flask server)
- **Host**: 0.0.0.0 (for Replit proxy)
- **Database**: DATABASE_URL environment variable
- **Cache Control**: Disabled for development
- **Dark Mode**: Default theme

## Recent Changes
- **December 11, 2025**: Complete User Data Cleanup - All Data From Database
  - Fixed `/api/user/profile` endpoint to include balance data in user object for frontend access
  - Removed hardcoded demo balance ($85,872.36) from DASHBOARD.html - now fetches from database
  - Added `dashboardApp()` Alpine component to dynamically load user profile data on dashboard init
  - Added logout handler that properly calls `/api/auth/logout` API and redirects to login
  - Verified LOGIN.html and SIGNUP.html form handlers properly call API endpoints
  - User isolation enforced at API level with `@login_required` decorators
  - All user data (name, balance, demo_balance, email, phone, country) loaded from database
  - No hardcoded dummy data remains in any HTML file
  - Complete data flow: Signup → Database → Login → Session → Dashboard (real data only)

- **December 9, 2025**: Complete User Data Isolation Across All Pages
  - Created userData() function in api.js for centralized user data loading
  - Updated ALL 27 HTML pages to use dynamic Alpine.js bindings
  - Replaced all hardcoded dummy names ("Madisyn Lowe DDS") with x-text="fullName"
  - Replaced all hardcoded emails ("real12@gmail.com") with x-text="email"
  - Replaced all hardcoded balances with x-text="balance"
  - Replaced all avatar initials "M" with x-text="avatarInitials"
  - Added improved error handling for API failures
  - Authentication redirect works across all protected pages
  - Each user now sees ONLY their own data (name, email, balance, phone, country)
  - New users start with fresh $0 balance

- **December 9, 2025**: Full-stack backend integration
  - Created Flask backend with SQLAlchemy ORM
  - Set up PostgreSQL database with 9 tables
  - Built authentication system (login, signup, sessions)
  - Created RESTful API endpoints for all features
  - Connected frontend forms to backend API
  - Added api.js for frontend-backend communication

- **December 9, 2025**: Connected all pages
  - Fixed all navigation links across 27 HTML pages
  - Converted external URLs to local page references
  - Connected sidebar, header navigation, and button links

- **December 4, 2025**: Rebranding
  - Changed website name from "Remedy" to "Pip Matrix" across all 27 pages
  
- **December 4, 2025**: Initial Replit setup
  - Created Python HTTP server with cache control headers
  - Configured workflow to run on port 5000
  - Added .gitignore for Python and Replit files

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (auto-configured)
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` - DB credentials
