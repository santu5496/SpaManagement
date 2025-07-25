// Main JavaScript functionality for Spa & Salon Management Suite

// Global application state and utilities
window.SpaApp = {
    currentUser: null,
    notifications: [],
    settings: {
        autoRefresh: true,
        refreshInterval: 30000,
        theme: 'dark'
    }
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupGlobalEventListeners();
    initializeComponents();
    setupFormValidation();
    setupNotifications();
    loadUserPreferences();
    
    // Auto-refresh data if enabled
    if (SpaApp.settings.autoRefresh) {
        startAutoRefresh();
    }
}

// Global event listeners
function setupGlobalEventListeners() {
    // Handle all modal events
    document.addEventListener('show.bs.modal', handleModalShow);
    document.addEventListener('hidden.bs.modal', handleModalHidden);
    
    // Handle form submissions
    document.addEventListener('submit', handleFormSubmit);
    
    // Handle button clicks
    document.addEventListener('click', handleButtonClick);
    
    // Handle input changes
    document.addEventListener('change', handleInputChange);
    
    // Handle keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Handle window resize
    window.addEventListener('resize', handleWindowResize);
    
    // Handle connection status
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);
}

// Modal event handlers
function handleModalShow(event) {
    const modal = event.target;
    const modalId = modal.id;
    
    // Initialize modal-specific functionality
    switch(modalId) {
        case 'addAppointmentModal':
            initializeAppointmentModal(modal);
            break;
        case 'addClientModal':
            initializeClientModal(modal);
            break;
        case 'addStaffModal':
            initializeStaffModal(modal);
            break;
        case 'addInventoryModal':
            initializeInventoryModal(modal);
            break;
        case 'updateStockModal':
            initializeStockModal(modal);
            break;
    }
}

function handleModalHidden(event) {
    const modal = event.target;
    
    // Clear form data and reset validation
    const forms = modal.querySelectorAll('form');
    forms.forEach(form => {
        form.reset();
        clearFormValidation(form);
    });
}

// Form submission handler
function handleFormSubmit(event) {
    const form = event.target;
    const formId = form.id;
    
    // Validate form before submission
    if (!validateForm(form)) {
        event.preventDefault();
        return false;
    }
    
    // Show loading state
    showFormLoading(form);
    
    // Handle specific forms
    switch(formId) {
        case 'appointmentForm':
            return handleAppointmentSubmit(event);
        case 'clientForm':
            return handleClientSubmit(event);
        case 'inventoryForm':
            return handleInventorySubmit(event);
    }
}

// Button click handler
function handleButtonClick(event) {
    const button = event.target.closest('button');
    if (!button) return;
    
    const action = button.dataset.action;
    const id = button.dataset.id;
    
    switch(action) {
        case 'delete':
            handleDeleteAction(button, id);
            break;
        case 'toggle-status':
            handleToggleStatus(button, id);
            break;
        case 'mark-paid':
            handleMarkPaid(button, id);
            break;
        case 'send-notification':
            handleSendNotification(button, id);
            break;
        case 'export-data':
            handleExportData(button);
            break;
        case 'print':
            handlePrint(button);
            break;
    }
}

// Input change handler
function handleInputChange(event) {
    const input = event.target;
    
    // Real-time validation
    if (input.form) {
        validateField(input);
    }
    
    // Handle specific input types
    switch(input.type) {
        case 'tel':
            formatPhoneNumber(input);
            break;
        case 'email':
            validateEmail(input);
            break;
        case 'number':
            validateNumericInput(input);
            break;
    }
    
    // Handle dependent fields
    if (input.id === 'service_id') {
        updateServiceDependentFields(input);
    } else if (input.id === 'client_id') {
        loadClientData(input.value);
    }
}

// Initialize components
function initializeComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize date pickers
    initializeDatePickers();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize data tables
    initializeDataTables();
    
    // Initialize charts
    initializeCharts();
}

// Form validation
function setupFormValidation() {
    // Add validation classes to all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.noValidate = true;
        setupFormFieldValidation(form);
    });
}

function setupFormFieldValidation(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => clearFieldError(input));
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    const required = field.hasAttribute('required');
    
    // Clear previous validation
    clearFieldError(field);
    
    // Required field validation
    if (required && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    if (!value) return true; // Skip validation for empty non-required fields
    
    // Type-specific validation
    switch(type) {
        case 'email':
            if (!isValidEmail(value)) {
                showFieldError(field, 'Please enter a valid email address');
                return false;
            }
            break;
            
        case 'tel':
            if (!isValidPhone(value)) {
                showFieldError(field, 'Please enter a valid phone number');
                return false;
            }
            break;
            
        case 'number':
            const min = parseFloat(field.min);
            const max = parseFloat(field.max);
            const numValue = parseFloat(value);
            
            if (isNaN(numValue)) {
                showFieldError(field, 'Please enter a valid number');
                return false;
            }
            
            if (!isNaN(min) && numValue < min) {
                showFieldError(field, `Value must be at least ${min}`);
                return false;
            }
            
            if (!isNaN(max) && numValue > max) {
                showFieldError(field, `Value must be no more than ${max}`);
                return false;
            }
            break;
            
        case 'date':
        case 'datetime-local':
            if (!isValidDate(value)) {
                showFieldError(field, 'Please enter a valid date');
                return false;
            }
            break;
    }
    
    // Custom validation rules
    if (field.dataset.validation) {
        return validateCustomRules(field, value);
    }
    
    return true;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
    
    if (field.value.trim()) {
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
    }
}

function clearFormValidation(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.classList.remove('is-invalid', 'is-valid');
    });
    
    const errorDivs = form.querySelectorAll('.invalid-feedback');
    errorDivs.forEach(div => div.remove());
}

// Validation utilities
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

function isValidDate(dateString) {
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date);
}

// Numeric input validation for forms
function validateNumericInput(input) {
    const value = parseFloat(input.value);
    const min = parseFloat(input.min);
    const max = parseFloat(input.max);
    
    if (isNaN(value)) {
        showFieldError(input, 'Please enter a valid number');
        return false;
    }
    
    if (!isNaN(min) && value < min) {
        showFieldError(input, `Value must be at least ${min}`);
        return false;
    }
    
    if (!isNaN(max) && value > max) {
        showFieldError(input, `Value must be no more than ${max}`);
        return false;
    }
    
    clearFieldError(input);
    return true;
}

// Notification system
function setupNotifications() {
    createNotificationContainer();
    checkForSystemNotifications();
}

function createNotificationContainer() {
    if (!document.getElementById('notificationContainer')) {
        const container = document.createElement('div');
        container.id = 'notificationContainer';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    
    const bgClass = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-info';
    
    notification.className = `toast ${bgClass} text-white`;
    notification.setAttribute('role', 'alert');
    notification.innerHTML = `
        <div class="toast-header ${bgClass} text-white border-0">
            <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
            <strong class="me-auto">Notification</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    container.appendChild(notification);
    
    const toast = new bootstrap.Toast(notification, {
        delay: duration
    });
    
    toast.show();
    
    // Auto-remove after animation
    notification.addEventListener('hidden.bs.toast', () => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    });
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Modal initialization functions
function initializeAppointmentModal(modal) {
    const serviceSelect = modal.querySelector('#service_id');
    const amountInput = modal.querySelector('#amount');
    
    if (serviceSelect && amountInput) {
        serviceSelect.addEventListener('change', updateServicePrice);
        
        // Set default date to today
        const dateInput = modal.querySelector('#appointment_date');
        if (dateInput && !dateInput.value) {
            const now = new Date();
            const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
                .toISOString().slice(0, 16);
            dateInput.value = localDateTime;
        }
    }
}

function initializeClientModal(modal) {
    const phoneInput = modal.querySelector('input[type="tel"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    }
}

function initializeStaffModal(modal) {
    const roleSelect = modal.querySelector('#role');
    const commissionInput = modal.querySelector('#commission_rate');
    
    if (roleSelect && commissionInput) {
        roleSelect.addEventListener('change', function() {
            if (this.value === 'cashier') {
                commissionInput.value = '0';
                commissionInput.disabled = true;
            } else {
                commissionInput.disabled = false;
            }
        });
    }
}

function initializeInventoryModal(modal) {
    const categorySelect = modal.querySelector('#category');
    const expiryInput = modal.querySelector('#expiry_date');
    
    if (categorySelect && expiryInput) {
        categorySelect.addEventListener('change', function() {
            if (this.value === 'equipment') {
                expiryInput.disabled = true;
                expiryInput.value = '';
            } else {
                expiryInput.disabled = false;
            }
        });
    }
}

function initializeStockModal(modal) {
    const adjustmentInput = modal.querySelector('#stockAdjustment');
    const currentStockInput = modal.querySelector('#currentStock');
    const newStockInput = modal.querySelector('#newStock');
    
    if (adjustmentInput && currentStockInput && newStockInput) {
        adjustmentInput.addEventListener('input', function() {
            const current = parseInt(currentStockInput.value) || 0;
            const adjustment = parseInt(this.value) || 0;
            const newStock = Math.max(0, current + adjustment);
            newStockInput.value = newStock;
        });
    }
}

// Action handlers
function handleDeleteAction(button, id) {
    const itemType = button.dataset.type || 'item';
    const confirmMessage = `Are you sure you want to delete this ${itemType}? This action cannot be undone.`;
    
    if (confirm(confirmMessage)) {
        // Show loading state
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        // In a real app, this would make an API call
        setTimeout(() => {
            button.closest('tr')?.remove();
            showNotification(`${itemType} deleted successfully`, 'success');
        }, 1000);
    }
}

function handleToggleStatus(button, id) {
    const currentStatus = button.dataset.status === 'true';
    const newStatus = !currentStatus;
    const action = newStatus ? 'activate' : 'deactivate';
    
    if (confirm(`Are you sure you want to ${action} this item?`)) {
        button.disabled = true;
        
        // Update button state
        setTimeout(() => {
            button.dataset.status = newStatus.toString();
            button.innerHTML = newStatus ? 
                '<i class="fas fa-eye-slash"></i>' : 
                '<i class="fas fa-eye"></i>';
            button.disabled = false;
            
            showNotification(`Item ${action}d successfully`, 'success');
        }, 500);
    }
}

function handleMarkPaid(button, id) {
    if (confirm('Mark this payment as received?')) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        setTimeout(() => {
            const row = button.closest('tr');
            if (row) {
                row.classList.add('table-success');
                button.innerHTML = '<i class="fas fa-check"></i> Paid';
                button.className = 'btn btn-sm btn-success';
            }
            
            showNotification('Payment marked as received', 'success');
        }, 1000);
    }
}

// Utility functions
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length >= 6) {
        value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
    } else if (value.length >= 3) {
        value = value.replace(/(\d{3})(\d{1,3})/, '($1) $2');
    }
    
    input.value = value;
}

function updateServiceDependentFields(serviceSelect) {
    const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
    const amountInput = document.getElementById('amount');
    
    if (selectedOption && amountInput) {
        const priceMatch = selectedOption.text.match(/\$([0-9.]+)/);
        if (priceMatch) {
            amountInput.value = priceMatch[1];
        }
    }
}

function loadClientData(clientId) {
    if (!clientId) return;
    
    // In a real app, this would fetch client data from the server
    console.log('Loading client data for ID:', clientId);
}

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, this.dataset.target);
            }, 300);
        });
    });
}

function performSearch(query, target) {
    const rows = document.querySelectorAll(`${target} tbody tr`);
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const matches = text.includes(query.toLowerCase());
        row.style.display = matches ? '' : 'none';
    });
}

// Data table initialization
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        // Add sorting functionality
        setupTableSorting(table);
        
        // Add row selection
        setupRowSelection(table);
    });
}

function setupTableSorting(table) {
    const headers = table.querySelectorAll('th[data-sortable]');
    
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            sortTable(table, header);
        });
    });
}

function sortTable(table, header) {
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const isAscending = header.dataset.sortDirection !== 'asc';
    
    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();
        
        const comparison = aValue.localeCompare(bValue, undefined, { numeric: true });
        return isAscending ? comparison : -comparison;
    });
    
    // Update table
    const tbody = table.querySelector('tbody');
    rows.forEach(row => tbody.appendChild(row));
    
    // Update sort indicator
    header.dataset.sortDirection = isAscending ? 'asc' : 'desc';
    
    // Update header appearance
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sorted-asc', 'sorted-desc');
    });
    header.classList.add(`sorted-${header.dataset.sortDirection}`);
}

// Auto-refresh functionality
function startAutoRefresh() {
    setInterval(() => {
        if (document.visibilityState === 'visible') {
            refreshPageData();
        }
    }, SpaApp.settings.refreshInterval);
}

function refreshPageData() {
    const refreshableElements = document.querySelectorAll('[data-auto-refresh]');
    
    refreshableElements.forEach(element => {
        // Add subtle loading indicator
        element.classList.add('refreshing');
        
        // Remove indicator after a short delay
        setTimeout(() => {
            element.classList.remove('refreshing');
        }, 1000);
    });
}

// Keyboard shortcuts
function handleKeyboardShortcuts(event) {
    // Only handle shortcuts when not typing in input fields
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return;
    }
    
    if (event.ctrlKey || event.metaKey) {
        switch(event.key) {
            case 's':
                event.preventDefault();
                saveCurrentForm();
                break;
            case 'n':
                event.preventDefault();
                openNewItemModal();
                break;
            case 'f':
                event.preventDefault();
                focusSearch();
                break;
        }
    }
    
    // Escape key to close modals
    if (event.key === 'Escape') {
        closeTopModal();
    }
}

function saveCurrentForm() {
    const forms = document.querySelectorAll('form:not([hidden])');
    if (forms.length > 0) {
        const lastForm = forms[forms.length - 1];
        if (validateForm(lastForm)) {
            lastForm.submit();
        }
    }
}

function openNewItemModal() {
    const addButtons = document.querySelectorAll('[data-bs-toggle="modal"]');
    if (addButtons.length > 0) {
        addButtons[0].click();
    }
}

function focusSearch() {
    const searchInput = document.querySelector('input[type="search"], .search-input');
    if (searchInput) {
        searchInput.focus();
    }
}

function closeTopModal() {
    const openModals = document.querySelectorAll('.modal.show');
    if (openModals.length > 0) {
        const topModal = openModals[openModals.length - 1];
        bootstrap.Modal.getInstance(topModal)?.hide();
    }
}

// Connection status handlers
function handleOnlineStatus() {
    showNotification('Connection restored', 'success', 3000);
    document.body.classList.remove('offline');
}

function handleOfflineStatus() {
    showNotification('Connection lost. Some features may not work properly.', 'warning', 5000);
    document.body.classList.add('offline');
}

// Window resize handler
function handleWindowResize() {
    // Refresh any charts or components that need to adjust to new size
    if (window.Chart) {
        Chart.helpers.each(Chart.instances, function(instance) {
            instance.resize();
        });
    }
}

// Form loading states
function showFormLoading(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        submitButton.dataset.originalText = originalText;
    }
}

function hideFormLoading(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton && submitButton.dataset.originalText) {
        submitButton.disabled = false;
        submitButton.innerHTML = submitButton.dataset.originalText;
        delete submitButton.dataset.originalText;
    }
}

// Date picker initialization
function initializeDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"], input[type="datetime-local"]');
    
    dateInputs.forEach(input => {
        // Set min date to today for future appointments
        if (input.dataset.minToday === 'true') {
            const today = new Date().toISOString().split('T')[0];
            input.min = today;
        }
    });
}

// Chart initialization
function initializeCharts() {
    // Initialize any charts present on the page
    const chartElements = document.querySelectorAll('canvas[id$="Chart"]');
    
    chartElements.forEach(canvas => {
        if (canvas.dataset.initialized !== 'true') {
            initializeSpecificChart(canvas);
            canvas.dataset.initialized = 'true';
        }
    });
}

function initializeSpecificChart(canvas) {
    // Chart initialization would be handled by specific page scripts
    console.log('Initializing chart:', canvas.id);
}

// Load user preferences
function loadUserPreferences() {
    const savedPreferences = localStorage.getItem('spaAppPreferences');
    if (savedPreferences) {
        try {
            const preferences = JSON.parse(savedPreferences);
            Object.assign(SpaApp.settings, preferences);
        } catch (e) {
            console.warn('Failed to load user preferences:', e);
        }
    }
}

// Save user preferences
function saveUserPreferences() {
    localStorage.setItem('spaAppPreferences', JSON.stringify(SpaApp.settings));
}

// Export functions
function exportTableData(table, filename) {
    const rows = table.querySelectorAll('tr');
    const csvContent = Array.from(rows).map(row => {
        const cells = row.querySelectorAll('th, td');
        return Array.from(cells).map(cell => {
            return `"${cell.textContent.trim().replace(/"/g, '""')}"`;
        }).join(',');
    }).join('\n');
    
    downloadCSV(csvContent, filename);
}

function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Print functionality
function printElement(element) {
    const printWindow = window.open('', '', 'width=800,height=600');
    const styles = Array.from(document.styleSheets).map(sheet => {
        try {
            return Array.from(sheet.cssRules).map(rule => rule.cssText).join('\n');
        } catch (e) {
            return '';
        }
    }).join('\n');
    
    printWindow.document.write(`
        <html>
            <head>
                <title>Print</title>
                <style>${styles}</style>
            </head>
            <body>
                ${element.outerHTML}
            </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
    printWindow.close();
}

// System notifications check
function checkForSystemNotifications() {
    // Check for various system notifications
    setTimeout(() => {
        checkLowStockNotifications();
        checkExpiringItemsNotifications();
        checkUpcomingAppointmentsNotifications();
    }, 2000);
}

function checkLowStockNotifications() {
    const lowStockElements = document.querySelectorAll('[data-low-stock="true"]');
    if (lowStockElements.length > 0) {
        showNotification(`${lowStockElements.length} items are low in stock`, 'warning');
    }
}

function checkExpiringItemsNotifications() {
    const expiringElements = document.querySelectorAll('[data-expiring="true"]');
    if (expiringElements.length > 0) {
        showNotification(`${expiringElements.length} items are expiring soon`, 'warning');
    }
}

function checkUpcomingAppointmentsNotifications() {
    const upcomingElements = document.querySelectorAll('[data-upcoming="true"]');
    if (upcomingElements.length > 0) {
        showNotification(`${upcomingElements.length} appointments coming up`, 'info');
    }
}

// Expose useful functions globally
window.showNotification = showNotification;
window.exportTableData = exportTableData;
window.printElement = printElement;
window.validateForm = validateForm;
window.saveUserPreferences = saveUserPreferences;

// CSS for dynamic features
const additionalStyles = `
<style>
.refreshing {
    position: relative;
    opacity: 0.7;
}

.refreshing::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    animation: refreshing 1s infinite;
}

@keyframes refreshing {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.offline {
    filter: grayscale(20%);
}

.offline::before {
    content: 'Offline Mode';
    position: fixed;
    top: 60px;
    right: 20px;
    background: #dc3545;
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 0.8em;
    z-index: 9998;
}

.sorted-asc::after {
    content: ' ↑';
    font-weight: bold;
}

.sorted-desc::after {
    content: ' ↓';
    font-weight: bold;
}

th[data-sortable]:hover {
    background-color: rgba(0,0,0,0.05);
}

.toast-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
}

@media print {
    .no-print {
        display: none !important;
    }
}
</style>
`;

// Inject additional styles
if (document.head) {
    document.head.insertAdjacentHTML('beforeend', additionalStyles);
}

// ========== VERTICAL SIDEBAR NAVIGATION FUNCTIONS ==========

// Set active navigation link based on current page
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('#sidebar .nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        
        // Check if link href matches current path
        const linkPath = new URL(link.href).pathname;
        if (linkPath === currentPath || (currentPath === '/' && linkPath.includes('dashboard'))) {
            link.classList.add('active');
        }
    });
}

// Setup mobile sidebar auto-close functionality
function setupMobileSidebarClose() {
    const sidebarLinks = document.querySelectorAll('#sidebar .nav-link');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebar) {
        sidebarLinks.forEach(link => {
            link.addEventListener('click', function() {
                // Close sidebar on mobile after clicking a link
                if (window.innerWidth < 992) {
                    const offcanvas = bootstrap.Offcanvas.getInstance(sidebar);
                    if (offcanvas) {
                        offcanvas.hide();
                    }
                }
            });
        });
    }
}

// Initialize sidebar functionality when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setActiveNavLink();
    setupMobileSidebarClose();
    
    // Update active link on page navigation
    window.addEventListener('popstate', setActiveNavLink);
    
    // Handle sidebar state on window resize
    window.addEventListener('resize', function() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar && window.innerWidth >= 992) {
            // Hide offcanvas on desktop
            const offcanvas = bootstrap.Offcanvas.getInstance(sidebar);
            if (offcanvas) {
                offcanvas.hide();
            }
        }
    });
});
