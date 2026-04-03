document.addEventListener('alpine:init', () => {
    Alpine.data('portfolioApp', () => ({
        positions: [],
        totals: [],
        isLoading: false,
        error: null,
        statusMode: 'all',
        searchQuery: '',

        // Account filtering
        selectedAccount: '',
        accounts: [],

        get includeOpen() { return this.statusMode !== 'closed'; },
        get includeClosed() { return this.statusMode !== 'open'; },
        get selectedAccountId() {
            if (!this.selectedAccount || this.selectedAccount === 'All') return null;
            const acc = this.accounts.find(a => a.name === this.selectedAccount);
            return acc ? acc.id : null;
        },

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
            const params = new URLSearchParams({ include_open: this.includeOpen, include_closed: this.includeClosed });
            if (this.selectedAccountId) params.append('account_id', this.selectedAccountId);
            const response = await fetch(`http://localhost:8000/positions?${params}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            this.positions = await response.json();
        },

        async fetchTotals() {
            const params = new URLSearchParams({ include_open: this.includeOpen, include_closed: this.includeClosed });
            if (this.selectedAccountId) params.append('account_id', this.selectedAccountId);
            const response = await fetch(`http://localhost:8000/positions/totals?${params}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
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
