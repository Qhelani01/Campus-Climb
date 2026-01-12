// Campus Climb Frontend JavaScript
class CampusClimbApp {
    constructor() {
        this.apiBaseUrl = window.APP_CONFIG ? window.APP_CONFIG.apiBaseUrl : 'http://localhost:8000/api';
        this.currentUser = null;
        this.opportunities = [];
        this.filteredOpportunities = [];
        this.searchQuery = '';
        this.initialized = false;
        this.currentRoute = null;
        this.isNavigating = false; // Flag to prevent recursive navigation
        this.init();
    }

    init() {
        if (this.initialized) return;
        
        this.setupEventListeners();
        this.setupRouting();
        this.loadOpportunities();
        this.loadFilters();
        
        // Check auth status first, then handle routing
        this.checkAuthStatus().then(() => {
            // Handle initial route after auth check completes
            this.handleRouteChange();
        });
        
        // Ensure only one section is visible initially
        this.ensureSingleSectionVisible();
        
        this.initialized = true;
    }

    setupRouting() {
        // Listen for browser back/forward button
        window.addEventListener('popstate', (e) => {
            this.handleRouteChange();
        });
    }

    handleRouteChange() {
        const hash = window.location.hash.slice(1) || 'welcome';
        this.navigateToRoute(hash, false); // false = don't push to history (already in history)
    }

    navigateToRoute(route, pushState = true) {
        if (pushState && this.currentRoute !== route) {
            window.history.pushState({ route }, '', `#${route}`);
        }
        this.currentRoute = route;
        this.isNavigating = true;

        switch(route) {
            case 'dashboard':
                if (this.currentUser) {
                    this.showDashboardInternal();
                } else {
                    this.showWelcomeSectionInternal();
                    this.currentRoute = 'welcome';
                    if (pushState) {
                        window.history.replaceState({ route: 'welcome' }, '', '#welcome');
                    }
                }
                break;
            case 'opportunities':
                if (this.currentUser) {
                    this.showOpportunitiesSectionInternal();
                } else {
                    this.showWelcomeSectionInternal();
                    this.currentRoute = 'welcome';
                    if (pushState) {
                        window.history.replaceState({ route: 'welcome' }, '', '#welcome');
                    }
                }
                break;
            case 'welcome':
            default:
                this.showWelcomeSectionInternal();
                break;
        }
        
        this.isNavigating = false;
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
        document.getElementById('closeLoginModalBtn').addEventListener('click', () => this.hideLoginModal());
        document.getElementById('closeRegisterModalBtn').addEventListener('click', () => this.hideRegisterModal());

        // Close modals on backdrop click
        document.getElementById('loginModal').addEventListener('click', (e) => {
            if (e.target.id === 'loginModal') this.hideLoginModal();
        });
        document.getElementById('registerModal').addEventListener('click', (e) => {
            if (e.target.id === 'registerModal') this.hideRegisterModal();
        });
        document.getElementById('aiAssistantModal').addEventListener('click', (e) => {
            if (e.target.id === 'aiAssistantModal') this.hideAIAssistant();
        });
        
        // AI Assistant tab switching
        document.querySelectorAll('.ai-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const type = tab.dataset.type;
                this.switchAITab(type);
            });
        });
        
        // AI Assistant buttons
        document.getElementById('generateAdviceBtn').addEventListener('click', () => this.generateAIAdvice());
        document.getElementById('saveProfileBtn').addEventListener('click', () => this.saveUserProfile());

        // Forms
        document.getElementById('loginForm').addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('registerForm').addEventListener('submit', (e) => this.handleRegister(e));

        // Dashboard buttons
        document.getElementById('viewAllBtn').addEventListener('click', () => this.showOpportunitiesSection());
        
        // Admin panel event listeners
        const fetchOpportunitiesBtn = document.getElementById('fetchOpportunitiesBtn');
        if (fetchOpportunitiesBtn) {
            fetchOpportunitiesBtn.addEventListener('click', () => this.fetchOpportunities());
        }
        
        const viewFetchStatusBtn = document.getElementById('viewFetchStatusBtn');
        if (viewFetchStatusBtn) {
            viewFetchStatusBtn.addEventListener('click', () => {
                const fetchStatus = document.getElementById('fetchStatus');
                if (fetchStatus) {
                    fetchStatus.classList.toggle('hidden');
                }
            });
        }

        // Filter controls
        document.getElementById('applyFilters').addEventListener('click', () => this.applyFilters());
        
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.applyFilters();
                }
            });
        }
        
        const clearSearch = document.getElementById('clearSearch');
        if (clearSearch) {
            clearSearch.addEventListener('click', () => this.clearSearch());
        }
        
        // Quick action buttons
        this.setupQuickActionButtons();
    }

    setupQuickActionButtons() {
        const quickActions = document.querySelectorAll('#dashboardSection .quick-action');
        quickActions.forEach((button, index) => {
            button.addEventListener('click', () => {
                const actions = ['searchJobs', 'internships', 'workshops', 'competitions'];
                this.handleQuickAction(actions[index]);
            });
        });
    }

    handleQuickAction(action) {
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
        const typeFilter = document.getElementById('typeFilter');
        if (typeFilter) {
            typeFilter.value = type;
            this.applyFilters();
        }
    }

    handleSearch(query) {
        this.searchQuery = query.toLowerCase().trim();
        const clearBtn = document.getElementById('clearSearch');
        if (clearBtn) {
            if (this.searchQuery) {
                clearBtn.classList.add('visible');
            } else {
                clearBtn.classList.remove('visible');
            }
        }
        this.applyFilters();
    }

    clearSearch() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
            this.handleSearch('');
        }
    }

    async checkAuthStatus() {
        const userEmail = localStorage.getItem('userEmail');
        if (userEmail) {
            try {
                let response = await fetch(`${this.apiBaseUrl}/auth/me`, {
                    method: 'GET',
                    credentials: 'include'
                });
                
                if (!response.ok) {
                    response = await fetch(`${this.apiBaseUrl}/auth/me?email=${encodeURIComponent(userEmail)}`, {
                        method: 'GET',
                        credentials: 'include'
                    });
                }
                
                if (response.ok) {
                    const data = await response.json();
                    this.currentUser = data.user;
                    localStorage.setItem('userData', JSON.stringify(data.user));
                } else {
                    const userData = localStorage.getItem('userData');
                    if (userData) {
                        try {
                            this.currentUser = JSON.parse(userData);
                            return;
                        } catch (e) {}
                    }
                    localStorage.removeItem('userEmail');
                    localStorage.removeItem('userData');
                    this.currentUser = null;
                }
            } catch (error) {
                console.error('Error checking auth status:', error);
                const userData = localStorage.getItem('userData');
                if (userData) {
                    try {
                        this.currentUser = JSON.parse(userData);
                        return;
                    } catch (e) {}
                }
                localStorage.removeItem('userEmail');
                localStorage.removeItem('userData');
                this.currentUser = null;
            }
        } else {
            this.currentUser = null;
        }
    }

    async loadOpportunities() {
        this.showLoadingSkeleton();
        try {
            const response = await fetch(`${this.apiBaseUrl}/opportunities`);
            if (response.ok) {
                this.opportunities = await response.json();
                this.filteredOpportunities = [...this.opportunities];
                this.updateDashboardStats();
                this.renderOpportunitiesGrid();
            } else {
                console.error('Failed to load opportunities');
                this.showEmptyState('Failed to load opportunities. Please try again later.');
            }
        } catch (error) {
            console.error('Error loading opportunities:', error);
            this.showEmptyState('Failed to load opportunities. Please check your connection and try again.');
        }
    }

    showLoadingSkeleton() {
        const grid = document.getElementById('opportunitiesGrid');
        if (!grid) return;
        
        grid.innerHTML = '';
        for (let i = 0; i < 6; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'card p-6';
            skeleton.innerHTML = `
                <div class="skeleton h-6 w-24 mb-4"></div>
                <div class="skeleton h-8 w-full mb-3"></div>
                <div class="skeleton h-6 w-3/4 mb-4"></div>
                <div class="skeleton h-20 w-full mb-4"></div>
                <div class="skeleton h-4 w-1/2"></div>
            `;
            grid.appendChild(skeleton);
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

        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }

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
            const oppDate = opp.created_at ? new Date(opp.created_at) : null;
            if (!oppDate) return false;
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            return oppDate >= weekAgo;
        }).length;

        const categories = [...new Set(this.opportunities.map(opp => opp.category))];
        const activeCategories = categories.length;

        // Animate numbers
        this.animateNumber('totalOpportunities', totalOpportunities);
        this.animateNumber('recentOpportunities', recentOpportunities);
        this.animateNumber('activeCategories', activeCategories);
    }

    animateNumber(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = parseInt(element.textContent) || 0;
        const duration = 600;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            
            element.textContent = currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.textContent = targetValue;
            }
        };
        
        requestAnimationFrame(animate);
    }

    renderOpportunitiesGrid() {
        const grid = document.getElementById('opportunitiesGrid');
        if (!grid) return;

        grid.innerHTML = '';

        if (!this.filteredOpportunities || this.filteredOpportunities.length === 0) {
            this.showEmptyState();
            return;
        }

        this.filteredOpportunities.forEach(opportunity => {
            const card = this.createOpportunityCard(opportunity);
            grid.appendChild(card);
        });
    }

    createOpportunityCard(opportunity) {
        const card = document.createElement('div');
        card.className = 'card opportunity-card p-6';
        card.dataset.opportunityId = opportunity.id;
        
        const typeConfig = {
            'internship': { 
                color: 'bg-blue-100 text-blue-800 border-blue-200',
                icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>'
            },
            'job': { 
                color: 'bg-green-100 text-green-800 border-green-200',
                icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2h8z"></path>'
            },
            'workshop': { 
                color: 'bg-purple-100 text-purple-800 border-purple-200',
                icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>'
            },
            'conference': { 
                color: 'bg-orange-100 text-orange-800 border-orange-200',
                icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>'
            },
            'competition': { 
                color: 'bg-red-100 text-red-800 border-red-200',
                icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>'
            }
        };

        const config = typeConfig[opportunity.type] || { 
            color: 'bg-gray-100 text-gray-800 border-gray-200',
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>'
        };

        const dateField = opportunity.created_at || opportunity.date_posted;
        const formattedDate = dateField ? new Date(dateField).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }) : 'Date not available';

        // Deadline handling
        let deadlineBadge = '';
        if (opportunity.deadline) {
            const deadline = new Date(opportunity.deadline);
            const today = new Date();
            const daysUntilDeadline = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24));
            
            if (daysUntilDeadline < 0) {
                deadlineBadge = '<span class="deadline-badge">Expired</span>';
            } else if (daysUntilDeadline <= 7) {
                deadlineBadge = `<span class="deadline-badge urgent">${daysUntilDeadline} days left</span>`;
            } else if (daysUntilDeadline <= 30) {
                deadlineBadge = `<span class="deadline-badge">${daysUntilDeadline} days left</span>`;
            } else {
                deadlineBadge = `<span class="deadline-badge" style="background: #f0fdf4; color: #166534;">Due ${deadline.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>`;
            }
        }

        const shortDescription = opportunity.description.length > 120 
            ? opportunity.description.substring(0, 120) + '...' 
            : opportunity.description;

        // Highlight search terms in description
        const highlightedDescription = this.searchQuery 
            ? this.highlightText(shortDescription, this.searchQuery)
            : shortDescription;

        card.innerHTML = `
            <div class="flex justify-between items-start mb-4">
                <span class="opportunity-badge ${config.color} border">
                    <svg class="opportunity-type-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        ${config.icon}
                    </svg>
                    ${opportunity.type.charAt(0).toUpperCase() + opportunity.type.slice(1)}
                </span>
                <div class="flex flex-col items-end gap-1">
                    ${deadlineBadge}
                    <span class="text-xs text-gray-500">${formattedDate}</span>
                </div>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-2">${this.highlightText(opportunity.title, this.searchQuery)}</h3>
            <div class="text-lg font-bold text-university-blue mb-3">${this.highlightText(opportunity.company, this.searchQuery)}</div>
            <p class="text-gray-600 mb-4 leading-relaxed opportunity-description">${highlightedDescription}</p>
            
            <div class="expanded-content hidden">
                <div class="border-t border-gray-200 pt-4 mb-4">
                    <h4 class="text-lg font-bold text-gray-900 mb-3">Full Description</h4>
                    <p class="text-gray-700 leading-relaxed mb-6">${this.highlightText(opportunity.description, this.searchQuery)}</p>
                    
                    ${opportunity.requirements ? `
                        <div class="mb-6">
                            <h4 class="text-lg font-bold text-gray-900 mb-3">Requirements</h4>
                            <p class="text-gray-700 leading-relaxed">${opportunity.requirements}</p>
                        </div>
                    ` : ''}
                    
                    <div class="flex flex-wrap items-center gap-4 mb-4">
                        <div class="flex items-center gap-2 text-sm text-gray-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                            <span class="font-medium">${opportunity.location}</span>
                        </div>
                        <div class="flex items-center gap-2 text-sm text-gray-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                            </svg>
                            <span class="font-medium">${opportunity.company}</span>
                        </div>
                        ${opportunity.salary ? `
                            <div class="flex items-center gap-2 text-sm text-gray-600">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <span class="font-medium">${opportunity.salary}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                ${opportunity.application_url ? `
                    <div class="text-center">
                        <a href="${opportunity.application_url}" target="_blank" rel="noopener noreferrer" 
                           class="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
                            </svg>
                            Apply Now
                        </a>
                    </div>
                ` : `
                    <div class="text-center">
                        <p class="text-gray-500 text-sm">Application link not available</p>
                    </div>
                `}
            </div>
            
            <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                <span class="text-sm font-semibold text-gray-600 px-3 py-1 bg-gray-100 rounded-full">${opportunity.category}</span>
                <div class="flex items-center gap-3">
                    <button class="ai-assistance-btn text-purple-600 hover:text-purple-700 font-semibold text-sm transition-colors flex items-center gap-1" data-opportunity-id="${opportunity.id}">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                        </svg>
                        AI Help
                    </button>
                    <button class="learn-more-btn text-blue-600 hover:text-blue-700 font-semibold text-sm transition-colors flex items-center gap-1">
                        Learn More
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        const learnMoreBtn = card.querySelector('.learn-more-btn');
        learnMoreBtn.addEventListener('click', () => this.toggleOpportunityExpansion(card));
        
        const aiAssistanceBtn = card.querySelector('.ai-assistance-btn');
        aiAssistanceBtn.addEventListener('click', () => this.showAIAssistant(opportunity.id));

        return card;
    }

    highlightText(text, query) {
        if (!query || !text) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark class="bg-yellow-200 px-1 rounded">$1</mark>');
    }

    applyFilters() {
        const typeFilter = document.getElementById('typeFilter')?.value || '';
        const categoryFilter = document.getElementById('categoryFilter')?.value || '';

        let filtered = [...this.opportunities];

        // Apply search
        if (this.searchQuery) {
            filtered = filtered.filter(opp => 
                opp.title.toLowerCase().includes(this.searchQuery) ||
                opp.company.toLowerCase().includes(this.searchQuery) ||
                opp.description.toLowerCase().includes(this.searchQuery)
            );
        }

        // Apply type filter
        if (typeFilter) {
            filtered = filtered.filter(opp => opp.type === typeFilter);
        }

        // Apply category filter
        if (categoryFilter) {
            filtered = filtered.filter(opp => opp.category === categoryFilter);
        }

        this.filteredOpportunities = filtered;
        this.renderOpportunitiesGrid();
    }

    showEmptyState(message = null) {
        const grid = document.getElementById('opportunitiesGrid');
        if (!grid) return;

        const defaultMessage = message || (this.searchQuery || document.getElementById('typeFilter')?.value || document.getElementById('categoryFilter')?.value
            ? 'No matching opportunities found. Try adjusting your filters or search terms.'
            : 'No opportunities available at the moment. Check back later for new opportunities.');

        grid.innerHTML = `
            <div class="col-span-full empty-state">
                <div class="empty-state-icon">
                    <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">No opportunities found</h3>
                <p class="text-gray-600 mb-6 max-w-md mx-auto">${defaultMessage}</p>
                ${this.searchQuery || document.getElementById('typeFilter')?.value || document.getElementById('categoryFilter')?.value ? `
                    <button onclick="window.appInstance.clearSearch(); document.getElementById('typeFilter').value=''; document.getElementById('categoryFilter').value=''; window.appInstance.applyFilters();" 
                            class="btn-primary text-white px-6 py-3 rounded-xl font-semibold">
                        Clear Filters
                    </button>
                ` : ''}
            </div>
        `;
    }

    showLoginModal() {
        document.getElementById('loginModal').classList.remove('hidden');
        document.getElementById('loginEmail').focus();
    }

    hideLoginModal() {
        document.getElementById('loginModal').classList.add('hidden');
        document.getElementById('loginForm').reset();
        document.getElementById('loginMessage').textContent = '';
        const submitBtn = document.getElementById('loginSubmitBtn');
        if (submitBtn) {
            submitBtn.classList.remove('btn-loading');
            submitBtn.disabled = false;
        }
    }

    showRegisterModal() {
        document.getElementById('registerModal').classList.remove('hidden');
        document.getElementById('registerFirstName').focus();
    }

    hideRegisterModal() {
        document.getElementById('registerModal').classList.add('hidden');
        document.getElementById('registerForm').reset();
        document.getElementById('registerMessage').textContent = '';
        const submitBtn = document.getElementById('registerSubmitBtn');
        if (submitBtn) {
            submitBtn.classList.remove('btn-loading');
            submitBtn.disabled = false;
        }
    }

    setButtonLoading(buttonId, loading) {
        const button = document.getElementById(buttonId);
        if (!button) return;
        
        if (loading) {
            button.classList.add('btn-loading');
            button.disabled = true;
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        // Email validation removed - backend handles it (allows admin users with any email)
        // Non-admin users still require @wvstateu.edu email (enforced by backend)

        // #region agent log
        fetch('http://127.0.0.1:7243/ingest/5554355a-10a5-4c58-b753-9612d8cd5684',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:690',message:'FRONTEND_LOGIN_START',data:{email:email,password_length:password.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
        // #endregion

        this.setButtonLoading('loginSubmitBtn', true);

        // #region agent log
        console.log('DEBUG: About to send login request to:', `${this.apiBaseUrl}/auth/login`);
        fetch('http://127.0.0.1:7243/ingest/5554355a-10a5-4c58-b753-9612d8cd5684',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:703',message:'FRONTEND_LOGIN_REQUEST_START',data:{api_url:`${this.apiBaseUrl}/auth/login`,email:email},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(e=>console.error('Log error:',e));
        // #endregion
        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Include cookies for session
                body: JSON.stringify({ email, password })
            });
            // #region agent log
            console.log('DEBUG: Login response received:', response.status, response.statusText, response.ok);
            fetch('http://127.0.0.1:7243/ingest/5554355a-10a5-4c58-b753-9612d8cd5684',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:712',message:'FRONTEND_LOGIN_RESPONSE',data:{status:response.status,statusText:response.statusText,ok:response.ok,api_url:`${this.apiBaseUrl}/auth/login`},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(e=>console.error('Log error:',e));
            // #endregion

            // Clone response for potential error reading
            const responseClone = response.clone();
            let data;

            try {
                data = await response.json();
                // #region agent log
                console.log('DEBUG: Response data parsed:', data);
                fetch('http://127.0.0.1:7243/ingest/5554355a-10a5-4c58-b753-9612d8cd5684',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:720',message:'FRONTEND_LOGIN_DATA_PARSED',data:{has_user:!!data.user,has_error:!!data.error,error_message:data.error},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(e=>console.error('Log error:',e));
                // #endregion
            } catch (jsonError) {
                console.error('Failed to parse JSON response:', jsonError);
                // #region agent log
                fetch('http://127.0.0.1:7243/ingest/5554355a-10a5-4c58-b753-9612d8cd5684',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:722',message:'FRONTEND_LOGIN_JSON_PARSE_ERROR',data:{error:jsonError.message,status:response.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(e=>console.error('Log error:',e));
                // #endregion
                try {
                    const text = await responseClone.text();
                    console.error('Response text:', text);
                } catch (textError) {
                    console.error('Could not read response text:', textError);
                }
                this.showMessage(`Server error: ${response.status} ${response.statusText}. Please check your connection.`, 'error', 'loginMessage');
                return;
            }

            if (response.ok) {
                // #region agent log
                fetch('http://127.0.0.1:7243/ingest/5554355a-10a5-4c58-b753-9612d8cd5684',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:733',message:'FRONTEND_LOGIN_SUCCESS',data:{user_id:data.user?.id,user_email:data.user?.email,user_is_admin:data.user?.is_admin},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
                // #endregion
                this.currentUser = data.user;
                localStorage.setItem('userEmail', email);
                localStorage.setItem('userData', JSON.stringify(data.user));
                this.hideLoginModal();
                this.showDashboard();
                this.setupPeriodicRefresh();
                this.showMessage('Login successful! Welcome back.', 'success');
            } else {
                // #region agent log
                console.log('DEBUG: Login failed - response.ok is false. Status:', response.status, 'Data:', data);
                fetch('http://127.0.0.1:7243/ingest/5554355a-10a5-4c58-b753-9612d8cd5684',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:748',message:'FRONTEND_LOGIN_ERROR',data:{error:data.error,status:response.status,error_message_shown:data.error||'Login failed',response_ok:response.ok},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(e=>console.error('Log error:',e));
                // #endregion
                const errorMsg = data.error || `Login failed (${response.status}). Please try again.`;
                console.error('Login failed:', response.status, data);
                this.showMessage(errorMsg, 'error', 'loginMessage');
            }
        } catch (error) {
            console.error('Login error:', error);
            // #region agent log
            fetch('http://127.0.0.1:7243/ingest/5554355a-10a5-4c58-b753-9612d8cd5684',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:750',message:'FRONTEND_LOGIN_EXCEPTION',data:{error:error.message,error_type:error.name},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(e=>console.error('Log error:',e));
            // #endregion
            const errorMsg = error.message.includes('Failed to fetch') || error.message.includes('NetworkError')
                ? 'Cannot connect to server. Please make sure the backend is running on port 8000.'
                : `Login failed: ${error.message}. Please check your connection and try again.`;
            this.showMessage(errorMsg, 'error', 'loginMessage');
        } finally {
            this.setButtonLoading('loginSubmitBtn', false);
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

        this.setButtonLoading('registerSubmitBtn', true);

        try {
            const requestData = { first_name: firstName, last_name: lastName, email, password };
            console.log('Attempting registration with:', { ...requestData, password: '***' });
            console.log('API URL:', `${this.apiBaseUrl}/auth/register`);

            const response = await fetch(`${this.apiBaseUrl}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Include cookies for session
                body: JSON.stringify(requestData)
            });

            console.log('Response status:', response.status);
            console.log('Response headers:', Object.fromEntries(response.headers.entries()));

            // Clone response for potential error reading
            const responseClone = response.clone();
            let data;

            try {
                const responseText = await response.text();
                console.log('Response text:', responseText);
                
                if (!responseText) {
                    throw new Error('Empty response from server');
                }
                
                data = JSON.parse(responseText);
            } catch (jsonError) {
                console.error('Failed to parse JSON response:', jsonError);
                try {
                    const text = await responseClone.text();
                    console.error('Response text (from clone):', text);
                    this.showMessage(`Server error: ${response.status} ${response.statusText}. Response: ${text.substring(0, 100)}`, 'error', 'registerMessage');
                } catch (textError) {
                    console.error('Could not read response text:', textError);
                    this.showMessage(`Server error: ${response.status} ${response.statusText}. Please check your connection.`, 'error', 'registerMessage');
                }
                return;
            }

            console.log('Parsed response data:', data);

            if (response.ok) {
                if (data.user) {
                    localStorage.setItem('userEmail', data.user.email);
                    localStorage.setItem('userData', JSON.stringify(data.user));
                }
                this.hideRegisterModal();
                this.showMessage('Registration successful! Please login to continue.', 'success');
            } else {
                const errorMsg = data.error || `Registration failed (${response.status}). Please try again.`;
                console.error('Registration failed:', response.status, data);
                this.showMessage(errorMsg, 'error', 'registerMessage');
            }
        } catch (error) {
            console.error('Registration error:', error);
            console.error('Error stack:', error.stack);
            const errorMsg = error.message.includes('Failed to fetch') || error.message.includes('NetworkError')
                ? 'Cannot connect to server. Please make sure the backend is running on port 8000.'
                : `Registration failed: ${error.message}. Please check your connection and try again.`;
            this.showMessage(errorMsg, 'error', 'registerMessage');
        } finally {
            this.setButtonLoading('registerSubmitBtn', false);
        }
    }

    async logout() {
        try {
            await fetch(`${this.apiBaseUrl}/auth/logout`, {
                method: 'POST',
                credentials: 'include'
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
        this.currentUser = null;
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userData');
        this.showWelcomeSection();
        this.showMessage('Logged out successfully!', 'success');
    }

    showDashboardInternal() {
        const welcomeSection = document.getElementById('welcomeSection');
        const opportunitiesSection = document.getElementById('opportunitiesSection');
        const dashboardSection = document.getElementById('dashboardSection');
        
        if (welcomeSection) welcomeSection.classList.add('hidden');
        if (opportunitiesSection) opportunitiesSection.classList.add('hidden');
        if (dashboardSection) dashboardSection.classList.remove('hidden');
        
        if (this.currentUser) {
            this.setupPeriodicRefresh();
            this.updateUserProfile();
        }
        
        const loginBtn = document.getElementById('loginBtn');
        const registerBtn = document.getElementById('registerBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        const userProfile = document.getElementById('userProfile');
        
        if (loginBtn) loginBtn.classList.add('hidden');
        if (registerBtn) registerBtn.classList.add('hidden');
        if (logoutBtn) logoutBtn.classList.remove('hidden');
        if (userProfile) userProfile.classList.remove('hidden');
        
        if (this.currentUser) {
            const userNameElement = document.getElementById('userName');
            if (userNameElement) {
                userNameElement.textContent = this.currentUser.first_name;
            }
        }
        
        this.loadOpportunities();
        this.updateDashboardStats();
        
        // Show admin panel if user is admin
        if (this.currentUser && this.currentUser.is_admin) {
            this.showAdminPanel();
        } else {
            this.hideAdminPanel();
        }
    }
    
    showAdminPanel() {
        const adminPanel = document.getElementById('adminPanel');
        if (adminPanel) {
            adminPanel.classList.remove('hidden');
            this.loadFetcherStatus();
            this.loadFetchLogs();
        }
    }
    
    hideAdminPanel() {
        const adminPanel = document.getElementById('adminPanel');
        if (adminPanel) {
            adminPanel.classList.add('hidden');
        }
    }
    
    async fetchOpportunities() {
        const fetchBtn = document.getElementById('fetchOpportunitiesBtn');
        const fetchLoading = document.getElementById('fetchLoading');
        const fetchStatus = document.getElementById('fetchStatus');
        const fetchStatusContent = document.getElementById('fetchStatusContent');
        
        if (fetchBtn) {
            fetchBtn.disabled = true;
            fetchBtn.textContent = 'Fetching...';
        }
        if (fetchLoading) fetchLoading.classList.remove('hidden');
        if (fetchStatus) fetchStatus.classList.add('hidden');
        
        try {
            // Get user email from localStorage for serverless session fallback
            const userEmail = localStorage.getItem('userEmail') || this.currentUser?.email;
            const url = userEmail ? `${this.apiBaseUrl}/admin/fetch-opportunities?email=${encodeURIComponent(userEmail)}` : `${this.apiBaseUrl}/admin/fetch-opportunities`;
            
            const response = await fetch(url, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            // Check content type before parsing
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                // Response is not JSON, likely an HTML error page
                const text = await response.text();
                console.error('Non-JSON response received:', {
                    status: response.status,
                    statusText: response.statusText,
                    contentType: contentType,
                    responsePreview: text.substring(0, 200)
                });
                throw new Error(`Server returned ${response.status} ${response.statusText}. Expected JSON but got ${contentType || 'unknown'}`);
            }
            
            if (response.ok) {
                const data = await response.json();
                const results = data.results || {};
                
                let statusHtml = '<div class="space-y-2">';
                statusHtml += `<p class="font-semibold text-green-700">✓ Fetch completed successfully!</p>`;
                statusHtml += `<p class="text-sm">Total fetched: ${results.total_fetched || 0}</p>`;
                statusHtml += `<p class="text-sm">New opportunities: ${results.total_new || 0}</p>`;
                statusHtml += `<p class="text-sm">Updated opportunities: ${results.total_updated || 0}</p>`;
                
                if (results.sources && Object.keys(results.sources).length > 0) {
                    statusHtml += '<div class="mt-4 pt-4 border-t border-gray-300">';
                    statusHtml += '<p class="font-semibold text-xs text-gray-600 mb-2">By Source:</p>';
                    for (const [source, stats] of Object.entries(results.sources)) {
                        statusHtml += `<p class="text-xs text-gray-600">${source}: ${stats.fetched || 0} fetched, ${stats.new || 0} new, ${stats.updated || 0} updated</p>`;
                    }
                    statusHtml += '</div>';
                }
                
                statusHtml += '</div>';
                
                if (fetchStatusContent) fetchStatusContent.innerHTML = statusHtml;
                if (fetchStatus) fetchStatus.classList.remove('hidden');
                
                // Reload opportunities
                this.loadOpportunities();
                this.updateDashboardStats();
                
                this.showMessage('Opportunities fetched successfully!', 'success');
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to fetch opportunities');
            }
        } catch (error) {
            console.error('Error fetching opportunities:', error);
            if (fetchStatusContent) {
                fetchStatusContent.innerHTML = `<p class="text-red-700">Error: ${error.message}</p>`;
            }
            if (fetchStatus) fetchStatus.classList.remove('hidden');
            this.showMessage(`Failed to fetch opportunities: ${error.message}`, 'error');
        } finally {
            if (fetchBtn) {
                fetchBtn.disabled = false;
                fetchBtn.textContent = 'Fetch Opportunities Now';
            }
            if (fetchLoading) fetchLoading.classList.add('hidden');
            
            // Reload logs
            this.loadFetchLogs();
        }
    }
    
    async loadFetchLogs() {
        const logsContainer = document.getElementById('fetchLogsContainer');
        if (!logsContainer) return;
        
        try {
            // Get user email from localStorage for serverless session fallback
            const userEmail = localStorage.getItem('userEmail') || this.currentUser?.email;
            const url = userEmail ? `${this.apiBaseUrl}/admin/fetch-logs?limit=10&email=${encodeURIComponent(userEmail)}` : `${this.apiBaseUrl}/admin/fetch-logs?limit=10`;
            
            const response = await fetch(url, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                const logs = data.logs || [];
                
                if (logs.length === 0) {
                    logsContainer.innerHTML = '<p class="text-sm text-gray-500">No fetch logs available</p>';
                    return;
                }
                
                let logsHtml = '<div class="space-y-2">';
                logs.reverse().forEach(log => {
                    logsHtml += `<div class="text-xs border-b border-gray-200 pb-2">`;
                    logsHtml += `<p class="font-semibold text-gray-800">${log.source}</p>`;
                    logsHtml += `<p class="text-gray-600">Fetched: ${log.fetched || 0} | New: ${log.new || 0} | Updated: ${log.updated || 0}`;
                    if (log.errors > 0) {
                        logsHtml += ` | <span class="text-red-600">Errors: ${log.errors}</span>`;
                    }
                    logsHtml += `</p>`;
                    logsHtml += `<p class="text-gray-500 text-xs">${new Date(log.timestamp).toLocaleString()}</p>`;
                    logsHtml += `</div>`;
                });
                logsHtml += '</div>';
                
                logsContainer.innerHTML = logsHtml;
            } else {
                logsContainer.innerHTML = '<p class="text-sm text-red-600">Failed to load fetch logs</p>';
            }
        } catch (error) {
            console.error('Error loading fetch logs:', error);
            logsContainer.innerHTML = '<p class="text-sm text-red-600">Error loading fetch logs</p>';
        }
    }
    
    async loadFetcherStatus() {
        const statusContainer = document.getElementById('fetcherStatusContainer');
        if (!statusContainer) return;
        
        try {
            // Get user email from localStorage for serverless session fallback
            const userEmail = localStorage.getItem('userEmail') || this.currentUser?.email;
            const url = userEmail ? `${this.apiBaseUrl}/admin/fetchers/status?email=${encodeURIComponent(userEmail)}` : `${this.apiBaseUrl}/admin/fetchers/status`;
            
            const response = await fetch(url, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const status = await response.json();
                
                let statusHtml = '<div class="space-y-2 text-sm">';
                statusHtml += `<p class="font-semibold text-gray-800">Enabled Fetchers:</p>`;
                statusHtml += `<p class="text-gray-600">${(status.enabled_fetchers || []).join(', ') || 'All'}</p>`;
                
                statusHtml += `<p class="font-semibold text-gray-800 mt-4">API Keys Configured:</p>`;
                const apiKeys = status.api_keys_configured || {};
                statusHtml += `<p class="text-gray-600">Jooble: ${apiKeys.jooble ? '✓' : '✗'}</p>`;
                statusHtml += `<p class="text-gray-600">Authentic Jobs: ${apiKeys.authentic_jobs ? '✓' : '✗'}</p>`;
                statusHtml += `<p class="text-gray-600">Meetup: ${apiKeys.meetup ? '✓' : '✗'}</p>`;
                
                statusHtml += `<p class="font-semibold text-gray-800 mt-4">RSS Feeds:</p>`;
                statusHtml += `<p class="text-gray-600 text-xs">${(status.rss_feeds || []).slice(0, 3).join(', ')}${(status.rss_feeds || []).length > 3 ? '...' : ''}</p>`;
                
                statusHtml += '</div>';
                
                statusContainer.innerHTML = statusHtml;
            } else {
                statusContainer.innerHTML = '<p class="text-sm text-red-600">Failed to load fetcher status</p>';
            }
        } catch (error) {
            console.error('Error loading fetcher status:', error);
            statusContainer.innerHTML = '<p class="text-sm text-red-600">Error loading fetcher status</p>';
        }
    }
    
    switchAdminTab(tabName) {
        // Hide all tab contents
        document.querySelectorAll('.admin-tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        
        // Remove active class from all tabs
        document.querySelectorAll('.admin-tab').forEach(tab => {
            tab.classList.remove('active', 'border-blue-600', 'text-blue-600');
            tab.classList.add('border-transparent', 'text-gray-500');
        });
        
        // Show selected tab content
        const contentId = `adminTabContent${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`;
        const content = document.getElementById(contentId);
        if (content) {
            content.classList.remove('hidden');
        }
        
        // Activate selected tab
        const tabId = `adminTab${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`;
        const tab = document.getElementById(tabId);
        if (tab) {
            tab.classList.add('active', 'border-blue-600', 'text-blue-600');
            tab.classList.remove('border-transparent', 'text-gray-500');
        }
        
        // Load data for the selected tab
        if (tabName === 'opportunities') {
            this.loadAdminOpportunities();
        } else if (tabName === 'users') {
            this.loadAdminUsers();
        }
    }
    
    async loadAdminOpportunities() {
        const container = document.getElementById('adminOpportunitiesContainer');
        if (!container) return;
        
        container.innerHTML = '<p class="text-sm text-gray-500">Loading opportunities...</p>';
        
        try {
            // Get user email from localStorage for serverless session fallback
            const userEmail = localStorage.getItem('userEmail') || this.currentUser?.email;
            const url = userEmail ? `${this.apiBaseUrl}/admin/opportunities?email=${encodeURIComponent(userEmail)}` : `${this.apiBaseUrl}/admin/opportunities`;
            
            const response = await fetch(url, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const opportunities = await response.json();
                
                if (opportunities.length === 0) {
                    container.innerHTML = '<p class="text-sm text-gray-500">No opportunities found</p>';
                    return;
                }
                
                let html = '<div class="space-y-3">';
                opportunities.forEach(opp => {
                    const isDeleted = opp.is_deleted || false;
                    html += `<div class="bg-gray-50 rounded-lg p-4 border ${isDeleted ? 'border-red-200 opacity-60' : 'border-gray-200'}">`;
                    html += `<div class="flex justify-between items-start">`;
                    html += `<div class="flex-1">`;
                    html += `<div class="flex items-center gap-2 mb-2">`;
                    html += `<h5 class="font-semibold text-gray-900">${this.escapeHtml(opp.title)}</h5>`;
                    if (isDeleted) {
                        html += `<span class="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-semibold">Deleted</span>`;
                    }
                    if (opp.auto_fetched) {
                        html += `<span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">Auto-fetched</span>`;
                    }
                    html += `</div>`;
                    html += `<p class="text-sm text-gray-600 mb-1"><span class="font-medium">Company:</span> ${this.escapeHtml(opp.company)} | <span class="font-medium">Location:</span> ${this.escapeHtml(opp.location)}</p>`;
                    html += `<p class="text-sm text-gray-600 mb-1"><span class="font-medium">Type:</span> ${this.escapeHtml(opp.type)} | <span class="font-medium">Category:</span> ${this.escapeHtml(opp.category)}</p>`;
                    html += `<p class="text-xs text-gray-500">Created: ${new Date(opp.created_at).toLocaleString()}</p>`;
                    html += `</div>`;
                    html += `<div class="flex gap-2">`;
                    html += `<button onclick="app.editOpportunity(${opp.id})" class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">Edit</button>`;
                    if (isDeleted) {
                        html += `<button onclick="app.restoreOpportunity(${opp.id})" class="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700">Restore</button>`;
                    } else {
                        html += `<button onclick="app.deleteOpportunity(${opp.id})" class="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700">Delete</button>`;
                    }
                    html += `</div>`;
                    html += `</div>`;
                    html += `</div>`;
                });
                html += '</div>';
                
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p class="text-sm text-red-600">Failed to load opportunities</p>';
            }
        } catch (error) {
            console.error('Error loading admin opportunities:', error);
            container.innerHTML = '<p class="text-sm text-red-600">Error loading opportunities</p>';
        }
    }
    
    async loadAdminUsers() {
        const container = document.getElementById('adminUsersContainer');
        if (!container) return;
        
        container.innerHTML = '<p class="text-sm text-gray-500">Loading users...</p>';
        
        try {
            // Get user email from localStorage for serverless session fallback
            const userEmail = localStorage.getItem('userEmail') || this.currentUser?.email;
            const url = userEmail ? `${this.apiBaseUrl}/admin/users?email=${encodeURIComponent(userEmail)}` : `${this.apiBaseUrl}/admin/users`;
            
            const response = await fetch(url, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const users = await response.json();
                
                if (users.length === 0) {
                    container.innerHTML = '<p class="text-sm text-gray-500">No users found</p>';
                    return;
                }
                
                let html = '<div class="space-y-3">';
                users.forEach(user => {
                    html += `<div class="bg-gray-50 rounded-lg p-4 border border-gray-200">`;
                    html += `<div class="flex justify-between items-start">`;
                    html += `<div class="flex-1">`;
                    html += `<div class="flex items-center gap-2 mb-2">`;
                    html += `<h5 class="font-semibold text-gray-900">${this.escapeHtml(user.first_name)} ${this.escapeHtml(user.last_name)}</h5>`;
                    if (user.is_admin) {
                        html += `<span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-semibold">Admin</span>`;
                    }
                    html += `</div>`;
                    html += `<p class="text-sm text-gray-600 mb-1"><span class="font-medium">Email:</span> ${this.escapeHtml(user.email)}</p>`;
                    html += `<p class="text-xs text-gray-500">Joined: ${new Date(user.created_at).toLocaleString()}</p>`;
                    html += `</div>`;
                    html += `<div class="flex gap-2">`;
                    if (!user.is_admin) {
                        html += `<button onclick="app.promoteToAdmin('${user.email}')" class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">Promote to Admin</button>`;
                    }
                    html += `</div>`;
                    html += `</div>`;
                    html += `</div>`;
                });
                html += '</div>';
                
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p class="text-sm text-red-600">Failed to load users</p>';
            }
        } catch (error) {
            console.error('Error loading admin users:', error);
            container.innerHTML = '<p class="text-sm text-red-600">Error loading users</p>';
        }
    }
    
    async deleteOpportunity(id) {
        if (!confirm('Are you sure you want to delete this opportunity?')) {
            return;
        }
        
        try {
            // Get user email from localStorage for serverless session fallback
            const userEmail = localStorage.getItem('userEmail') || this.currentUser?.email;
            const url = userEmail ? `${this.apiBaseUrl}/admin/opportunities/${id}?email=${encodeURIComponent(userEmail)}` : `${this.apiBaseUrl}/admin/opportunities/${id}`;
            
            const response = await fetch(url, {
                method: 'DELETE',
                credentials: 'include'
            });
            
            if (response.ok) {
                this.showMessage('Opportunity deleted successfully', 'success');
                this.loadAdminOpportunities();
                this.loadOpportunities();
                this.updateDashboardStats();
            } else {
                const error = await response.json();
                this.showMessage(`Failed to delete: ${error.error}`, 'error');
            }
        } catch (error) {
            this.showMessage(`Error deleting opportunity: ${error.message}`, 'error');
        }
    }
    
    async restoreOpportunity(id) {
        try {
            // Get user email from localStorage for serverless session fallback
            const userEmail = localStorage.getItem('userEmail') || this.currentUser?.email;
            const url = userEmail ? `${this.apiBaseUrl}/admin/opportunities/${id}?email=${encodeURIComponent(userEmail)}` : `${this.apiBaseUrl}/admin/opportunities/${id}`;
            
            const response = await fetch(url, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ is_deleted: false })
            });
            
            if (response.ok) {
                this.showMessage('Opportunity restored successfully', 'success');
                this.loadAdminOpportunities();
                this.loadOpportunities();
                this.updateDashboardStats();
            } else {
                const error = await response.json();
                this.showMessage(`Failed to restore: ${error.error}`, 'error');
            }
        } catch (error) {
            this.showMessage(`Error restoring opportunity: ${error.message}`, 'error');
        }
    }
    
    editOpportunity(id) {
        // TODO: Implement edit opportunity modal/form
        this.showMessage('Edit functionality coming soon!', 'info');
    }
    
    async promoteToAdmin(email) {
        if (!confirm(`Are you sure you want to promote ${email} to admin?`)) {
            return;
        }
        
        const secretKey = prompt('Enter admin secret key:');
        if (!secretKey) {
            return;
        }
        
        try {
            // Get current user email from localStorage for serverless session fallback
            const currentUserEmail = localStorage.getItem('userEmail') || this.currentUser?.email;
            const url = currentUserEmail ? `${this.apiBaseUrl}/admin/promote?email=${encodeURIComponent(currentUserEmail)}` : `${this.apiBaseUrl}/admin/promote`;
            
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    email: email,
                    secret_key: secretKey
                })
            });
            
            if (response.ok) {
                this.showMessage('User promoted to admin successfully', 'success');
                this.loadAdminUsers();
            } else {
                const error = await response.json();
                this.showMessage(`Failed to promote: ${error.error}`, 'error');
            }
        } catch (error) {
            this.showMessage(`Error promoting user: ${error.message}`, 'error');
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showCreateOpportunityModal() {
        const modal = document.getElementById('createOpportunityModal');
        if (modal) {
            modal.classList.remove('hidden');
            document.getElementById('createOpportunityForm').reset();
        }
    }
    
    closeCreateOpportunityModal() {
        const modal = document.getElementById('createOpportunityModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }
    
    async handleCreateOpportunity(event) {
        event.preventDefault();
        
        const opportunityData = {
            title: document.getElementById('oppTitle').value.trim(),
            company: document.getElementById('oppCompany').value.trim(),
            location: document.getElementById('oppLocation').value.trim(),
            type: document.getElementById('oppType').value,
            category: document.getElementById('oppCategory').value,
            description: document.getElementById('oppDescription').value.trim(),
            requirements: document.getElementById('oppRequirements').value.trim(),
            salary: document.getElementById('oppSalary').value.trim(),
            application_url: document.getElementById('oppApplicationUrl').value.trim()
        };
        
        try {
            // Get user email from localStorage for serverless session fallback
            const userEmail = localStorage.getItem('userEmail') || this.currentUser?.email;
            const url = userEmail ? `${this.apiBaseUrl}/admin/opportunities?email=${encodeURIComponent(userEmail)}` : `${this.apiBaseUrl}/admin/opportunities`;
            
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(opportunityData)
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showMessage('Opportunity created successfully!', 'success');
                this.closeCreateOpportunityModal();
                this.loadAdminOpportunities();
                this.loadOpportunities();
                this.updateDashboardStats();
            } else {
                const error = await response.json();
                this.showMessage(`Failed to create: ${error.error}`, 'error');
            }
        } catch (error) {
            this.showMessage(`Error creating opportunity: ${error.message}`, 'error');
        }
    }

    showDashboard() {
        if (!this.isNavigating) {
            this.navigateToRoute('dashboard');
        } else {
            this.showDashboardInternal();
        }
    }

    updateUserProfile() {
        if (!this.currentUser) return;
        
        const userProfile = document.getElementById('userProfile');
        const userNameNav = document.getElementById('userNameNav');
        const userAvatar = document.getElementById('userAvatar');
        
        if (userProfile) userProfile.classList.remove('hidden');
        if (userNameNav) {
            userNameNav.textContent = `${this.currentUser.first_name} ${this.currentUser.last_name}`;
        }
        if (userAvatar) {
            const initials = `${this.currentUser.first_name[0]}${this.currentUser.last_name[0]}`.toUpperCase();
            userAvatar.textContent = initials;
        }
    }

    showWelcomeSectionInternal() {
        document.getElementById('dashboardSection').classList.add('hidden');
        document.getElementById('opportunitiesSection').classList.add('hidden');
        document.getElementById('welcomeSection').classList.remove('hidden');
        
        document.getElementById('logoutBtn').classList.add('hidden');
        document.getElementById('loginBtn').classList.remove('hidden');
        document.getElementById('registerBtn').classList.remove('hidden');
        const userProfile = document.getElementById('userProfile');
        if (userProfile) userProfile.classList.add('hidden');
    }

    showWelcomeSection() {
        if (!this.isNavigating) {
            this.navigateToRoute('welcome');
        } else {
            this.showWelcomeSectionInternal();
        }
    }

    showOpportunitiesSectionInternal() {
        document.getElementById('welcomeSection').classList.add('hidden');
        document.getElementById('dashboardSection').classList.add('hidden');
        document.getElementById('opportunitiesSection').classList.remove('hidden');
        
        this.loadOpportunities();
        this.loadFilters();
    }

    showOpportunitiesSection() {
        if (!this.currentUser) {
            this.showMessage('Please login to browse opportunities.', 'error');
            this.showLoginModal();
            return;
        }

        if (!this.isNavigating) {
            this.navigateToRoute('opportunities');
        } else {
            this.showOpportunitiesSectionInternal();
        }
    }

    ensureSingleSectionVisible() {
        const sections = ['welcomeSection', 'dashboardSection', 'opportunitiesSection'];
        sections.forEach(sectionId => {
            const element = document.getElementById(sectionId);
            if (element) {
                element.classList.add('hidden');
            }
        });
        
        const welcome = document.getElementById('welcomeSection');
        if (welcome) {
            welcome.classList.remove('hidden');
        }
    }

    showMessage(message, type = 'info', elementId = null) {
        const messageElement = elementId ? document.getElementById(elementId) : null;
        
        if (messageElement) {
            messageElement.textContent = message;
            messageElement.className = `text-sm font-medium ${type === 'error' ? 'text-red-600' : type === 'success' ? 'text-green-600' : 'text-blue-600'}`;
        } else {
            const notification = document.createElement('div');
            notification.className = `toast ${type}`;
            
            const icon = type === 'success' ? 
                '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>' :
                type === 'error' ?
                '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>' :
                '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
            
            notification.innerHTML = `${icon}<span>${message}</span>`;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, 4000);
        }
    }

    setupPeriodicRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this.refreshInterval = setInterval(() => {
            if (this.currentUser) {
                this.loadOpportunities();
            }
        }, 30000);
    }

    toggleOpportunityExpansion(card) {
        const expandedContent = card.querySelector('.expanded-content');
        const learnMoreBtn = card.querySelector('.learn-more-btn');
        const isExpanded = !expandedContent.classList.contains('hidden');
        
        if (isExpanded) {
            expandedContent.classList.add('hidden');
            learnMoreBtn.innerHTML = 'Learn More <svg class="w-4 h-4 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>';
            card.classList.remove('expanded');
        } else {
            expandedContent.classList.remove('hidden');
            learnMoreBtn.innerHTML = 'Show Less <svg class="w-4 h-4 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path></svg>';
            card.classList.add('expanded');
            
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
