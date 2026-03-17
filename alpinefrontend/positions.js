document.addEventListener('alpine:init', () => {
    Alpine.data('portfolioApp', () => ({
        positions: [],
        totals: [],
        isLoading: false,
        error: null,
        statusFilter: 'all',
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
                await Promise.all([
                    this.fetchPositions(),
                    this.fetchTotals()
                ]);
            } catch (err) {
                console.error("Failed to fetch data:", err);
                this.error = "Failed to load portfolio data. Make sure the backend Server is running on port 8000.";
            } finally {
                this.isLoading = false;
            }
        },

        async fetchPositions() {
            const url = `http://localhost:8000/api/positions?status_filter=${this.statusFilter}&account_name=${this.selectedAccount}`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.positions = await response.json();
        },

        async fetchTotals() {
            const url = `http://localhost:8000/api/positions/totals?status_filter=${this.statusFilter}&account_name=${this.selectedAccount}`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.totals = await response.json();
        },

        get filteredPositions() {
            if (this.searchQuery === '') return this.positions;

            const q = this.searchQuery.toLowerCase();
            return this.positions.filter(pos => {
                const nameMatch = (pos.instrument_name || '').toLowerCase().includes(q);
                const tickerMatch = (pos.instrument_ticker || '').toLowerCase().includes(q);
                const isinMatch = (pos.instrument_isin || '').toLowerCase().includes(q);
                return nameMatch || tickerMatch || isinMatch;
            });
        },

        // Formatters mapping (using shared utils)
        formatMoney: window.utils.formatMoney,
        formatPercent: window.utils.formatPercent,
        formatDate: window.utils.formatDate,
        getColorClass: window.utils.getColorClass
    }));
});
