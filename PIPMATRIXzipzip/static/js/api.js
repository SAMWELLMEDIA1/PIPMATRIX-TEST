const API_BASE = '/api';

const api = {
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include',
            ...options
        };
        
        if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
            config.body = JSON.stringify(options.body);
        } else if (options.body instanceof FormData) {
            delete config.headers['Content-Type'];
            config.body = options.body;
        }
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    auth: {
        async register(userData) {
            return api.request('/auth/register', {
                method: 'POST',
                body: userData
            });
        },

        async login(email, password, remember = false) {
            return api.request('/auth/login', {
                method: 'POST',
                body: { email, password, remember }
            });
        },

        async logout() {
            return api.request('/auth/logout', { method: 'POST' });
        },

        async check() {
            return api.request('/auth/check');
        }
    },

    user: {
        async getProfile() {
            return api.request('/user/profile');
        },

        async updateProfile(data) {
            return api.request('/user/profile', {
                method: 'PUT',
                body: data
            });
        }
    },

    dashboard: {
        async get() {
            return api.request('/dashboard');
        }
    },

    transactions: {
        async getAll(page = 1, type = null) {
            let url = `/transactions?page=${page}`;
            if (type) url += `&type=${type}`;
            return api.request(url);
        },

        async deposit(amount, paymentMethod, walletAddress) {
            return api.request('/deposit', {
                method: 'POST',
                body: { amount, payment_method: paymentMethod, wallet_address: walletAddress }
            });
        },

        async withdraw(amount, paymentMethod, walletAddress, cryptoType = null, cryptoNetwork = null) {
            return api.request('/withdraw', {
                method: 'POST',
                body: { 
                    amount, 
                    payment_method: paymentMethod, 
                    wallet_address: walletAddress,
                    crypto_type: cryptoType,
                    crypto_network: cryptoNetwork
                }
            });
        },

        async transfer(amount, recipient) {
            return api.request('/transfer', {
                method: 'POST',
                body: { amount, recipient }
            });
        }
    },

    crypto: {
        async getWallets() {
            return api.request('/crypto/wallets');
        },

        async getWallet(cryptoId) {
            return api.request(`/crypto/wallet/${cryptoId}`);
        },

        async submitDeposit(formData) {
            return api.request('/deposit/crypto', {
                method: 'POST',
                body: formData
            });
        },

        async submitDepositJson(data) {
            return api.request('/deposit/crypto', {
                method: 'POST',
                body: data
            });
        }
    },

    investments: {
        async getAll() {
            return api.request('/investments');
        },

        async create(planName, planType, amount, durationDays, roi) {
            return api.request('/investments', {
                method: 'POST',
                body: { plan_name: planName, plan_type: planType, amount, duration_days: durationDays, roi }
            });
        }
    },

    trades: {
        async getAll(demo = false, status = null) {
            let url = `/trades?demo=${demo}`;
            if (status) url += `&status=${status}`;
            return api.request(url);
        },

        async create(symbol, tradeType, amount, entryPrice, leverage = 1, isDemo = false) {
            return api.request('/trades', {
                method: 'POST',
                body: { symbol, trade_type: tradeType, amount, entry_price: entryPrice, leverage, is_demo: isDemo }
            });
        },

        async close(tradeId, exitPrice) {
            return api.request(`/trades/${tradeId}/close`, {
                method: 'POST',
                body: { exit_price: exitPrice }
            });
        }
    },

    loans: {
        async getAll() {
            return api.request('/loans');
        },

        async create(amount, durationMonths, interestRate, purpose) {
            return api.request('/loans', {
                method: 'POST',
                body: { amount, duration_months: durationMonths, interest_rate: interestRate, purpose }
            });
        }
    },

    copyTrading: {
        async getAll() {
            return api.request('/copy-trading');
        },

        async start(traderName, amount, profitShare = 20) {
            return api.request('/copy-trading', {
                method: 'POST',
                body: { trader_name: traderName, amount, profit_share: profitShare }
            });
        }
    },

    botTrading: {
        async getAll() {
            return api.request('/bot-trading');
        },

        async start(botName, strategy, amount) {
            return api.request('/bot-trading', {
                method: 'POST',
                body: { bot_name: botName, strategy, amount }
            });
        }
    },

    support: {
        async getTickets() {
            return api.request('/support');
        },

        async createTicket(subject, message, priority = 'medium') {
            return api.request('/support', {
                method: 'POST',
                body: { subject, message, priority }
            });
        }
    },

    referral: {
        async get() {
            return api.request('/referral');
        }
    }
};

async function checkAuth() {
    try {
        const result = await api.auth.check();
        return result.authenticated;
    } catch {
        return false;
    }
}

async function requireAuth() {
    const isAuth = await checkAuth();
    if (!isAuth) {
        window.location.href = 'LOGIN.html';
        return false;
    }
    return true;
}

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transition-all transform translate-x-full`;
    
    const colors = {
        success: 'bg-green-600 text-white',
        error: 'bg-red-600 text-white',
        warning: 'bg-yellow-600 text-white',
        info: 'bg-blue-600 text-white'
    };
    
    notification.classList.add(...colors[type].split(' '));
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.remove('translate-x-full'), 100);
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function userData() {
    return {
        user: null,
        fullName: '',
        firstName: '',
        email: '',
        phone: '',
        country: '',
        username: '',
        balance: '$0.00',
        totalProfit: '$0.00',
        totalDeposits: '$0.00',
        totalWithdrawals: '$0.00',
        avatarUrl: 'https://ui-avatars.com/api/?name=User&color=7F9CF5&background=EBF4FF',
        avatarInitials: 'U',
        loading: true,
        deposits: [],
        withdrawals: [],
        transactions: [],
        notifications: [],
        depositHistory: [],
        trades: [],
        notificationCount: 0,
        
        async init() {
            await this.loadUserData();
            await this.loadNotifications();
            await this.loadDepositHistory();
            await this.loadTrades();
        },
        
        async loadNotifications() {
            try {
                const data = await api.request('/notifications');
                if (data.success && data.notifications) {
                    this.notifications = data.notifications;
                    this.notificationCount = data.notifications.length;
                }
            } catch (error) {
                console.error('Failed to load notifications:', error);
                this.notifications = [];
            }
        },
        
        async loadDepositHistory() {
            try {
                const data = await api.transactions.getAll(1, 'deposit');
                if (data.success && data.transactions) {
                    this.depositHistory = data.transactions;
                }
            } catch (error) {
                console.error('Failed to load deposit history:', error);
                this.depositHistory = [];
            }
        },
        
        async loadTrades() {
            try {
                const data = await api.request('/trades?demo=false');
                if (data.success && data.trades) {
                    this.trades = data.trades;
                }
            } catch (error) {
                console.error('Failed to load trades:', error);
                this.trades = [];
            }
        },
        
        async loadUserData() {
            try {
                const authCheck = await api.auth.check();
                if (!authCheck.authenticated) {
                    window.location.href = 'LOGIN.html';
                    return;
                }
                
                const profileData = await api.user.getProfile();
                if (profileData.success && profileData.user) {
                    this.user = profileData.user;
                    this.fullName = profileData.user.full_name || profileData.user.username || 'User';
                    this.firstName = this.fullName.split(' ')[0];
                    this.email = profileData.user.email || '';
                    this.phone = profileData.user.phone || '';
                    this.country = profileData.user.country || '';
                    this.username = profileData.user.username || '';
                    
                    const bal = parseFloat(profileData.user.balance) || 0;
                    const profit = parseFloat(profileData.user.total_profit) || 0;
                    const deposits = parseFloat(profileData.user.total_deposits) || 0;
                    const withdrawals = parseFloat(profileData.user.total_withdrawals) || 0;
                    
                    this.balance = formatCurrency(bal);
                    this.totalProfit = formatCurrency(profit);
                    this.totalDeposits = formatCurrency(deposits);
                    this.totalWithdrawals = formatCurrency(withdrawals);
                    
                    const initials = this.fullName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
                    this.avatarInitials = initials || 'U';
                    this.avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(initials)}&color=7F9CF5&background=EBF4FF`;
                } else {
                    console.error('Failed to load profile data');
                    showNotification('Failed to load profile data', 'error');
                }
                this.loading = false;
            } catch (error) {
                console.error('Failed to load user data:', error);
                this.loading = false;
                if (error.message && error.message.includes('unauthorized')) {
                    window.location.href = 'LOGIN.html';
                } else {
                    showNotification('Error loading user data. Please refresh.', 'error');
                }
            }
        },
        
        async handleLogout() {
            try {
                await api.auth.logout();
                window.location.href = 'LOGIN.html';
            } catch (e) {
                window.location.href = 'LOGIN.html';
            }
        }
    };
}

function cryptoPayment() {
    return {
        wallets: [],
        selectedCrypto: null,
        amount: '',
        txid: '',
        receiptFile: null,
        loading: false,
        submitting: false,
        step: 1,
        depositHistory: [],

        async init() {
            this.loading = true;
            try {
                const [walletsData, historyData] = await Promise.all([
                    api.crypto.getWallets(),
                    api.transactions.getAll(1, 'deposit')
                ]);
                if (walletsData.success) {
                    this.wallets = walletsData.wallets;
                }
                if (historyData.success && historyData.transactions) {
                    this.depositHistory = historyData.transactions;
                }
            } catch (error) {
                console.error('Failed to load data:', error);
                showNotification('Failed to load payment options', 'error');
            }
            this.loading = false;
        },

        selectCrypto(wallet) {
            this.selectedCrypto = wallet;
            this.step = 2;
        },

        goBack() {
            if (this.step > 1) {
                this.step--;
                if (this.step === 1) {
                    this.selectedCrypto = null;
                }
            }
        },

        proceedToPayment() {
            if (!this.amount || parseFloat(this.amount) <= 0) {
                showNotification('Please enter a valid amount', 'error');
                return;
            }
            this.step = 3;
        },

        handleFileChange(event) {
            const file = event.target.files[0];
            if (file) {
                const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
                if (!allowedTypes.includes(file.type)) {
                    showNotification('Invalid file type. Please upload JPG, PNG, GIF, or PDF', 'error');
                    return;
                }
                if (file.size > 10 * 1024 * 1024) {
                    showNotification('File too large. Maximum 10MB allowed', 'error');
                    return;
                }
                this.receiptFile = file;
            }
        },

        async copyAddress() {
            try {
                await navigator.clipboard.writeText(this.selectedCrypto.address);
                showNotification('Wallet address copied!', 'success');
            } catch (error) {
                const input = document.createElement('input');
                input.value = this.selectedCrypto.address;
                document.body.appendChild(input);
                input.select();
                document.execCommand('copy');
                document.body.removeChild(input);
                showNotification('Wallet address copied!', 'success');
            }
        },

        async submitDeposit() {
            if (!this.txid) {
                showNotification('Please enter the transaction hash (TXID)', 'error');
                return;
            }

            this.submitting = true;

            try {
                let result;
                
                if (this.receiptFile) {
                    // Use FormData when there's a file
                    const formData = new FormData();
                    formData.append('amount', this.amount);
                    formData.append('crypto_type', this.selectedCrypto.id);
                    formData.append('txid', this.txid);
                    formData.append('receipt', this.receiptFile);
                    result = await api.crypto.submitDeposit(formData);
                } else {
                    // Use JSON when no file
                    result = await api.crypto.submitDepositJson({
                        amount: parseFloat(this.amount),
                        crypto_type: this.selectedCrypto.id,
                        txid: this.txid
                    });
                }
                
                if (result.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Deposit Submitted!',
                        text: `Your ${this.selectedCrypto.name} deposit of $${this.amount} has been submitted. Reference: ${result.reference}`,
                        confirmButtonColor: '#3B82F6'
                    }).then(() => {
                        window.location.href = 'ACCOUNTHISTORY.html';
                    });
                } else {
                    showNotification(result.message || 'Failed to submit deposit', 'error');
                }
            } catch (error) {
                console.error('Deposit submission error:', error);
                showNotification(error.message || 'Failed to submit deposit', 'error');
            }

            this.submitting = false;
        },

        getCryptoIcon(iconName) {
            const icons = {
                'bitcoin': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#F7931A"/><path d="M22.7 13.2c.3-2-1.2-3.1-3.3-3.8l.7-2.7-1.6-.4-.7 2.7c-.4-.1-.9-.2-1.3-.3l.7-2.7-1.6-.4-.7 2.7c-.3-.1-.7-.2-1-.3l-2.2-.6-.4 1.7s1.2.3 1.2.3c.7.2.8.6.8 1l-2 7.9c-.1.2-.3.5-.8.4 0 0-1.2-.3-1.2-.3l-.8 1.9 2.1.5c.4.1.8.2 1.2.3l-.7 2.7 1.6.4.7-2.7c.5.1.9.2 1.4.3l-.7 2.7 1.6.4.7-2.7c2.8.5 4.9.3 5.8-2.2.7-2-.1-3.2-1.5-4 1.1-.3 1.9-1 2.1-2.5zm-3.8 5.3c-.5 2-3.9.9-5 .7l.9-3.6c1.1.3 4.6.8 4.1 2.9zm.5-5.4c-.5 1.8-3.3.9-4.2.7l.8-3.2c.9.2 3.9.6 3.4 2.5z" fill="#fff"/></svg>`,
                'ethereum': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#627EEA"/><path d="M16.5 4v8.9l7.5 3.3-7.5-12.2z" fill="#fff" fill-opacity=".6"/><path d="M16.5 4L9 16.2l7.5-3.3V4z" fill="#fff"/><path d="M16.5 21.9v6.1L24 17.6l-7.5 4.3z" fill="#fff" fill-opacity=".6"/><path d="M16.5 28v-6.1L9 17.6l7.5 10.4z" fill="#fff"/><path d="M16.5 20.5l7.5-4.3-7.5-3.4v7.7z" fill="#fff" fill-opacity=".2"/><path d="M9 16.2l7.5 4.3v-7.7L9 16.2z" fill="#fff" fill-opacity=".6"/></svg>`,
                'bnb': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#F3BA2F"/><path d="M12.1 14.3L16 10.4l3.9 3.9 2.3-2.3L16 5.8 9.8 12l2.3 2.3zm-2.3 1.7L7.5 16l2.3 2.3 2.3-2.3-2.3-2.3zm6.2 4.4L12.1 16.5l-2.3 2.3L16 25l6.2-6.2-2.3-2.3-3.9 3.9zm6.2-4.4l-2.3 2.3 2.3 2.3 2.3-2.3-2.3-2.3zM16 13.7l-2.3 2.3 2.3 2.3 2.3-2.3-2.3-2.3z" fill="#fff"/></svg>`,
                'solana': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="url(#sol)"/><defs><linearGradient id="sol" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#00FFA3"/><stop offset="100%" style="stop-color:#DC1FFF"/></linearGradient></defs><path d="M10.3 20.4a.5.5 0 01.4-.2h13.6c.2 0 .4.3.2.5l-2.5 2.5a.5.5 0 01-.4.2H8c-.2 0-.4-.3-.2-.5l2.5-2.5zm0-8.8a.5.5 0 01.4-.2h13.6c.2 0 .4.3.2.5l-2.5 2.5a.5.5 0 01-.4.2H8c-.2 0-.4-.3-.2-.5l2.5-2.5zm11.7 4.2a.5.5 0 00-.4-.2H8c-.2 0-.4.3-.2.5l2.5 2.5a.5.5 0 00.4.2h13.6c.2 0 .4-.3.2-.5L22 15.8z" fill="#fff"/></svg>`,
                'dogecoin': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#C3A634"/><path d="M13 10h3.5c3.3 0 6 2.7 6 6s-2.7 6-6 6H13V10zm2 2v8h1.5c2.2 0 4-1.8 4-4s-1.8-4-4-4H15zm-2 3h6v2h-6v-2z" fill="#fff"/></svg>`,
                'usdt': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#26A17B"/><path d="M17.9 17.9v-2.4c3.3-.2 5.8-1 5.8-2s-2.5-1.8-5.8-2v-1.8h3.4V7.5H10.7v2.2h3.4v1.8c-3.3.2-5.8 1-5.8 2s2.5 1.8 5.8 2v5h3.8v-2.6zm-1.9-.5c-3.2 0-5.8-.8-5.8-1.7s2.6-1.7 5.8-1.7 5.8.8 5.8 1.7-2.6 1.7-5.8 1.7z" fill="#fff"/></svg>`,
                'xrp': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#23292F"/><path d="M23.1 9h2.5l-5.4 5.2c-1.2 1.1-3.1 1.1-4.3 0L10.4 9h2.5l4 3.8c.6.6 1.5.6 2.1 0L23.1 9zM10.4 23l5.5-5.2c1.2-1.1 3.1-1.1 4.3 0l5.4 5.2h-2.5l-4-3.8c-.6-.6-1.5-.6-2.1 0l-4 3.8h-2.6z" fill="#fff"/></svg>`
            };
            return icons[iconName] || `<div class="w-8 h-8 bg-gray-600 rounded-full"></div>`;
        }
    };
}

function withdrawalHistory() {
    return {
        withdrawals: [],
        loading: false,
        
        async loadWithdrawals() {
            this.loading = true;
            try {
                const data = await api.transactions.getAll(1, 'withdrawal');
                if (data.success && data.transactions) {
                    this.withdrawals = data.transactions.map(t => ({
                        id: t.id,
                        amount: t.amount,
                        date: new Date(t.created_at).toLocaleDateString('en-US', {year: 'numeric', month: 'short', day: 'numeric'}),
                        time: new Date(t.created_at).toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'}),
                        method: t.crypto_type || t.payment_method || 'Crypto',
                        status: t.status === 'approved' ? 'Completed' : (t.status === 'rejected' ? 'Rejected' : 'Pending')
                    }));
                }
            } catch (error) {
                console.error('Failed to load withdrawals:', error);
                this.withdrawals = [];
            }
            this.loading = false;
        }
    };
}

window.api = api;
window.checkAuth = checkAuth;
window.requireAuth = requireAuth;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.showNotification = showNotification;
window.userData = userData;
window.cryptoPayment = cryptoPayment;
window.withdrawalHistory = withdrawalHistory;
