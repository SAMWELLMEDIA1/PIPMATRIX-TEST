import os
from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Account, Transaction, Investment, Trade, Loan, CopyTrading, BotTrading, Referral, SupportTicket
from datetime import datetime, timedelta
import secrets

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return send_from_directory('.', 'INDEX.html')

@app.route('/<path:filename>')
def serve_static(filename):
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    return send_from_directory('.', filename)

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'success': False, 'message': 'Username already taken'}), 400
    
    user = User(
        username=data.get('username'),
        email=data.get('email'),
        full_name=data.get('full_name'),
        phone=data.get('phone'),
        country=data.get('country')
    )
    user.set_password(data.get('password'))
    
    db.session.add(user)
    db.session.flush()
    
    account = Account(user_id=user.id)
    db.session.add(account)
    
    referral = Referral(
        referrer_id=user.id,
        referral_code=f"PIP{secrets.token_hex(4).upper()}"
    )
    db.session.add(referral)
    
    db.session.commit()
    
    login_user(user)
    
    return jsonify({
        'success': True,
        'message': 'Registration successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter(
        (User.email == data.get('email')) | (User.username == data.get('email'))
    ).first()
    
    if user and user.check_password(data.get('password')):
        user.last_login = datetime.utcnow()
        db.session.commit()
        login_user(user, remember=data.get('remember', False))
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name
            }
        })
    
    return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'full_name': current_user.full_name
            }
        })
    return jsonify({'authenticated': False})

@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_profile():
    account = current_user.account
    referral = Referral.query.filter_by(referrer_id=current_user.id).first()
    
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'phone': current_user.phone,
            'country': current_user.country,
            'is_verified': current_user.is_verified,
            'is_premium': current_user.is_premium,
            'balance': account.balance if account else 0,
            'demo_balance': account.demo_balance if account else 10000,
            'total_profit': account.total_profit if account else 0,
            'total_deposits': account.total_deposits if account else 0,
            'total_withdrawals': account.total_withdrawals if account else 0,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None
        },
        'account': {
            'balance': account.balance if account else 0,
            'demo_balance': account.demo_balance if account else 10000,
            'total_profit': account.total_profit if account else 0,
            'total_deposits': account.total_deposits if account else 0,
            'total_withdrawals': account.total_withdrawals if account else 0,
            'account_type': account.account_type if account else 'standard'
        },
        'referral_code': referral.referral_code if referral else None
    })

@app.route('/api/user/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()
    
    if 'full_name' in data:
        current_user.full_name = data['full_name']
    if 'phone' in data:
        current_user.phone = data['phone']
    if 'country' in data:
        current_user.country = data['country']
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Profile updated successfully'})

@app.route('/api/dashboard', methods=['GET'])
@login_required
def get_dashboard():
    account = current_user.account
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).limit(5).all()
    active_investments = Investment.query.filter_by(user_id=current_user.id, status='active').all()
    open_trades = Trade.query.filter_by(user_id=current_user.id, status='open').all()
    
    return jsonify({
        'account': {
            'balance': account.balance if account else 0,
            'demo_balance': account.demo_balance if account else 10000,
            'total_profit': account.total_profit if account else 0,
            'total_deposits': account.total_deposits if account else 0,
            'total_withdrawals': account.total_withdrawals if account else 0
        },
        'recent_transactions': [{
            'id': t.id,
            'type': t.type,
            'amount': t.amount,
            'status': t.status,
            'created_at': t.created_at.isoformat()
        } for t in recent_transactions],
        'active_investments': [{
            'id': i.id,
            'plan_name': i.plan_name,
            'amount': i.amount,
            'expected_return': i.expected_return,
            'status': i.status
        } for i in active_investments],
        'open_trades': len(open_trades)
    })

@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    tx_type = request.args.get('type')
    
    query = Transaction.query.filter_by(user_id=current_user.id)
    if tx_type:
        query = query.filter_by(type=tx_type)
    
    transactions = query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'transactions': [{
            'id': t.id,
            'type': t.type,
            'amount': t.amount,
            'status': t.status,
            'payment_method': t.payment_method,
            'description': t.description,
            'created_at': t.created_at.isoformat(),
            'completed_at': t.completed_at.isoformat() if t.completed_at else None
        } for t in transactions.items],
        'total': transactions.total,
        'pages': transactions.pages,
        'current_page': page
    })

@app.route('/api/deposit', methods=['POST'])
@login_required
def create_deposit():
    data = request.get_json()
    
    transaction = Transaction(
        user_id=current_user.id,
        type='deposit',
        amount=data.get('amount'),
        payment_method=data.get('payment_method'),
        wallet_address=data.get('wallet_address'),
        status='pending',
        reference=f"DEP{secrets.token_hex(6).upper()}"
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Deposit request submitted',
        'reference': transaction.reference
    })

@app.route('/api/withdraw', methods=['POST'])
@login_required
def create_withdrawal():
    data = request.get_json()
    amount = data.get('amount', 0)
    
    if current_user.account.balance < amount:
        return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
    
    transaction = Transaction(
        user_id=current_user.id,
        type='withdrawal',
        amount=amount,
        payment_method=data.get('payment_method'),
        wallet_address=data.get('wallet_address'),
        status='pending',
        reference=f"WTH{secrets.token_hex(6).upper()}"
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Withdrawal request submitted',
        'reference': transaction.reference
    })

@app.route('/api/transfer', methods=['POST'])
@login_required
def create_transfer():
    data = request.get_json()
    amount = data.get('amount', 0)
    recipient_username = data.get('recipient')
    
    if current_user.account.balance < amount:
        return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
    
    recipient = User.query.filter_by(username=recipient_username).first()
    if not recipient:
        return jsonify({'success': False, 'message': 'Recipient not found'}), 404
    
    current_user.account.balance -= amount
    recipient.account.balance += amount
    
    sender_tx = Transaction(
        user_id=current_user.id,
        type='transfer',
        amount=-amount,
        status='completed',
        description=f"Transfer to {recipient_username}",
        reference=f"TRF{secrets.token_hex(6).upper()}",
        completed_at=datetime.utcnow()
    )
    
    recipient_tx = Transaction(
        user_id=recipient.id,
        type='transfer',
        amount=amount,
        status='completed',
        description=f"Transfer from {current_user.username}",
        reference=sender_tx.reference,
        completed_at=datetime.utcnow()
    )
    
    db.session.add_all([sender_tx, recipient_tx])
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Transfer completed'})

@app.route('/api/investments', methods=['GET'])
@login_required
def get_investments():
    investments = Investment.query.filter_by(user_id=current_user.id).order_by(Investment.start_date.desc()).all()
    
    return jsonify({
        'investments': [{
            'id': i.id,
            'plan_name': i.plan_name,
            'plan_type': i.plan_type,
            'amount': i.amount,
            'expected_return': i.expected_return,
            'actual_return': i.actual_return,
            'duration_days': i.duration_days,
            'status': i.status,
            'start_date': i.start_date.isoformat(),
            'end_date': i.end_date.isoformat() if i.end_date else None
        } for i in investments]
    })

@app.route('/api/investments', methods=['POST'])
@login_required
def create_investment():
    data = request.get_json()
    amount = data.get('amount', 0)
    
    if current_user.account.balance < amount:
        return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
    
    current_user.account.balance -= amount
    
    duration_days = data.get('duration_days', 30)
    expected_return = amount * (1 + (data.get('roi', 10) / 100))
    
    investment = Investment(
        user_id=current_user.id,
        plan_name=data.get('plan_name'),
        plan_type=data.get('plan_type'),
        amount=amount,
        expected_return=expected_return,
        duration_days=duration_days,
        end_date=datetime.utcnow() + timedelta(days=duration_days)
    )
    db.session.add(investment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Investment created successfully',
        'investment_id': investment.id
    })

@app.route('/api/trades', methods=['GET'])
@login_required
def get_trades():
    is_demo = request.args.get('demo', 'false').lower() == 'true'
    status = request.args.get('status')
    
    query = Trade.query.filter_by(user_id=current_user.id, is_demo=is_demo)
    if status:
        query = query.filter_by(status=status)
    
    trades = query.order_by(Trade.created_at.desc()).all()
    
    return jsonify({
        'trades': [{
            'id': t.id,
            'symbol': t.symbol,
            'trade_type': t.trade_type,
            'amount': t.amount,
            'entry_price': t.entry_price,
            'exit_price': t.exit_price,
            'profit_loss': t.profit_loss,
            'leverage': t.leverage,
            'status': t.status,
            'created_at': t.created_at.isoformat(),
            'closed_at': t.closed_at.isoformat() if t.closed_at else None
        } for t in trades]
    })

@app.route('/api/trades', methods=['POST'])
@login_required
def create_trade():
    data = request.get_json()
    is_demo = data.get('is_demo', False)
    amount = data.get('amount', 0)
    
    if is_demo:
        if current_user.account.demo_balance < amount:
            return jsonify({'success': False, 'message': 'Insufficient demo balance'}), 400
        current_user.account.demo_balance -= amount
    else:
        if current_user.account.balance < amount:
            return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
        current_user.account.balance -= amount
    
    trade = Trade(
        user_id=current_user.id,
        symbol=data.get('symbol'),
        trade_type=data.get('trade_type'),
        amount=amount,
        entry_price=data.get('entry_price'),
        leverage=data.get('leverage', 1),
        is_demo=is_demo
    )
    db.session.add(trade)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Trade opened successfully',
        'trade_id': trade.id
    })

@app.route('/api/trades/<int:trade_id>/close', methods=['POST'])
@login_required
def close_trade(trade_id):
    trade = Trade.query.filter_by(id=trade_id, user_id=current_user.id).first()
    
    if not trade:
        return jsonify({'success': False, 'message': 'Trade not found'}), 404
    
    if trade.status != 'open':
        return jsonify({'success': False, 'message': 'Trade is not open'}), 400
    
    data = request.get_json()
    exit_price = data.get('exit_price', trade.entry_price)
    
    price_diff = exit_price - trade.entry_price
    if trade.trade_type == 'sell':
        price_diff = -price_diff
    
    profit_loss = (price_diff / trade.entry_price) * trade.amount * trade.leverage
    
    trade.exit_price = exit_price
    trade.profit_loss = profit_loss
    trade.status = 'closed'
    trade.closed_at = datetime.utcnow()
    
    return_amount = trade.amount + profit_loss
    if trade.is_demo:
        current_user.account.demo_balance += return_amount
    else:
        current_user.account.balance += return_amount
        current_user.account.total_profit += profit_loss
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Trade closed',
        'profit_loss': profit_loss
    })

@app.route('/api/loans', methods=['GET'])
@login_required
def get_loans():
    loans = Loan.query.filter_by(user_id=current_user.id).order_by(Loan.created_at.desc()).all()
    
    return jsonify({
        'loans': [{
            'id': l.id,
            'amount': l.amount,
            'interest_rate': l.interest_rate,
            'duration_months': l.duration_months,
            'monthly_payment': l.monthly_payment,
            'total_repayment': l.total_repayment,
            'amount_paid': l.amount_paid,
            'status': l.status,
            'purpose': l.purpose,
            'created_at': l.created_at.isoformat()
        } for l in loans]
    })

@app.route('/api/loans', methods=['POST'])
@login_required
def create_loan():
    data = request.get_json()
    amount = data.get('amount', 0)
    duration_months = data.get('duration_months', 12)
    interest_rate = data.get('interest_rate', 5.0)
    
    total_repayment = amount * (1 + (interest_rate * duration_months / 100))
    monthly_payment = total_repayment / duration_months
    
    loan = Loan(
        user_id=current_user.id,
        amount=amount,
        interest_rate=interest_rate,
        duration_months=duration_months,
        monthly_payment=monthly_payment,
        total_repayment=total_repayment,
        purpose=data.get('purpose'),
        status='pending'
    )
    db.session.add(loan)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Loan application submitted',
        'loan_id': loan.id
    })

@app.route('/api/copy-trading', methods=['GET'])
@login_required
def get_copy_trading():
    copies = CopyTrading.query.filter_by(user_id=current_user.id).all()
    
    return jsonify({
        'copy_trading': [{
            'id': c.id,
            'trader_name': c.trader_name,
            'amount_allocated': c.amount_allocated,
            'profit_share': c.profit_share,
            'total_profit': c.total_profit,
            'status': c.status,
            'created_at': c.created_at.isoformat()
        } for c in copies]
    })

@app.route('/api/copy-trading', methods=['POST'])
@login_required
def start_copy_trading():
    data = request.get_json()
    amount = data.get('amount', 0)
    
    if current_user.account.balance < amount:
        return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
    
    current_user.account.balance -= amount
    
    copy = CopyTrading(
        user_id=current_user.id,
        trader_name=data.get('trader_name'),
        amount_allocated=amount,
        profit_share=data.get('profit_share', 20.0)
    )
    db.session.add(copy)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Copy trading started',
        'copy_id': copy.id
    })

@app.route('/api/bot-trading', methods=['GET'])
@login_required
def get_bot_trading():
    bots = BotTrading.query.filter_by(user_id=current_user.id).all()
    
    return jsonify({
        'bots': [{
            'id': b.id,
            'bot_name': b.bot_name,
            'strategy': b.strategy,
            'amount_allocated': b.amount_allocated,
            'total_profit': b.total_profit,
            'trades_executed': b.trades_executed,
            'win_rate': b.win_rate,
            'status': b.status,
            'created_at': b.created_at.isoformat()
        } for b in bots]
    })

@app.route('/api/bot-trading', methods=['POST'])
@login_required
def start_bot_trading():
    data = request.get_json()
    amount = data.get('amount', 0)
    
    if current_user.account.balance < amount:
        return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
    
    current_user.account.balance -= amount
    
    bot = BotTrading(
        user_id=current_user.id,
        bot_name=data.get('bot_name'),
        strategy=data.get('strategy'),
        amount_allocated=amount
    )
    db.session.add(bot)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Bot trading started',
        'bot_id': bot.id
    })

@app.route('/api/support', methods=['GET'])
@login_required
def get_support_tickets():
    tickets = SupportTicket.query.filter_by(user_id=current_user.id).order_by(SupportTicket.created_at.desc()).all()
    
    return jsonify({
        'tickets': [{
            'id': t.id,
            'subject': t.subject,
            'message': t.message,
            'priority': t.priority,
            'status': t.status,
            'response': t.response,
            'created_at': t.created_at.isoformat(),
            'resolved_at': t.resolved_at.isoformat() if t.resolved_at else None
        } for t in tickets]
    })

@app.route('/api/support', methods=['POST'])
@login_required
def create_support_ticket():
    data = request.get_json()
    
    ticket = SupportTicket(
        user_id=current_user.id,
        subject=data.get('subject'),
        message=data.get('message'),
        priority=data.get('priority', 'medium')
    )
    db.session.add(ticket)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Support ticket created',
        'ticket_id': ticket.id
    })

@app.route('/api/referral', methods=['GET'])
@login_required
def get_referral():
    referral = Referral.query.filter_by(referrer_id=current_user.id).first()
    referred_users = User.query.join(Referral, Referral.referred_user_id == User.id).filter(
        Referral.referrer_id == current_user.id
    ).all()
    
    return jsonify({
        'referral_code': referral.referral_code if referral else None,
        'total_bonus': referral.bonus_earned if referral else 0,
        'referred_users': len(referred_users)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
