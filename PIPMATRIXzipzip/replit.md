# Pip Matrix Trading Platform

## Overview
A full-stack trading platform built with Flask backend and HTML/Tailwind CSS frontend. The platform allows users to register, login, manage deposits/withdrawals, trade, and receive notifications for all their activities.

## Project Architecture

### Backend (Python/Flask)
- **app.py** - Main Flask application with all API endpoints
- **models.py** - SQLAlchemy database models for users, accounts, transactions, trades, notifications, etc.

### Frontend (HTML/Tailwind CSS/Alpine.js)
- **INDEX.html** - Landing page
- **LOGIN.html** - User login page
- **SIGNUP.html** - User registration page
- **DASHBOARD.html** - Main user dashboard
- **DEPOSIT.html** - Deposit funds page
- **WITHDRAW.html** - Withdrawal page
- **ACCOUNTHISTORY.html** - Transaction history
- **PROFILE.html** - User profile management
- And more trading-related pages (STOCK, CRYPTO, FOREX, etc.)

### Static Files
- **static/js/api.js** - API wrapper for frontend to communicate with backend
- **images/** - Logo and other images

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/check` - Check authentication status

### User
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `GET /api/dashboard` - Get dashboard data

### Transactions
- `GET /api/transactions` - Get user transactions (with optional type filter)
- `POST /api/deposit` - Create deposit request
- `POST /api/withdraw` - Create withdrawal request
- `POST /api/transfer` - Transfer funds to another user

### Trading
- `GET /api/trades` - Get user trades
- `POST /api/trades` - Open new trade
- `POST /api/trades/<id>/close` - Close trade

### Notifications
- `GET /api/notifications` - Get user notifications
- `POST /api/notifications/<id>/read` - Mark notification as read
- `POST /api/notifications/read-all` - Mark all notifications as read

### Other
- `GET /api/investments` - Get investments
- `POST /api/investments` - Create investment
- `GET /api/loans` - Get loans
- `POST /api/loans` - Apply for loan
- `GET /api/support` - Get support tickets
- `POST /api/support` - Create support ticket
- `GET /api/referral` - Get referral info

## Database Models
- **User** - User accounts with authentication
- **Account** - User financial account (balance, demo balance, etc.)
- **Transaction** - Deposits, withdrawals, transfers
- **Investment** - Investment plans
- **Trade** - Trading positions
- **Loan** - Loan applications
- **CopyTrading** - Copy trading subscriptions
- **BotTrading** - Bot trading configurations
- **Referral** - Referral codes and bonuses
- **SupportTicket** - Customer support tickets
- **Notification** - User notifications

## Key Features
1. User registration and authentication with Flask-Login
2. Dynamic balance tracking (starts at $0 for new users)
3. Deposit and withdrawal system
4. Trading functionality (live and demo accounts)
5. Automatic notification generation for all user actions
6. Support ticket system
7. Referral system

## Recent Changes

### December 11, 2025 - Wallet Connection & Payment Enhancements
- Created CONNECT.html with full wallet selection interface (40+ wallets from provider code)
- Updated Dashboard "Connect Wallet" button to navigate to CONNECT.html
- Wallet page includes search functionality, Bootstrap styling, and responsive grid layout
- Fixed CSS/jQuery dependencies and added Bootstrap CDN integration
- Created shared `paymentModal.js` component for consistent payment method selection across pages
- Updated BOT.html with payment modal - all 55 "Invest Now" buttons now open crypto payment selection modal
- Updated PREMIUM.html with payment modal for subscription purchases
- DEPOSIT.html now accepts URL parameters (crypto, source, amount, plan) for context-aware payment flows
- Fixed Premium Signals navbar links across 18+ HTML files (corrected from DASHBOARD.html to PREMIUM.html)
- Payment flow routes users directly to specific cryptocurrency deposit pages with context preserved

### Previous Changes
- Added Notification model and API endpoints
- Removed all hardcoded dummy data from frontend
- Added automatic notification creation for deposits, withdrawals, and trades
- Dashboard now loads notifications dynamically from API
- All user data displays as empty/zero for new users until they perform actions

## Running the Application
The Flask server runs on port 5000 with the command: `python app.py`
