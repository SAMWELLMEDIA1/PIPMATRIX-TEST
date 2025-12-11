function paymentModal() {
    return {
        showPaymentModal: false,
        paymentContext: null,
        selectedPaymentMethod: null,

        paymentMethods: [
            { id: 'bank', name: 'Bank Transfer', network: 'Wire Transfer', icon: 'bank', maintenance: true },
            { id: 'BTC', name: 'Bitcoin', network: 'Bitcoin', icon: 'bitcoin', maintenance: false },
            { id: 'ETH', name: 'Ethereum', network: 'Ethereum', icon: 'ethereum', maintenance: false },
            { id: 'BNB', name: 'BNB', network: 'BNB Smart Chain', icon: 'bnb', maintenance: false },
            { id: 'SOL', name: 'Solana', network: 'Solana', icon: 'solana', maintenance: false },
            { id: 'DOGE', name: 'Dogecoin', network: 'Dogecoin', icon: 'dogecoin', maintenance: false },
            { id: 'USDT_TRC20', name: 'USDT', network: 'Tron (TRC20)', icon: 'usdt', maintenance: false },
            { id: 'XRP', name: 'XRP', network: 'XRP Ledger', icon: 'xrp', maintenance: false }
        ],

        openPaymentModal(context) {
            this.paymentContext = context;
            this.showPaymentModal = true;
            this.selectedPaymentMethod = null;
        },

        closePaymentModal() {
            this.showPaymentModal = false;
            this.paymentContext = null;
        },

        selectPaymentMethod(method) {
            if (method.maintenance) {
                this.showBankMaintenanceAlert();
                return;
            }
            
            const params = new URLSearchParams();
            params.set('crypto', method.id);
            if (this.paymentContext?.source) {
                params.set('source', this.paymentContext.source);
            }
            if (this.paymentContext?.amount) {
                params.set('amount', this.paymentContext.amount);
            }
            if (this.paymentContext?.plan) {
                params.set('plan', this.paymentContext.plan);
            }
            
            window.location.href = `DEPOSIT.html?${params.toString()}`;
        },

        showBankMaintenanceAlert() {
            Swal.fire({
                icon: 'info',
                title: 'Bank Transfer Under Maintenance',
                html: `
                    <div class="text-left">
                        <p class="mb-4 text-gray-600 dark:text-gray-300">Bank transfer deposits are currently under maintenance. We're working to enhance this service for you.</p>
                        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
                            <div class="flex items-start gap-3">
                                <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <div>
                                    <p class="text-sm font-medium text-blue-900 dark:text-blue-200">Alternative Option</p>
                                    <p class="text-sm text-blue-800 dark:text-blue-300">You can deposit funds using cryptocurrency with instant confirmation.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `,
                confirmButtonText: 'Use Cryptocurrency',
                confirmButtonColor: '#3B82F6',
                showCancelButton: true,
                cancelButtonText: 'Cancel',
                customClass: {
                    popup: 'dark:bg-gray-800',
                    title: 'dark:text-white',
                    htmlContainer: 'dark:text-gray-300'
                }
            });
        },

        getPaymentIcon(iconName) {
            const icons = {
                'bank': `<svg class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h10m4 0a1 1 0 11-2 0 1 1 0 012 0zM7 15a1 1 0 11-2 0 1 1 0 012 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V7a1 1 0 011-1z"/></svg>`,
                'bitcoin': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#F7931A"/><path d="M22.7 13.2c.3-2-1.2-3.1-3.3-3.8l.7-2.7-1.6-.4-.7 2.7c-.4-.1-.9-.2-1.3-.3l.7-2.7-1.6-.4-.7 2.7c-.3-.1-.7-.2-1-.3l-2.2-.6-.4 1.7s1.2.3 1.2.3c.7.2.8.6.8 1l-2 7.9c-.1.2-.3.5-.8.4 0 0-1.2-.3-1.2-.3l-.8 1.9 2.1.5c.4.1.8.2 1.2.3l-.7 2.7 1.6.4.7-2.7c.5.1.9.2 1.4.3l-.7 2.7 1.6.4.7-2.7c2.8.5 4.9.3 5.8-2.2.7-2-.1-3.2-1.5-4 1.1-.3 1.9-1 2.1-2.5zm-3.8 5.3c-.5 2-3.9.9-5 .7l.9-3.6c1.1.3 4.6.8 4.1 2.9zm.5-5.4c-.5 1.8-3.3.9-4.2.7l.8-3.2c.9.2 3.9.6 3.4 2.5z" fill="#fff"/></svg>`,
                'ethereum': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#627EEA"/><path d="M16.5 4v8.9l7.5 3.3-7.5-12.2z" fill="#fff" fill-opacity=".6"/><path d="M16.5 4L9 16.2l7.5-3.3V4z" fill="#fff"/><path d="M16.5 21.9v6.1L24 17.6l-7.5 4.3z" fill="#fff" fill-opacity=".6"/><path d="M16.5 28v-6.1L9 17.6l7.5 10.4z" fill="#fff"/><path d="M16.5 20.5l7.5-4.3-7.5-3.4v7.7z" fill="#fff" fill-opacity=".2"/><path d="M9 16.2l7.5 4.3v-7.7L9 16.2z" fill="#fff" fill-opacity=".6"/></svg>`,
                'bnb': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#F3BA2F"/><path d="M12.1 14.3L16 10.4l3.9 3.9 2.3-2.3L16 5.8 9.8 12l2.3 2.3zm-2.3 1.7L7.5 16l2.3 2.3 2.3-2.3-2.3-2.3zm6.2 4.4L12.1 16.5l-2.3 2.3L16 25l6.2-6.2-2.3-2.3-3.9 3.9zm6.2-4.4l-2.3 2.3 2.3 2.3 2.3-2.3-2.3-2.3zM16 13.7l-2.3 2.3 2.3 2.3 2.3-2.3-2.3-2.3z" fill="#fff"/></svg>`,
                'solana': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="url(#sol2)"/><defs><linearGradient id="sol2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#00FFA3"/><stop offset="100%" style="stop-color:#DC1FFF"/></linearGradient></defs><path d="M10.3 20.4a.5.5 0 01.4-.2h13.6c.2 0 .4.3.2.5l-2.5 2.5a.5.5 0 01-.4.2H8c-.2 0-.4-.3-.2-.5l2.5-2.5zm0-8.8a.5.5 0 01.4-.2h13.6c.2 0 .4.3.2.5l-2.5 2.5a.5.5 0 01-.4.2H8c-.2 0-.4-.3-.2-.5l2.5-2.5zm11.7 4.2a.5.5 0 00-.4-.2H8c-.2 0-.4.3-.2.5l2.5 2.5a.5.5 0 00.4.2h13.6c.2 0 .4-.3.2-.5L22 15.8z" fill="#fff"/></svg>`,
                'dogecoin': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#C3A634"/><path d="M13 10h3.5c3.3 0 6 2.7 6 6s-2.7 6-6 6H13V10zm2 2v8h1.5c2.2 0 4-1.8 4-4s-1.8-4-4-4H15zm-2 3h6v2h-6v-2z" fill="#fff"/></svg>`,
                'usdt': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#26A17B"/><path d="M17.9 17.9v-2.4c3.3-.2 5.8-1 5.8-2s-2.5-1.8-5.8-2v-1.8h3.4V7.5H10.7v2.2h3.4v1.8c-3.3.2-5.8 1-5.8 2s2.5 1.8 5.8 2v5h3.8v-2.6zm-1.9-.5c-3.2 0-5.8-.8-5.8-1.7s2.6-1.7 5.8-1.7 5.8.8 5.8 1.7-2.6 1.7-5.8 1.7z" fill="#fff"/></svg>`,
                'xrp': `<svg viewBox="0 0 32 32" class="w-8 h-8"><circle cx="16" cy="16" r="16" fill="#23292F"/><path d="M23.1 9h2.5l-5.4 5.2c-1.2 1.1-3.1 1.1-4.3 0L10.4 9h2.5l4 3.8c.6.6 1.5.6 2.1 0L23.1 9zM10.4 23l5.5-5.2c1.2-1.1 3.1-1.1 4.3 0l5.4 5.2h-2.5l-4-3.8c-.6-.6-1.5-.6-2.1 0l-4 3.8h-2.6z" fill="#fff"/></svg>`
            };
            return icons[iconName] || `<div class="w-8 h-8 bg-gray-600 rounded-full"></div>`;
        }
    };
}

function getPaymentModalHTML() {
    return `
    <div x-show="showPaymentModal" 
         class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
         @click.self="closePaymentModal()"
         x-transition:enter="transition ease-out duration-300"
         x-transition:enter-start="opacity-0"
         x-transition:enter-end="opacity-100"
         x-transition:leave="transition ease-in duration-200"
         x-transition:leave-start="opacity-100"
         x-transition:leave-end="opacity-0"
         style="display: none;">
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto"
             x-show="showPaymentModal"
             x-transition:enter="transition ease-out duration-300"
             x-transition:enter-start="opacity-0 scale-95"
             x-transition:enter-end="opacity-100 scale-100"
             x-transition:leave="transition ease-in duration-200"
             x-transition:leave-start="opacity-100 scale-100"
             x-transition:leave-end="opacity-0 scale-95">
            
            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
                <div class="flex items-center justify-between">
                    <div>
                        <h3 class="text-xl font-bold text-gray-900 dark:text-white">Select Payment Method</h3>
                        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1" x-text="paymentContext?.description || 'Choose how you want to pay'"></p>
                    </div>
                    <button @click="closePaymentModal()" class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <template x-if="paymentContext?.amount">
                    <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-blue-700 dark:text-blue-300">Amount to Pay:</span>
                            <span class="text-lg font-bold text-blue-900 dark:text-blue-100" x-text="'$' + parseFloat(paymentContext.amount).toLocaleString()"></span>
                        </div>
                    </div>
                </template>
            </div>
            
            <div class="p-6">
                <div class="grid grid-cols-1 gap-3">
                    <template x-for="method in paymentMethods" :key="method.id">
                        <button @click="selectPaymentMethod(method)"
                                class="flex items-center p-4 rounded-xl border-2 transition-all duration-200 group"
                                :class="method.maintenance 
                                    ? 'bg-gray-50 dark:bg-gray-700/30 border-gray-200 dark:border-gray-700 opacity-60 hover:opacity-80' 
                                    : 'bg-gray-50 dark:bg-gray-700/50 border-transparent hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20'">
                            <div class="flex-shrink-0 mr-4" x-html="getPaymentIcon(method.icon)"></div>
                            <div class="text-left flex-1">
                                <div class="font-semibold text-gray-900 dark:text-white" x-text="method.name"></div>
                                <div class="text-sm text-gray-500 dark:text-gray-400" x-text="method.network"></div>
                            </div>
                            <template x-if="method.maintenance">
                                <span class="px-2 py-1 text-xs font-semibold bg-yellow-500 text-white rounded-lg">MAINTENANCE</span>
                            </template>
                            <template x-if="!method.maintenance">
                                <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                                </svg>
                            </template>
                        </button>
                    </template>
                </div>
                
                <div class="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-xl border border-amber-200 dark:border-amber-800">
                    <div class="flex items-start gap-3">
                        <svg class="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                        </svg>
                        <div>
                            <p class="text-sm font-medium text-amber-800 dark:text-amber-200">Secure Payment</p>
                            <p class="text-xs text-amber-700 dark:text-amber-300 mt-1">All cryptocurrency transactions are verified on the blockchain for maximum security.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `;
}

window.paymentModal = paymentModal;
window.getPaymentModalHTML = getPaymentModalHTML;
