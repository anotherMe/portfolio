document.addEventListener('alpine:init', () => {
    Alpine.data('accountsApp', () => ({
        accountsData: [],
        isLoading: false,
        error: null,
        searchQuery: '',

        async init() {
            this.fetchData();
        },

        async fetchData() {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await fetch("http://localhost:8000/api/accounts");
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                this.accountsData = await response.json();
            } catch (err) {
                console.error("Failed to fetch accounts:", err);
                this.error = "Failed to load accounts. Make sure the backend Server is running on port 8000.";
            } finally {
                this.isLoading = false;
            }
        },

        get filteredAccounts() {
            let list = this.accountsData;

            if (this.searchQuery === '') return list;

            const q = this.searchQuery.toLowerCase();
            return list.filter(a => {
                const nameMatch = (a.name || '').toLowerCase().includes(q);
                const descMatch = (a.description || '').toLowerCase().includes(q);
                return nameMatch || descMatch;
            });
        }
    }));
});
