# Pip Matrix Trading Platform

## Overview
Pip Matrix is a full-stack cryptocurrency and trading platform designed to allow users to manage investments across various asset classes, including crypto, forex, stocks, ETFs, and real estate. The platform aims to provide a comprehensive trading experience with features such as user authentication, cryptocurrency-based deposit/withdrawal management, demo trading, bot trading, copy trading, loan applications, and a referral system. Its ambition is to offer a unified solution for diverse investment needs, catering to both novice and experienced traders.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend
- **Technology Stack**: Static HTML pages, Tailwind CSS for styling, Alpine.js for reactive UI.
- **Design Principles**: Multi-page application (MPA) architecture, dark mode by default with a custom indigo color palette, mobile-responsive design.
- **UI Components**: SweetAlert2 for notifications, Lucide and FontAwesome for iconography, Google Fonts (Inter).
- **State Management**: `localStorage` for theme persistence, Alpine.js for page-level reactivity.

### Backend
- **Framework**: Flask (Python).
- **API**: RESTful JSON API endpoints prefixed with `/api/`.
- **Authentication**: Session-based using Flask-Login with Werkzeug for password hashing.
- **File Serving**: Flask serves static HTML and assets.

### Database
- **ORM**: SQLAlchemy with Flask-SQLAlchemy.
- **Database**: PostgreSQL (configured via `DATABASE_URL`).
- **Connection Management**: `pool_pre_ping` for connection health checks.

### Data Models
Key entities include `User`, `Account` (live/demo balances), `Transaction` (deposits/withdrawals), `Investment`, `Trade`, `Loan`, `CopyTrading`, `BotTrading`, `Referral`, `SupportTicket`, `Notification`, `TradeRule` (admin-defined profit/loss rules), and `Subscription`.

### Core Features & Implementations
- **Crypto Payment System**: Supports BTC, ETH, BNB, SOL, DOGE, USDT (TRC20), XRP. Features dynamic QR code generation, network display, TXID submission, and optional receipt upload. Admin approval for deposits and withdrawals.
- **Trading Systems**:
    - **Demo Trading**: Virtual balance, asset selection (crypto, stocks, forex), trade configuration (amount, leverage, order type), real-time trade summary, and account reset.
    - **Live Trading**: Real-money trading with balance validation, warning confirmations, and integration with the deposit system.
    - **Martingale Trading Chart**: Custom canvas-based chart on the dashboard with multiple asset types, timeframes, simulated real-time price updates, market sentiment, payout display, and trade timer. Trades automatically close upon timer expiry, calculating profit/loss based on entry/exit prices and admin-defined rules.
- **Admin Dashboard**: Secure, tab-based interface with admin authentication. Provides statistics, user management, new signup tracking, and comprehensive tools for managing deposits, withdrawals, subscriptions, and defining trade profit/loss rules.
- **Account History**: Consolidated view for all trades (demo and live) and a dedicated tab for live trade history with detailed insights.
- **File Uploads**: Handles payment receipts up to 16MB in the `uploads/` directory.

## External Dependencies

### Frontend Libraries (CDN)
-   Tailwind CSS
-   Alpine.js
-   SweetAlert2
-   Lucide Icons
-   FontAwesome
-   Google Fonts (Inter)

### Backend Python Packages
-   Flask
-   Flask-SQLAlchemy
-   Flask-Login
-   Werkzeug
-   qrcode

### Database
-   PostgreSQL

### External Services
-   None currently integrated for external trading data or payment gateways; the platform relies on direct crypto wallet interactions.