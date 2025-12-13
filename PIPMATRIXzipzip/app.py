import os
import io
import base64
from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Account, Transaction, Investment, Trade, Loan, CopyTrading, BotTrading, Referral, SupportTicket, Notification
from datetime import datetime, timedelta
import secrets
import qrcode

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CRYPTO_WALLETS = {
    'BTC': {
        'address': 'bc1q8a07p9n6xlwvaare2a9dghtvtk5zd232ca55q0',
        'network': 'Bitcoin',
        'name': 'Bitcoin',
        'symbol': 'BTC',
        'icon': 'bitcoin'
    },
    'ETH': {
        'address': '0x11722310395Dd27de946F5B87F79da16Ea2fdECe',
        'network': 'Ethereum',
        'name': 'Ethereum',
        'symbol': 'ETH',
        'icon': 'ethereum'
    },
    'BNB': {
        'address': '0x11722310395Dd27de946F5B87F79da16Ea2fdECe',
        'network': 'BNB Smart Chain',
        'name': 'BNB',
        'symbol': 'BNB',
        'icon': 'bnb'
    },
    'SOL': {
        'address': 'GdLjdGR6GWxPoYDvfvLbfAgNhNDMNE3B6sXCzrwHCT8r',
        'network': 'Solana',
        'name': 'Solana',
        'symbol': 'SOL',
        'icon': 'solana'
    },
    'DOGE': {
        'address': 'DPN2z9snmiM7w3bqkHqRS8NJiYyHYE4Js8',
        'network': 'Dogecoin',
        'name': 'Dogecoin',
        'symbol': 'DOGE',
        'icon': 'dogecoin'
    },
    'USDT_TRC20': {
        'address': 'TMWtrR9eAe1crQyyUoF1E9eZBaanxCDTs1',
        'network': 'Tron (TRC20)',
        'name': 'USDT',
        'symbol': 'USDT',
        'icon': 'usdt'
    },
    'XRP': {
        'address': 'rUBFJqt1WCcYH88o7keaRV5CBoKAaA5AC',
        'network': 'XRP Ledger',
        'name': 'XRP',
        'symbol': 'XRP',
        'icon': 'xrp'
    }
}

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

@app.route('/')
def index():
    return send_from_directory('.', 'INDEX.html')

@app.route('/<path:filename>')
def serve_static(filename):
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    return send_from_directory('.', filename)

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

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
        'success': True,
        'transactions': [{
            'id': t.id,
            'type': t.type,
            'amount': t.amount,
            'status': t.status,
            'payment_method': t.payment_method,
            'crypto_type': t.crypto_type,
            'crypto_network': t.crypto_network,
            'txid': t.txid,
            'description': t.description,
            'created_at': t.created_at.isoformat(),
            'completed_at': t.completed_at.isoformat() if t.completed_at else None
        } for t in transactions.items],
        'total': transactions.total,
        'pages': transactions.pages,
        'current_page': page
    })

@app.route('/api/crypto/wallets', methods=['GET'])
def get_crypto_wallets():
    wallets = []
    for key, wallet in CRYPTO_WALLETS.items():
        qr_code = generate_qr_code(wallet['address'])
        wallets.append({
            'id': key,
            'name': wallet['name'],
            'symbol': wallet['symbol'],
            'network': wallet['network'],
            'address': wallet['address'],
            'icon': wallet['icon'],
            'qr_code': qr_code
        })
    return jsonify({'success': True, 'wallets': wallets})

@app.route('/api/crypto/wallet/<crypto_id>', methods=['GET'])
def get_crypto_wallet(crypto_id):
    crypto_id = crypto_id.upper()
    if crypto_id not in CRYPTO_WALLETS:
        return jsonify({'success': False, 'message': 'Invalid cryptocurrency'}), 400
    
    wallet = CRYPTO_WALLETS[crypto_id]
    qr_code = generate_qr_code(wallet['address'])
    
    return jsonify({
        'success': True,
        'wallet': {
            'id': crypto_id,
            'name': wallet['name'],
            'symbol': wallet['symbol'],
            'network': wallet['network'],
            'address': wallet['address'],
            'icon': wallet['icon'],
            'qr_code': qr_code
        }
    })

@app.route('/api/deposit/crypto', methods=['POST'])
@login_required
def create_crypto_deposit():
    if 'receipt' in request.files:
        receipt_file = request.files['receipt']
        amount = request.form.get('amount', 0, type=float)
        crypto_type = request.form.get('crypto_type', '')
        txid = request.form.get('txid', '')
    else:
        data = request.get_json() or {}
        amount = data.get('amount', 0)
        crypto_type = data.get('crypto_type', '')
        txid = data.get('txid', '')
        receipt_file = None
    
    crypto_id = crypto_type.upper()
    if crypto_id not in CRYPTO_WALLETS:
        return jsonify({'success': False, 'message': 'Invalid cryptocurrency selected'}), 400
    
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Invalid amount'}), 400
    
    if not txid:
        return jsonify({'success': False, 'message': 'Transaction hash (TXID) is required'}), 400
    
    wallet = CRYPTO_WALLETS[crypto_id]
    
    receipt_filename = None
    if receipt_file and receipt_file.filename:
        ext = receipt_file.filename.rsplit('.', 1)[-1].lower() if '.' in receipt_file.filename else 'png'
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'pdf']:
            return jsonify({'success': False, 'message': 'Invalid file type. Allowed: jpg, jpeg, png, gif, pdf'}), 400
        
        receipt_filename = f"{secrets.token_hex(16)}_{current_user.id}.{ext}"
        receipt_file.save(os.path.join(UPLOAD_FOLDER, receipt_filename))
    
    transaction = Transaction(
        user_id=current_user.id,
        type='deposit',
        amount=amount,
        payment_method='crypto',
        wallet_address=wallet['address'],
        crypto_type=wallet['symbol'],
        crypto_network=wallet['network'],
        txid=txid,
        receipt_filename=receipt_filename,
        status='pending',
        reference=f"DEP{secrets.token_hex(6).upper()}"
    )
    db.session.add(transaction)
    
    notification = Notification(
        user_id=current_user.id,
        title='Crypto Deposit Submitted',
        message=f'Your deposit of ${amount:,.2f} via {wallet["name"]} ({wallet["network"]}) has been submitted. TXID: {txid[:20]}...',
        type='info'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Deposit request submitted successfully. Please wait for confirmation.',
        'reference': transaction.reference,
        'transaction': {
            'id': transaction.id,
            'amount': transaction.amount,
            'crypto_type': transaction.crypto_type,
            'crypto_network': transaction.crypto_network,
            'txid': transaction.txid,
            'status': transaction.status
        }
    })

@app.route('/api/deposit', methods=['POST'])
@login_required
def create_deposit():
    data = request.get_json()
    amount = data.get('amount', 0)
    
    transaction = Transaction(
        user_id=current_user.id,
        type='deposit',
        amount=amount,
        payment_method=data.get('payment_method'),
        wallet_address=data.get('wallet_address'),
        status='pending',
        reference=f"DEP{secrets.token_hex(6).upper()}"
    )
    db.session.add(transaction)
    
    notification = Notification(
        user_id=current_user.id,
        title='Deposit Request Submitted',
        message=f'Your deposit request for ${amount:,.2f} has been submitted and is pending confirmation.',
        type='info'
    )
    db.session.add(notification)
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
    
    notification = Notification(
        user_id=current_user.id,
        title='Withdrawal Request Submitted',
        message=f'Your withdrawal request for ${amount:,.2f} has been submitted and is being processed.',
        type='info'
    )
    db.session.add(notification)
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
    symbol = data.get('symbol', 'Unknown')
    
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
        symbol=symbol,
        trade_type=data.get('trade_type'),
        amount=amount,
        entry_price=data.get('entry_price'),
        leverage=data.get('leverage', 1),
        is_demo=is_demo
    )
    db.session.add(trade)
    
    account_type = 'Demo' if is_demo else 'Live'
    notification = Notification(
        user_id=current_user.id,
        title=f'{account_type} Trade Opened',
        message=f'You opened a {data.get("trade_type", "buy").upper()} trade on {symbol} for ${amount:,.2f}.',
        type='success'
    )
    db.session.add(notification)
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
    referred_users = Referral.query.filter_by(referrer_id=current_user.id).all()
    
    return jsonify({
        'referral_code': referral.referral_code if referral else None,
        'total_referrals': len(referred_users),
        'total_bonus': sum(r.bonus_earned for r in referred_users)
    })

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
    
    def time_ago(dt):
        now = datetime.utcnow()
        diff = now - dt
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    return jsonify({
        'success': True,
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.type,
            'read': n.read,
            'created_at': n.created_at.isoformat(),
            'time_ago': time_ago(n.created_at)
        } for n in notifications]
    })

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
    if notification:
        notification.read = True
        db.session.commit()
    return jsonify({'success': True})

@app.route('/api/demo/balance', methods=['GET'])
@login_required
def get_demo_balance():
    account = Account.query.filter_by(user_id=current_user.id).first()
    if not account:
        account = Account(user_id=current_user.id, demo_balance=10000.0)
        db.session.add(account)
        db.session.commit()
    
    open_trades = Trade.query.filter_by(user_id=current_user.id, is_demo=True, status='open').all()
    open_trades_value = sum(t.amount for t in open_trades)
    
    return jsonify({
        'success': True,
        'demo_balance': account.demo_balance,
        'open_trades_count': len(open_trades),
        'open_trades_value': open_trades_value
    })

@app.route('/api/demo/trade', methods=['POST'])
@login_required
def place_demo_trade():
    data = request.get_json()
    
    symbol = data.get('symbol')
    trade_type = data.get('trade_type', 'buy')
    amount = float(data.get('amount', 0))
    entry_price = float(data.get('entry_price', 0))
    leverage = int(data.get('leverage', 1))
    expiry_seconds = int(data.get('expiry_seconds', 60))
    
    if not symbol or amount <= 0 or entry_price <= 0:
        return jsonify({'success': False, 'message': 'Invalid trade parameters'}), 400
    
    account = Account.query.filter_by(user_id=current_user.id).first()
    if not account:
        account = Account(user_id=current_user.id, demo_balance=10000.0)
        db.session.add(account)
        db.session.commit()
    
    if amount > account.demo_balance:
        return jsonify({'success': False, 'message': 'Insufficient demo balance'}), 400
    
    account.demo_balance -= amount
    
    trade = Trade(
        user_id=current_user.id,
        symbol=symbol,
        trade_type=trade_type,
        amount=amount,
        entry_price=entry_price,
        leverage=leverage,
        status='open',
        is_demo=True
    )
    
    db.session.add(trade)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Demo trade placed successfully',
        'trade_id': trade.id,
        'new_balance': account.demo_balance,
        'expiry_seconds': expiry_seconds
    })

@app.route('/api/demo/trade/<int:trade_id>/close', methods=['POST'])
@login_required
def close_demo_trade(trade_id):
    data = request.get_json()
    exit_price = float(data.get('exit_price', 0))
    
    trade = Trade.query.filter_by(id=trade_id, user_id=current_user.id, is_demo=True).first()
    if not trade:
        return jsonify({'success': False, 'message': 'Trade not found'}), 404
    
    if trade.status != 'open':
        return jsonify({'success': False, 'message': 'Trade already closed'}), 400
    
    account = Account.query.filter_by(user_id=current_user.id).first()
    
    price_change_percent = ((exit_price - trade.entry_price) / trade.entry_price) * 100
    
    if trade.trade_type == 'sell':
        price_change_percent = -price_change_percent
    
    leveraged_change = price_change_percent * trade.leverage
    profit_loss = (trade.amount * leveraged_change) / 100
    
    if profit_loss > trade.amount:
        profit_loss = trade.amount * 0.85
    elif profit_loss < -trade.amount:
        profit_loss = -trade.amount
    
    trade.exit_price = exit_price
    trade.profit_loss = profit_loss
    trade.status = 'closed'
    trade.closed_at = datetime.utcnow()
    
    final_return = trade.amount + profit_loss
    if final_return > 0:
        account.demo_balance += final_return
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Trade closed',
        'profit_loss': profit_loss,
        'result': 'win' if profit_loss > 0 else 'loss',
        'new_balance': account.demo_balance
    })

@app.route('/api/demo/trades/open', methods=['GET'])
@login_required
def get_open_demo_trades():
    trades = Trade.query.filter_by(user_id=current_user.id, is_demo=True, status='open').order_by(Trade.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'trades': [{
            'id': t.id,
            'symbol': t.symbol,
            'trade_type': t.trade_type,
            'amount': t.amount,
            'entry_price': t.entry_price,
            'leverage': t.leverage,
            'created_at': t.created_at.isoformat()
        } for t in trades]
    })

@app.route('/api/demo/history', methods=['GET'])
@login_required
def get_demo_history():
    trades = Trade.query.filter_by(user_id=current_user.id, is_demo=True, status='closed').order_by(Trade.closed_at.desc()).limit(50).all()
    
    total_profit = sum(t.profit_loss for t in trades if t.profit_loss > 0)
    total_loss = sum(abs(t.profit_loss) for t in trades if t.profit_loss < 0)
    win_count = sum(1 for t in trades if t.profit_loss > 0)
    loss_count = sum(1 for t in trades if t.profit_loss <= 0)
    
    return jsonify({
        'success': True,
        'trades': [{
            'id': t.id,
            'symbol': t.symbol,
            'trade_type': t.trade_type,
            'amount': t.amount,
            'entry_price': t.entry_price,
            'exit_price': t.exit_price,
            'profit_loss': t.profit_loss,
            'leverage': t.leverage,
            'result': 'win' if t.profit_loss > 0 else 'loss',
            'created_at': t.created_at.isoformat(),
            'closed_at': t.closed_at.isoformat() if t.closed_at else None
        } for t in trades],
        'stats': {
            'total_trades': len(trades),
            'wins': win_count,
            'losses': loss_count,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'net_pnl': total_profit - total_loss,
            'win_rate': (win_count / len(trades) * 100) if trades else 0
        }
    })

@app.route('/api/demo/reset', methods=['POST'])
@login_required
def reset_demo_account():
    account = Account.query.filter_by(user_id=current_user.id).first()
    if not account:
        account = Account(user_id=current_user.id)
        db.session.add(account)
    
    account.demo_balance = 10000.0
    
    Trade.query.filter_by(user_id=current_user.id, is_demo=True, status='open').update({'status': 'cancelled'})
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Demo account reset successfully',
        'new_balance': 10000.0
    })

@app.route('/api/trades/all-history', methods=['GET'])
@login_required
def get_all_trade_history():
    trades = Trade.query.filter_by(user_id=current_user.id, status='closed').order_by(Trade.closed_at.desc()).all()
    
    total_profit = sum(t.profit_loss for t in trades if t.profit_loss > 0)
    total_loss = abs(sum(t.profit_loss for t in trades if t.profit_loss < 0))
    win_count = sum(1 for t in trades if t.profit_loss > 0)
    loss_count = sum(1 for t in trades if t.profit_loss <= 0)
    
    demo_trades = [t for t in trades if t.is_demo]
    live_trades = [t for t in trades if not t.is_demo]
    
    return jsonify({
        'success': True,
        'trades': [{
            'id': t.id,
            'symbol': t.symbol,
            'trade_type': t.trade_type,
            'amount': t.amount,
            'entry_price': t.entry_price,
            'exit_price': t.exit_price,
            'profit_loss': t.profit_loss,
            'leverage': t.leverage,
            'is_demo': t.is_demo,
            'account_type': 'DEMO' if t.is_demo else 'LIVE',
            'result': 'win' if t.profit_loss > 0 else 'loss',
            'created_at': t.created_at.isoformat(),
            'closed_at': t.closed_at.isoformat() if t.closed_at else None
        } for t in trades],
        'stats': {
            'total_trades': len(trades),
            'demo_trades': len(demo_trades),
            'live_trades': len(live_trades),
            'wins': win_count,
            'losses': loss_count,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'net_pnl': total_profit - total_loss,
            'win_rate': (win_count / len(trades) * 100) if trades else 0
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
