// Campus Climb Frontend JavaScript
class CampusClimbApp {
    constructor() {
        this.apiBaseUrl = window.APP_CONFIG ? window.APP_CONFIG.apiBaseUrl : 'http://localhost:8000/api';
        this.currentUser = null;
        this.opportunities = [];
        this.initialized = false;
        this.init();
    }

    init() {
        if (this.initialized) return;
        
        this.setupEventListeners();
        this.loadOpportunities();
        this.loadFilters();
        this.checkAuthStatus();
        
        // Ensure only one section is visible initially
        this.ensureSingleSectionVisible();
        
        this.initialized = true;
    }

    setupEventListeners() {
        // Navigation buttons
        document.getElementById('loginBtn').addEventListener('click', () => this.showLoginModal());
        document.getElementById('registerBtn').addEventListener('click', () => this.showRegisterModal());
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
        document.getElementById('loginWelcomeBtn').addEventListener('click', () => this.showLoginModal());

        // Modal controls
        document.getElementById('closeLoginModal').addEventListener('click', () => this.hideLoginModal());
        document.getElementById('closeRegisterModal').addEventListener('click', () => this.hideRegisterModal());

        // Forms
        document.getElementById('loginForm').addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('registerForm').addEventListener('submit', (e) => this.handleRegister(e));

        // Dashboard buttons - only available after login
        document.getElementById('viewAllBtn').addEventListener('click', () => this.showOpportunitiesSection());

        // Filter controls
        document.getElementById('applyFilters').addEventListener('click', () => this.applyFilters());
        
        // Quick action buttons
        this.setupQuickActionButtons();
    }

    setupQuickActionButtons() {
        // Add event listeners for quick action buttons
        const quickActions = document.querySelectorAll('#dashboardSection .grid button');
        quickActions.forEach((button, index) => {
            button.addEventListener('click', () => {
                const actions = ['searchJobs', 'internships', 'workshops', 'competitions'];
                this.handleQuickAction(actions[index]);
            });
        });
    }

    handleQuickAction(action) {
        // Handle quick action button clicks
        switch(action) {
            case 'searchJobs':
                this.showOpportunitiesSection();
                this.filterByType('job');
                break;
            case 'internships':
                this.showOpportunitiesSection();
                this.filterByType('internship');
                break;
            case 'workshops':
                this.showOpportunitiesSection();
                this.filterByType('workshop');
                break;
            case 'competitions':
                this.showOpportunitiesSection();
                this.filterByType('competition');
                break;
        }
    }

    filterByType(type) {
        // Set the type filter and apply it
        const typeFilter = document.getElementById('typeFilter');
        if (typeFilter) {
            typeFilter.value = type;
            this.applyFilters();
        }
    }

    async checkAuthStatus() {
        const userEmail = localStorage.getItem('userEmail');
        if (userEmail) {
            try {
                const response = await fetch(`${this.apiBaseUrl}/auth/profile?email=${userEmail}`);
                if (response.ok) {
                    this.currentUser = await response.json();
                    this.showDashboard();
                } else {
                    localStorage.removeItem('userEmail');
                    this.showWelcomeSection();
                }
            } catch (error) {
                console.error('Error checking auth status:', error);
                localStorage.removeItem('userEmail');
                this.showWelcomeSection();
            }
        } else {
            this.showWelcomeSection();
        }
    }

    async loadOpportunities() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/opportunities`);
            if (response.ok) {
                this.opportunities = await response.json();
                this.updateDashboardStats();
                this.renderOpportunitiesGrid();
            } else {
                console.error('Failed to load opportunities');
            }
        } catch (error) {
            console.error('Error loading opportunities:', error);
            this.showMessage('Failed to load opportunities. Please try again later.', 'error');
        }
    }

    async loadFilters() {
        try {
            const [typesResponse, categoriesResponse] = await Promise.all([
                fetch(`${this.apiBaseUrl}/opportunities/types`),
                fetch(`${this.apiBaseUrl}/opportunities/categories`)
            ]);

            if (typesResponse.ok && categoriesResponse.ok) {
                const types = await typesResponse.json();
                const categories = await categoriesResponse.json();

                this.populateFilterOptions('typeFilter', types);
                this.populateFilterOptions('categoryFilter', categories);
            }
        } catch (error) {
            console.error('Error loading filters:', error);
        }
    }

    populateFilterOptions(selectId, options) {
        const select = document.getElementById(selectId);
        if (!select) return;

        // Clear existing options except the first one
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }

        // Add new options
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option.charAt(0).toUpperCase() + option.slice(1);
            select.appendChild(optionElement);
        });
    }

    updateDashboardStats() {
        if (!this.opportunities) return;

        const totalOpportunities = this.opportunities.length;
        const recentOpportunities = this.opportunities.filter(opp => {
            const oppDate = new Date(opp.date_posted);
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            return oppDate >= weekAgo;
        }).length;

        const categories = [...new Set(this.opportunities.map(opp => opp.category))];
        const activeCategories = categories.length;

        // Update stats
        const totalElement = document.getElementById('totalOpportunities');
        const recentElement = document.getElementById('recentOpportunities');
        const categoriesElement = document.getElementById('activeCategories');

        if (totalElement) totalElement.textContent = totalOpportunities;
        if (recentElement) recentElement.textContent = recentOpportunities;
        if (categoriesElement) categoriesElement.textContent = activeCategories;
    }

    renderOpportunitiesGrid() {
        const grid = document.getElementById('opportunitiesGrid');
        if (!grid) return;

        grid.innerHTML = '';

        if (!this.opportunities || this.opportunities.length === 0) {
            grid.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">No opportunities found</h3>
                    <p class="text-gray-600">Try adjusting your filters or check back later for new opportunities.</p>
                </div>
            `;
            return;
        }

        this.opportunities.forEach(opportunity => {
            const card = this.createOpportunityCard(opportunity);
            grid.appendChild(card);
        });
    }

    createOpportunityCard(opportunity) {
        const card = document.createElement('div');
        card.className = 'card p-6 hover:shadow-lg transition-all duration-300';
        card.dataset.opportunityId = opportunity.id;
        
        const typeColors = {
            'internship': 'bg-blue-100 text-blue-800',
            'job': 'bg-green-100 text-green-800',
            'workshop': 'bg-purple-100 text-purple-800',
            'conference': 'bg-orange-100 text-orange-800',
            'competition': 'bg-red-100 text-red-800'
        };

        const typeColor = typeColors[opportunity.type] || 'bg-gray-100 text-gray-800';
        const formattedDate = new Date(opportunity.date_posted).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });

        // Truncate description for initial view
        const shortDescription = opportunity.description.length > 150 
            ? opportunity.description.substring(0, 150) + '...' 
            : opportunity.description;

        card.innerHTML = `
            <div class="flex justify-between items-start mb-4">
                <span class="px-3 py-1 rounded-full text-xs font-semibold ${typeColor}">
                    ${opportunity.type.charAt(0).toUpperCase() + opportunity.type.slice(1)}
                </span>
                <span class="text-sm text-gray-500">${formattedDate}</span>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">${opportunity.title}</h3>
            <div class="text-lg font-bold text-university-blue mb-3">${opportunity.company}</div>
            <p class="text-gray-600 mb-4 opportunity-description" data-full-description="${opportunity.description}">${shortDescription}</p>
            
            <!-- Expanded content (hidden by default) -->
            <div class="expanded-content hidden">
                <div class="border-t border-gray-200 pt-4 mb-4">
                    <h4 class="text-lg font-semibold text-gray-900 mb-3">Full Description</h4>
                    <p class="text-gray-700 leading-relaxed mb-6">${opportunity.description}</p>
                    
                    ${opportunity.requirements ? `
                        <div class="mb-6">
                            <h4 class="text-lg font-semibold text-gray-900 mb-3">Requirements</h4>
                            <p class="text-gray-700 leading-relaxed">${opportunity.requirements}</p>
                        </div>
                    ` : ''}
                    
                    <div class="flex items-center justify-between">
                        <div class="text-sm text-gray-600">
                            <span class="font-medium">Location:</span> ${opportunity.location}
                        </div>
                        <div class="text-sm text-gray-600">
                            <span class="font-medium">Company:</span> ${opportunity.company}
                        </div>
                    </div>
                </div>
                
                ${opportunity.application_url ? `
                    <div class="text-center">
                        <a href="${opportunity.application_url}" target="_blank" rel="noopener noreferrer" 
                           class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                            🚀 Apply Now
                        </a>
                    </div>
                ` : `
                    <div class="text-center">
                        <p class="text-gray-500 text-sm">Application link not available</p>
                    </div>
                `}
            </div>
            
            <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-700">${opportunity.category}</span>
                <button class="learn-more-btn text-blue-600 hover:text-blue-700 font-semibold text-sm transition-colors">
                    Learn More →
                </button>
            </div>
        `;

        // Add event listener for Learn More button
        const learnMoreBtn = card.querySelector('.learn-more-btn');
        learnMoreBtn.addEventListener('click', () => this.toggleOpportunityExpansion(card));

        return card;
    }

    applyFilters() {
        const typeFilter = document.getElementById('typeFilter').value;
        const categoryFilter = document.getElementById('categoryFilter').value;

        let filteredOpportunities = this.opportunities;

        if (typeFilter) {
            filteredOpportunities = filteredOpportunities.filter(opp => opp.type === typeFilter);
        }

        if (categoryFilter) {
            filteredOpportunities = filteredOpportunities.filter(opp => opp.category === categoryFilter);
        }

        this.renderFilteredOpportunities(filteredOpportunities);
    }

    renderFilteredOpportunities(filteredOpportunities) {
        const grid = document.getElementById('opportunitiesGrid');
        if (!grid) return;

        grid.innerHTML = '';

        if (filteredOpportunities.length === 0) {
            grid.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">No matching opportunities</h3>
                    <p class="text-gray-600">Try adjusting your filters to see more results.</p>
                </div>
            `;
            return;
        }

        filteredOpportunities.forEach(opportunity => {
            const card = this.createOpportunityCard(opportunity);
            grid.appendChild(card);
        });
    }

    showLoginModal() {
        document.getElementById('loginModal').classList.remove('hidden');
        document.getElementById('loginEmail').focus();
    }

    hideLoginModal() {
        document.getElementById('loginModal').classList.add('hidden');
        document.getElementById('loginForm').reset();
        document.getElementById('loginMessage').textContent = '';
    }

    showRegisterModal() {
        document.getElementById('registerModal').classList.remove('hidden');
        document.getElementById('registerFirstName').focus();
    }

    hideRegisterModal() {
        document.getElementById('registerModal').classList.add('hidden');
        document.getElementById('registerForm').reset();
        document.getElementById('registerMessage').textContent = '';
    }

    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        if (!email.endsWith('@wvstateu.edu')) {
            this.showMessage('Please use your WVSU email address (@wvstateu.edu).', 'error', 'loginMessage');
            return;
        }

        try {
            console.log('Attempting login with:', email);
            const response = await fetch(`${this.apiBaseUrl}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();
            console.log('Login response:', data);

            if (response.ok) {
                console.log('Login successful, showing dashboard...');
                this.currentUser = data.user;
                localStorage.setItem('userEmail', email);
                this.hideLoginModal();
                this.showDashboard();
                this.setupPeriodicRefresh(); // Start periodic refresh
                this.showMessage('Login successful! Welcome back.', 'success');
            } else {
                console.log('Login failed:', data.error);
                this.showMessage(data.error || 'Invalid email or password.', 'error', 'loginMessage');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showMessage('Login failed. Please check your connection and try again.', 'error', 'loginMessage');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const firstName = document.getElementById('registerFirstName').value;
        const lastName = document.getElementById('registerLastName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;

        if (!email.endsWith('@wvstateu.edu')) {
            this.showMessage('Please use your WVSU email address (@wvstateu.edu).', 'error', 'registerMessage');
            return;
        }

        if (password.length < 6) {
            this.showMessage('Password must be at least 6 characters long.', 'error', 'registerMessage');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ first_name: firstName, last_name: lastName, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.hideRegisterModal();
                this.showMessage('Registration successful! Please login to continue.', 'success');
            } else {
                this.showMessage(data.error || 'Registration failed. Please try again.', 'error', 'registerMessage');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showMessage('Registration failed. Please check your connection and try again.', 'error', 'registerMessage');
        }
    }

    logout() {
        this.currentUser = null;
        localStorage.removeItem('userEmail');
        this.showWelcomeSection();
        this.showMessage('Logged out successfully!', 'success');
    }

    showDashboard() {
        console.log('showDashboard called');
        console.log('Current user:', this.currentUser);
        
        // Hide all sections
        const welcomeSection = document.getElementById('welcomeSection');
        const opportunitiesSection = document.getElementById('opportunitiesSection');
        const dashboardSection = document.getElementById('dashboardSection');
        
        if (welcomeSection) welcomeSection.classList.add('hidden');
        if (opportunitiesSection) opportunitiesSection.classList.add('hidden');
        if (dashboardSection) dashboardSection.classList.remove('hidden');
        
        // Setup periodic refresh for logged-in users
        if (this.currentUser) {
            this.setupPeriodicRefresh();
        }
        
        console.log('Sections updated');
        
        // Update navigation
        const loginBtn = document.getElementById('loginBtn');
        const registerBtn = document.getElementById('registerBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        
        if (loginBtn) loginBtn.classList.add('hidden');
        if (registerBtn) registerBtn.classList.add('hidden');
        if (logoutBtn) logoutBtn.classList.remove('hidden');
        
        console.log('Navigation updated');
        
        // Update user name
        if (this.currentUser) {
            const userNameElement = document.getElementById('userName');
            if (userNameElement) {
                userNameElement.textContent = this.currentUser.first_name;
                console.log('User name updated:', this.currentUser.first_name);
            }
        }
        
        // Refresh data and update stats
        this.loadOpportunities();
        this.updateDashboardStats();
        console.log('Dashboard shown successfully');
    }

    showWelcomeSection() {
        // Hide all sections
        document.getElementById('dashboardSection').classList.add('hidden');
        document.getElementById('opportunitiesSection').classList.add('hidden');
        document.getElementById('welcomeSection').classList.remove('hidden');
        
        // Update navigation
        document.getElementById('logoutBtn').classList.add('hidden');
        document.getElementById('loginBtn').classList.remove('hidden');
        document.getElementById('registerBtn').classList.remove('hidden');
    }

    showOpportunitiesSection() {
        // Only show opportunities if user is logged in
        if (!this.currentUser) {
            this.showMessage('Please login to browse opportunities.', 'error');
            this.showLoginModal();
            return;
        }

        // Hide all sections
        document.getElementById('welcomeSection').classList.add('hidden');
        document.getElementById('dashboardSection').classList.add('hidden');
        document.getElementById('opportunitiesSection').classList.remove('hidden');
        
        // Refresh and render opportunities
        this.loadOpportunities();
        this.loadFilters();
    }

    ensureSingleSectionVisible() {
        // Hide all sections first
        const sections = ['welcomeSection', 'dashboardSection', 'opportunitiesSection'];
        sections.forEach(sectionId => {
            const element = document.getElementById(sectionId);
            if (element) {
                element.classList.add('hidden');
            }
        });
        
        // Show welcome section by default
        const welcome = document.getElementById('welcomeSection');
        if (welcome) {
            welcome.classList.remove('hidden');
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
            
            // Remove after 3 seconds
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, 3000);
        }
    }

    setupPeriodicRefresh() {
        // Refresh data every 30 seconds for logged-in users
        setInterval(() => {
            if (this.currentUser) {
                this.loadOpportunities();
            }
        }, 30000); // 30 seconds
    }

    toggleOpportunityExpansion(card) {
        const expandedContent = card.querySelector('.expanded-content');
        const learnMoreBtn = card.querySelector('.learn-more-btn');
        const isExpanded = !expandedContent.classList.contains('hidden');
        
        if (isExpanded) {
            // Collapse
            expandedContent.classList.add('hidden');
            learnMoreBtn.textContent = 'Learn More →';
            card.classList.remove('expanded');
        } else {
            // Expand
            expandedContent.classList.remove('hidden');
            learnMoreBtn.textContent = 'Show Less ←';
            card.classList.add('expanded');
            
            // Smooth scroll to show the expanded content
            setTimeout(() => {
                card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (!window.appInstance) {
        window.appInstance = new CampusClimbApp();
    }
});
