// Shared Utility Functions for PIP

window.utils = {
    formatMoney(value, symbol = '') {
        if (value === null || value === undefined) return '-';
        const formatter = new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        return `${formatter.format(value)} ${symbol}`;
    },

    formatPercent(value) {
        if (value === null || value === undefined) return '-';
        const formatter = new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        return `${formatter.format(value * 100)} %`;
    },

    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '';

        // Format to YYYY-MM-DD HH:MM:SS
        const y = date.getFullYear();
        const m = String(date.getMonth() + 1).padStart(2, '0');
        const d = String(date.getDate()).padStart(2, '0');
        const hh = String(date.getHours()).padStart(2, '0');
        const mm = String(date.getMinutes()).padStart(2, '0');
        const ss = String(date.getSeconds()).padStart(2, '0');

        return `${y}-${m}-${d} ${hh}:${mm}:${ss}`;
    },

    getColorClass(value) {
        if (value > 0) return 'positive';
        if (value < 0) return 'negative';
        return 'neutral';
    },

    // Shared State management
    state: {
        _selectedAccount: localStorage.getItem('selectedAccount') || 'All',

        get selectedAccount() {
            return this._selectedAccount;
        },

        set selectedAccount(value) {
            this._selectedAccount = value;
            localStorage.setItem('selectedAccount', value);
            // Dispatch event so other components can react
            window.dispatchEvent(new CustomEvent('account-changed', { detail: value }));
        }
    },

    async fetchAccounts() {
        try {
            const response = await fetch('http://localhost:8000/api/accounts');
            if (!response.ok) throw new Error('Failed to fetch accounts');
            return await response.json();
        } catch (err) {
            console.error(err);
            return [];
        }
    },

    async fetchInstruments() {
        try {
            const response = await fetch('http://localhost:8000/api/instruments');
            if (!response.ok) throw new Error('Failed to fetch instruments');
            return await response.json();
        } catch (err) {
            console.error(err);
            return [];
        }
    }
};
