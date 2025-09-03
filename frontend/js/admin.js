// Campus Climb Admin Panel JavaScript
class AdminPanel {
    constructor() {
        this.apiBaseUrl = window.APP_CONFIG ? window.APP_CONFIG.apiBaseUrl : 'http://localhost:8000/api';
        this.isAuthenticated = false;
        this.currentSection = 'dashboard';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuthStatus();
    }

    setupEventListeners() {
        // Admin login form
        document.getElementById('adminLoginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleAdminLogin();
        });

        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.target.dataset.section;
                this.showSection(section);
            });
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });

        // CSV management
        document.getElementById('uploadCsvBtn').addEventListener('click', () => {
            this.uploadCsv();
        });

        document.getElementById('exportCsvBtn').addEventListener('click', () => {
            this.exportCsv();
        });

        document.getElementById('reloadCsvBtn').addEventListener('click', () => {
            this.reloadCsv();
        });

        // Add opportunity button
        document.getElementById('addOpportunityBtn').addEventListener('click', () => {
            this.showAddOpportunityModal();
        });

        // Opportunity form
        document.getElementById('opportunityForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleOpportunitySubmit();
        });

        // Modal buttons
        document.getElementById('cancelOpportunityBtn').addEventListener('click', () => {
            this.hideOpportunityModal();
        });

        document.getElementById('cancelDeleteBtn').addEventListener('click', () => {
            this.hideDeleteModal();
        });

        document.getElementById('confirmDeleteBtn').addEventListener('click', () => {
            this.confirmDeleteOpportunity();
        });
    }

    checkAuthStatus() {
        // Check if admin is already logged in
        const adminEmail = localStorage.getItem('adminEmail');
        const adminEmails = ['qhestoemoyo@gmail.com', 'chiwalenatwange@gmail.com'];
        if (adminEmails.includes(adminEmail)) {
            this.isAuthenticated = true;
            this.showAdminDashboard();
        } else {
            this.showAdminLogin();
        }
    }

    async handleAdminLogin() {
        const email = document.getElementById('adminEmail').value;
        const password = document.getElementById('adminPassword').value;

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.isAuthenticated = true;
                localStorage.setItem('adminEmail', email);
                this.showAdminDashboard();
                this.showMessage('Admin login successful!', 'success');
            } else {
                this.showMessage(data.error || 'Invalid admin credentials.', 'error', 'adminLoginMessage');
            }
        } catch (error) {
            console.error('Admin login error:', error);
            this.showMessage('Login failed. Please check your connection and try again.', 'error', 'adminLoginMessage');
        }
    }

    showAdminLogin() {
        document.getElementById('adminLoginModal').classList.remove('hidden');
        document.getElementById('adminDashboard').classList.add('hidden');
        this.clearLoginForm();
    }

    showAdminDashboard() {
        document.getElementById('adminLoginModal').classList.add('hidden');
        document.getElementById('adminDashboard').classList.remove('hidden');
        this.loadDashboardData();
    }

    logout() {
        this.isAuthenticated = false;
        localStorage.removeItem('adminEmail');
        this.showAdminLogin();
        this.clearLoginForm();
        this.showMessage('Logged out successfully!', 'success');
    }

    clearLoginForm() {
        // Clear the login form fields
        document.getElementById('adminEmail').value = '';
        document.getElementById('adminPassword').value = '';
        document.getElementById('adminLoginMessage').textContent = '';
    }

    showSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Hide all sections
        document.querySelectorAll('.admin-section').forEach(sectionEl => {
            sectionEl.classList.add('hidden');
        });

        // Show selected section
        document.getElementById(`${section}Section`).classList.remove('hidden');
        this.currentSection = section;

        // Load section-specific data
        switch (section) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'opportunities':
                this.loadOpportunities();
                break;
            case 'users':
                this.loadUsers();
                break;
            case 'csv':
                // CSV section doesn't need initial data load
                break;
        }
    }

    async loadDashboardData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/dashboard`);
            const data = await response.json();

            if (response.ok) {
                this.updateDashboardStats(data);
                this.updateRecentUsers(data.recent_users);
                this.updateRecentOpportunities(data.recent_opportunities);
            } else {
                console.error('Failed to load dashboard data:', data.error);
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    updateDashboardStats(data) {
        document.getElementById('totalUsers').textContent = data.total_users;
        document.getElementById('totalOpportunities').textContent = data.total_opportunities;
        document.getElementById('activeCategories').textContent = this.getUniqueCategories(data.recent_opportunities);
        document.getElementById('recentActivity').textContent = data.recent_users.length + data.recent_opportunities.length;
    }

    getUniqueCategories(opportunities) {
        const categories = new Set(opportunities.map(opp => opp.category));
        return categories.size;
    }

    updateRecentUsers(users) {
        const container = document.getElementById('recentUsers');
        container.innerHTML = '';

        users.forEach(user => {
            const userEl = document.createElement('div');
            userEl.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg';
            userEl.innerHTML = `
                <div>
                    <p class="font-medium text-gray-900">${user.first_name} ${user.last_name}</p>
                    <p class="text-sm text-gray-600">${user.email}</p>
                </div>
                <span class="text-xs text-gray-500">${new Date(user.created_at).toLocaleDateString()}</span>
            `;
            container.appendChild(userEl);
        });
    }

    updateRecentOpportunities(opportunities) {
        const container = document.getElementById('recentOpportunities');
        container.innerHTML = '';

        opportunities.forEach(opp => {
            const oppEl = document.createElement('div');
            oppEl.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg';
            oppEl.innerHTML = `
                <div>
                    <p class="font-medium text-gray-900">${opp.title}</p>
                    <p class="text-sm text-gray-600">${opp.company}</p>
                </div>
                <span class="text-xs text-gray-500">${opp.type}</span>
            `;
            container.appendChild(oppEl);
        });
    }

    async loadOpportunities() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/opportunities`);
            const opportunities = await response.json();

            if (response.ok) {
                this.renderOpportunitiesTable(opportunities);
            } else {
                console.error('Failed to load opportunities:', opportunities.error);
            }
        } catch (error) {
            console.error('Error loading opportunities:', error);
        }
    }

    renderOpportunitiesTable(opportunities) {
        const tbody = document.getElementById('opportunitiesTable');
        tbody.innerHTML = '';

        opportunities.forEach(opp => {
            const row = this.createOpportunityRow(opp);
            tbody.appendChild(row);
        });
    }

    async loadUsers() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/users`);
            const users = await response.json();

            if (response.ok) {
                this.renderUsersTable(users);
            } else {
                console.error('Failed to load users:', users.error);
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    renderUsersTable(users) {
        const tbody = document.getElementById('usersTable');
        tbody.innerHTML = '';

        users.forEach(user => {
            const row = document.createElement('tr');
            row.className = 'table-row border-b border-gray-200';
            row.innerHTML = `
                <td class="py-3 px-4">
                    <div>
                        <p class="font-medium text-gray-900">${user.first_name} ${user.last_name}</p>
                    </div>
                </td>
                <td class="py-3 px-4 text-gray-700">${user.email}</td>
                <td class="py-3 px-4 text-gray-700">${new Date(user.created_at).toLocaleDateString()}</td>
                <td class="py-3 px-4">
                    <button onclick="adminPanel.deleteUser(${user.id})" class="text-red-600 hover:text-red-700 text-sm font-medium">
                        🗑️ Delete
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user?')) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/users/${userId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showMessage('User deleted successfully!', 'success');
                this.loadUsers();
                this.loadDashboardData();
            } else {
                const data = await response.json();
                this.showMessage(data.error || 'Failed to delete user.', 'error');
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            this.showMessage('Failed to delete user.', 'error');
        }
    }

    async deleteOpportunity(oppId) {
        if (!confirm('Are you sure you want to delete this opportunity?')) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/opportunities/${oppId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showMessage('Opportunity deleted successfully!', 'success');
                this.loadOpportunities();
                this.loadDashboardData();
            } else {
                const data = await response.json();
                this.showMessage(data.error || 'Failed to delete opportunity.', 'error');
            }
        } catch (error) {
            console.error('Error deleting opportunity:', error);
            this.showMessage('Failed to delete opportunity.', 'error');
        }
    }

    async uploadCsv() {
        const fileInput = document.getElementById('csvFileInput');
        const file = fileInput.files[0];

        if (!file) {
            this.showMessage('Please select a CSV file.', 'error');
            return;
        }

        // For now, we'll just reload the existing CSV
        // In a full implementation, you'd upload the file to the server
        this.reloadCsv();
    }

    async exportCsv() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/export-csv`);
            const data = await response.json();

            if (response.ok) {
                this.downloadCsv(data.csv_data);
            } else {
                this.showMessage(data.error || 'Failed to export CSV.', 'error');
            }
        } catch (error) {
            console.error('Error exporting CSV:', error);
            this.showMessage('Failed to export CSV.', 'error');
        }
    }

    downloadCsv(csvData) {
        const headers = ['title', 'company', 'location', 'type', 'category', 'description', 'requirements', 'salary', 'deadline', 'application_url'];
        const csvContent = [
            headers.join(','),
            ...csvData.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'campus_climb_opportunities.csv';
        a.click();
        window.URL.revokeObjectURL(url);

        this.showMessage('CSV exported successfully!', 'success');
    }

    async reloadCsv() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/load-csv`, {
                method: 'POST'
            });

            const data = await response.json();

            if (response.ok) {
                this.showMessage('CSV data reloaded successfully!', 'success');
                this.loadDashboardData();
                if (this.currentSection === 'opportunities') {
                    this.loadOpportunities();
                }
            } else {
                this.showMessage(data.error || 'Failed to reload CSV data.', 'error');
            }
        } catch (error) {
            console.error('Error reloading CSV:', error);
            this.showMessage('Failed to reload CSV data.', 'error');
        }
    }

    showMessage(message, type = 'info', elementId = null) {
        const messageElement = elementId ? document.getElementById(elementId) : null;
        
        if (messageElement) {
            messageElement.textContent = message;
            messageElement.className = `text-sm ${type === 'error' ? 'text-red-600' : type === 'success' ? 'text-green-600' : 'text-blue-600'}`;
        } else {
            // Create a temporary notification
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-xl shadow-lg transition-all duration-300 ${
                type === 'error' ? 'bg-red-500 text-white' : 
                type === 'success' ? 'bg-green-500 text-white' : 
                'bg-blue-500 text-white'
            }`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            // Remove notification after 3 seconds
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
    }

    // Opportunity Management Methods
    showAddOpportunityModal() {
        this.currentOpportunityId = null;
        document.getElementById('modalTitle').textContent = 'Add Opportunity';
        document.getElementById('modalSubtitle').textContent = 'Enter opportunity details below';
        document.getElementById('submitBtnText').textContent = 'Add Opportunity';
        document.getElementById('opportunityForm').reset();
        document.getElementById('opportunityModal').classList.remove('hidden');
    }

    showEditOpportunityModal(opportunity) {
        this.currentOpportunityId = opportunity.id;
        document.getElementById('modalTitle').textContent = 'Edit Opportunity';
        document.getElementById('modalSubtitle').textContent = 'Update opportunity details below';
        document.getElementById('submitBtnText').textContent = 'Update Opportunity';
        
        // Fill form with opportunity data
        document.getElementById('opportunityId').value = opportunity.id;
        document.getElementById('opportunityTitle').value = opportunity.title;
        document.getElementById('opportunityCompany').value = opportunity.company;
        document.getElementById('opportunityType').value = opportunity.type;
        document.getElementById('opportunityCategory').value = opportunity.category;
        document.getElementById('opportunityLocation').value = opportunity.location;
        document.getElementById('opportunityDeadline').value = opportunity.deadline;
        document.getElementById('opportunityDescription').value = opportunity.description;
        document.getElementById('opportunityRequirements').value = opportunity.requirements || '';
        document.getElementById('opportunityLink').value = opportunity.application_url || '';
        
        document.getElementById('opportunityModal').classList.remove('hidden');
    }

    hideOpportunityModal() {
        document.getElementById('opportunityModal').classList.add('hidden');
        document.getElementById('opportunityForm').reset();
        document.getElementById('opportunityMessage').textContent = '';
    }

    async handleOpportunitySubmit() {
        const formData = {
            title: document.getElementById('opportunityTitle').value,
            company: document.getElementById('opportunityCompany').value,
            type: document.getElementById('opportunityType').value,
            category: document.getElementById('opportunityCategory').value,
            location: document.getElementById('opportunityLocation').value,
            deadline: document.getElementById('opportunityDeadline').value,
            description: document.getElementById('opportunityDescription').value,
            requirements: document.getElementById('opportunityRequirements').value,
            application_link: document.getElementById('opportunityLink').value
        };

        try {
            const url = this.currentOpportunityId 
                ? `${this.apiBaseUrl}/admin/opportunities/${this.currentOpportunityId}`
                : `${this.apiBaseUrl}/admin/opportunities`;
            
            const method = this.currentOpportunityId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                this.hideOpportunityModal();
                this.showMessage(data.message, 'success');
                this.loadOpportunities();
                this.loadDashboardData();
            } else {
                this.showMessage(data.error || 'Failed to save opportunity.', 'error', 'opportunityMessage');
            }
        } catch (error) {
            console.error('Error saving opportunity:', error);
            this.showMessage('Failed to save opportunity.', 'error', 'opportunityMessage');
        }
    }

    showDeleteConfirmation(opportunity) {
        this.opportunityToDelete = opportunity;
        document.getElementById('deleteOpportunityTitle').textContent = opportunity.title;
        document.getElementById('deleteModal').classList.remove('hidden');
    }

    hideDeleteModal() {
        document.getElementById('deleteModal').classList.add('hidden');
        this.opportunityToDelete = null;
    }

    async confirmDeleteOpportunity() {
        if (!this.opportunityToDelete) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/opportunities/${this.opportunityToDelete.id}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (response.ok) {
                this.hideDeleteModal();
                this.showMessage(data.message, 'success');
                this.loadOpportunities();
                this.loadDashboardData();
            } else {
                this.showMessage(data.error || 'Failed to delete opportunity.', 'error');
            }
        } catch (error) {
            console.error('Error deleting opportunity:', error);
            this.showMessage('Failed to delete opportunity.', 'error');
        }
    }

    createOpportunityRow(opportunity) {
        const row = document.createElement('tr');
        row.className = 'table-row border-b border-gray-100 hover:bg-gray-50 transition-colors duration-200';
        
        row.innerHTML = `
            <td class="py-4 px-4">
                <div>
                    <div class="font-semibold text-gray-900">${opportunity.title}</div>
                    <div class="text-sm text-gray-500">${opportunity.location}</div>
                </div>
            </td>
            <td class="py-4 px-4 text-gray-700">${opportunity.company}</td>
            <td class="py-4 px-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    ${opportunity.type}
                </span>
            </td>
            <td class="py-4 px-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    ${opportunity.category}
                </span>
            </td>
            <td class="py-4 px-4">
                <div class="flex space-x-2">
                    <button onclick="window.adminPanel.showEditOpportunityModal(${JSON.stringify(opportunity).replace(/"/g, '&quot;')})" 
                            class="text-blue-600 hover:text-blue-800 font-medium text-sm transition-colors duration-200">
                        ✏️ Edit
                    </button>
                    <button onclick="window.adminPanel.showDeleteConfirmation(${JSON.stringify(opportunity).replace(/"/g, '&quot;')})" 
                            class="text-red-600 hover:text-red-800 font-medium text-sm transition-colors duration-200">
                        🗑️ Delete
                    </button>
                </div>
            </td>
        `;
        
        return row;
    }
}

// Initialize admin panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});
