from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(200))
    phone = db.Column(db.String(120))
    country = db.Column(db.String(100))
    profile_image = db.Column(db.String(500))
    is_verified = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    account = db.relationship('Account', backref='user', uselist=False, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    investments = db.relationship('Investment', backref='user', lazy=True, cascade='all, delete-orphan')
    loans = db.relationship('Loan', backref='user', lazy=True, cascade='all, delete-orphan')
    referrals = db.relationship('Referral', backref='referrer', lazy=True, foreign_keys='Referral.referrer_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    demo_balance = db.Column(db.Float, default=10000.0)
    total_profit = db.Column(db.Float, default=0.0)
    total_deposits = db.Column(db.Float, default=0.0)
    total_withdrawals = db.Column(db.Float, default=0.0)
    account_type = db.Column(db.String(50), default='standard')
    wallet_address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    payment_method = db.Column(db.String(100))
    wallet_address = db.Column(db.String(200))
    reference = db.Column(db.String(100))
    description = db.Column(db.Text)
    crypto_type = db.Column(db.String(50))
    crypto_network = db.Column(db.String(50))
    txid = db.Column(db.String(200))
    receipt_filename = db.Column(db.String(500))
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class Investment(db.Model):
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    plan_type = db.Column(db.String(50))
    amount = db.Column(db.Float, nullable=False)
    expected_return = db.Column(db.Float)
    actual_return = db.Column(db.Float, default=0.0)
    duration_days = db.Column(db.Integer)
    status = db.Column(db.String(50), default='active')
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    trade_type = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float)
    profit_loss = db.Column(db.Float, default=0.0)
    leverage = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50), default='open')
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, default=5.0)
    duration_months = db.Column(db.Integer, nullable=False)
    monthly_payment = db.Column(db.Float)
    total_repayment = db.Column(db.Float)
    amount_paid = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='pending')
    purpose = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)

class CopyTrading(db.Model):
    __tablename__ = 'copy_trading'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trader_name = db.Column(db.String(100), nullable=False)
    amount_allocated = db.Column(db.Float, nullable=False)
    profit_share = db.Column(db.Float, default=20.0)
    total_profit = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BotTrading(db.Model):
    __tablename__ = 'bot_trading'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bot_name = db.Column(db.String(100), nullable=False)
    strategy = db.Column(db.String(100))
    amount_allocated = db.Column(db.Float, nullable=False)
    total_profit = db.Column(db.Float, default=0.0)
    trades_executed = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Referral(db.Model):
    __tablename__ = 'referrals'
    
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    referred_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    referral_code = db.Column(db.String(50), unique=True)
    bonus_earned = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(50), default='open')
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TradeRule(db.Model):
    __tablename__ = 'trade_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    asset = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    profit_percentage = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    apply_all_time = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscription_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    payment_method = db.Column(db.String(100))
    txid = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    activated_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref=db.backref('subscriptions', lazy=True))
