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
        
        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
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

        async withdraw(amount, paymentMethod, walletAddress) {
            return api.request('/withdraw', {
                method: 'POST',
                body: { amount, payment_method: paymentMethod, wallet_address: walletAddress }
            });
        },

        async transfer(amount, recipient) {
            return api.request('/transfer', {
                method: 'POST',
                body: { amount, recipient }
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
        notificationCount: 0,
        
        async init() {
            await this.loadUserData();
            await this.loadNotifications();
            await this.loadDepositHistory();
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
