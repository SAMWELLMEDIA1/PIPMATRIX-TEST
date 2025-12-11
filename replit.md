# Pip Matrix Trading Platform

## Overview

Pip Matrix is a full-stack cryptocurrency and trading platform that allows users to manage investments across multiple asset classes including crypto, forex, stocks, ETFs, and real estate. The platform features user authentication, deposit/withdrawal management via cryptocurrency payments, demo trading, bot trading, copy trading, loan applications, and referral systems.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology**: Static HTML pages with Tailwind CSS for styling and Alpine.js for reactive UI components
- **Design Pattern**: Multi-page application (MPA) with each feature having its own HTML page
- **Styling Approach**: Dark mode by default using Tailwind's class-based dark mode strategy with custom color palette (primary indigo tones)
- **UI Components**: Uses SweetAlert2 for notifications/modals, Lucide icons for iconography
- **State Management**: localStorage for theme persistence, Alpine.js for page-level reactive state

### Backend Architecture
- **Framework**: Flask (Python) with Flask-Login for session management
- **API Design**: RESTful JSON API endpoints prefixed with `/api/`
- **Authentication**: Session-based authentication using Flask-Login with password hashing via Werkzeug
- **File Serving**: Flask serves static HTML files directly, with a simple HTTP server fallback (server.py)

### Database Layer
- **ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Database**: PostgreSQL (configured via DATABASE_URL environment variable)
- **Connection Pooling**: Uses `pool_pre_ping` for connection health checks

### Data Models
- **User**: Core user entity with authentication, profile data, and relationships
- **Account**: Financial account with balance tracking (live and demo)
- **Transaction**: Deposits, withdrawals, and transfers
- **Investment**: Investment packages and plans
- **Trade**: Trading positions and history
- **Loan**: Loan applications and status
- **CopyTrading/BotTrading**: Automated trading features
- **Referral**: User referral tracking
- **SupportTicket**: Customer support system
- **Notification**: User notifications

### Crypto Payment System
- **Supported Currencies**: BTC, ETH, BNB, SOL, DOGE, USDT (TRC20), XRP
- **QR Code Generation**: Dynamic QR codes using Python qrcode library
- **Wallet Addresses**: Hardcoded in backend (CRYPTO_WALLETS dictionary in app.py)
- **Payment Flow**: User selects crypto → displays wallet + QR → user submits TXID + receipt → admin approval

### File Upload Handling
- **Location**: `uploads/` directory
- **Max Size**: 16MB limit configured in Flask
- **Use Case**: Payment receipts/screenshots for deposit verification

## External Dependencies

### Frontend CDN Libraries
- **Tailwind CSS**: Utility-first CSS framework (cdn.tailwindcss.com)
- **Alpine.js**: Lightweight reactive JavaScript framework
- **SweetAlert2**: Modal and notification library
- **Lucide Icons**: Icon library
- **FontAwesome**: Additional icons
- **Google Fonts**: Inter font family

### Backend Python Packages
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Werkzeug**: Password hashing and security utilities
- **qrcode**: QR code generation for crypto payments
- **Pillow** (implied): Image processing for QR codes

### Database
- **PostgreSQL**: Primary database, connection string via `DATABASE_URL` environment variable

### External Services
- **None currently integrated**: The platform is self-contained without third-party API integrations for trading data or payment processing