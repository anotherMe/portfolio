document.addEventListener('alpine:init', () => {
    Alpine.data('tradesApp', () => ({
        trades: [],
        isLoading: false,
        error: null,
        searchQuery: '',

        // Account filtering
        selectedAccount: '',
        accounts: [],

        async init() {
            this.accounts = await window.utils.fetchAccounts();
            // Restore selection AFTER accounts are loaded so Alpine.js finds the option
            await this.$nextTick();
            this.selectedAccount = window.utils.state.selectedAccount;
            this.fetchData();

            // Listen for changes from other components (if any)
            window.addEventListener('account-changed', (e) => {
                this.selectedAccount = e.detail;
                this.fetchData();
            });
        },

        updateAccount() {
            window.utils.state.selectedAccount = this.selectedAccount;
            this.fetchData();
        },

        async fetchData() {
            this.isLoading = true;
            this.error = null;
            try {
                const url = `http://localhost:8000/api/trades?account_name=${this.selectedAccount}`;
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                this.trades = await response.json();
            } catch (err) {
                console.error("Failed to fetch trades:", err);
                this.error = "Failed to load trades. Make sure the backend Server is running on port 8000.";
            } finally {
                this.isLoading = false;
            }
        },

        get filteredTrades() {
            if (this.searchQuery === '') return this.trades;

            const q = this.searchQuery.toLowerCase();
            return this.trades.filter(t => {
                const typeMatch = (t.type || '').toLowerCase().includes(q);
                const descMatch = (t.description || '').toLowerCase().includes(q);
                return typeMatch || descMatch;
            });
        },

        // Formatters mapping (using shared utils)
        formatMoney: window.utils.formatMoney,
        formatDate: window.utils.formatDate,
        getColorClass: window.utils.getColorClass
    }));
});
