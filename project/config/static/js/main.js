// Main JavaScript for Waste Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarToggleTop = document.getElementById('sidebarToggleTop');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');

    function toggleSidebar() {
        sidebar.classList.toggle('show');
        
        // For desktop: adjust main content margin
        if (window.innerWidth > 768) {
            if (sidebar.classList.contains('show')) {
                mainContent.style.marginLeft = '0';
            } else {
                mainContent.style.marginLeft = 'var(--sidebar-width)';
            }
        }
    }

    // Add event listeners for both toggle buttons
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSidebar();
        });
    }

    if (sidebarToggleTop) {
        sidebarToggleTop.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSidebar();
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768 && sidebar.classList.contains('show')) {
            if (!sidebar.contains(event.target) && 
                !event.target.closest('#sidebarToggleTop') && 
                !event.target.closest('#sidebarToggle')) {
                sidebar.classList.remove('show');
            }
        }
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('show');
            mainContent.style.marginLeft = 'var(--sidebar-width)';
        } else {
            mainContent.style.marginLeft = '0';
        }
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-delete') || 'Êtes-vous sûr de vouloir supprimer cet élément ?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Format numbers in tables
    const numberCells = document.querySelectorAll('.format-number');
    numberCells.forEach(function(cell) {
        const value = parseFloat(cell.textContent);
        if (!isNaN(value)) {
            cell.textContent = value.toLocaleString('fr-FR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
    });

    // Search functionality with debounce
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        let timeout;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                // Trigger search after 300ms of no typing
                const form = input.closest('form');
                if (form) {
                    form.submit();
                }
            }, 300);
        });
    });

    // Auto-calculate totals in forms
    const calculateTotalInputs = document.querySelectorAll('.calculate-total');
    calculateTotalInputs.forEach(function(input) {
        input.addEventListener('input', calculateFormTotals);
    });

    function calculateFormTotals() {
        // This function can be customized based on specific form requirements
        const quantityInputs = document.querySelectorAll('input[name*="quantity"]');
        const priceInputs = document.querySelectorAll('input[name*="unit_price"]');
        let total = 0;

        quantityInputs.forEach(function(qtyInput, index) {
            const priceInput = priceInputs[index];
            if (qtyInput && priceInput) {
                const qty = parseFloat(qtyInput.value) || 0;
                const price = parseFloat(priceInput.value) || 0;
                const lineTotal = qty * price;
                
                // Update line total display if exists
                const lineTotalDisplay = qtyInput.closest('tr')?.querySelector('.line-total');
                if (lineTotalDisplay) {
                    lineTotalDisplay.textContent = lineTotal.toFixed(2);
                }
                
                total += lineTotal;
            }
        });

        // Update total display
        const totalDisplay = document.getElementById('total-display');
        if (totalDisplay) {
            totalDisplay.textContent = total.toFixed(2) + ' DA';
        }
    }

    // Print functionality
    const printButtons = document.querySelectorAll('.print-btn');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const printUrl = this.getAttribute('href');
            const printWindow = window.open(printUrl, '_blank');
            printWindow.onload = function() {
                printWindow.print();
            };
        });
    });

    // Status update functionality
    const statusSelects = document.querySelectorAll('.status-select');
    statusSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            if (form && confirm('Mettre à jour le statut ?')) {
                form.submit();
            }
        });
    });

    // Dynamic form fields (add/remove)
    const addFieldButtons = document.querySelectorAll('.add-field-btn');
    addFieldButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const template = this.getAttribute('data-template');
            const container = document.querySelector(this.getAttribute('data-container'));
            if (template && container) {
                const newField = document.createElement('div');
                newField.innerHTML = template;
                container.appendChild(newField);
            }
        });
    });

    // Remove field functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-field-btn')) {
            const fieldContainer = e.target.closest('.field-container');
            if (fieldContainer && confirm('Supprimer ce champ ?')) {
                fieldContainer.remove();
            }
        }
    });

    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const file = this.files[0];
            const preview = document.querySelector(this.getAttribute('data-preview'));
            
            if (file && preview) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (file.type.startsWith('image/')) {
                        preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px;">`;
                    } else {
                        preview.innerHTML = `<p>Fichier sélectionné: ${file.name}</p>`;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Loading states for buttons
    const loadingButtons = document.querySelectorAll('.btn-loading');
    loadingButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Chargement...';
            this.disabled = true;
            
            // Re-enable after 3 seconds (adjust as needed)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 3000);
        });
    });

    // Table sorting (basic implementation)
    const sortableHeaders = document.querySelectorAll('.sortable');
    sortableHeaders.forEach(function(header) {
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(this.parentNode.children).indexOf(this);
            const isAscending = !this.classList.contains('sort-asc');
            
            // Remove existing sort classes
            sortableHeaders.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
            
            // Add appropriate sort class
            this.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
            
            // Sort rows
            rows.sort(function(a, b) {
                const aValue = a.cells[columnIndex].textContent.trim();
                const bValue = b.cells[columnIndex].textContent.trim();
                
                // Try to parse as numbers
                const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
                const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAscending ? aNum - bNum : bNum - aNum;
                } else {
                    return isAscending ? 
                        aValue.localeCompare(bValue) : 
                        bValue.localeCompare(aValue);
                }
            });
            
            // Reorder rows in DOM
            rows.forEach(row => tbody.appendChild(row));
        });
    });

    // Initialize any charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = 'Nunito Sans, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto';
        Chart.defaults.color = '#858796';
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+S to save forms
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const form = document.querySelector('form');
            if (form) {
                form.submit();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
    });

    // Auto-save draft functionality (for forms)
    const autoSaveForms = document.querySelectorAll('.auto-save');
    autoSaveForms.forEach(function(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(function(input) {
            input.addEventListener('input', debounce(function() {
                // Save to localStorage
                const formData = new FormData(form);
                const data = Object.fromEntries(formData);
                localStorage.setItem('draft_' + form.id, JSON.stringify(data));
                
                // Show save indicator
                showSaveIndicator();
            }, 1000));
        });
        
        // Load draft on page load
        const savedData = localStorage.getItem('draft_' + form.id);
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(function(key) {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
        }
    });

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function showSaveIndicator() {
        // Create or show save indicator
        let indicator = document.getElementById('save-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'save-indicator';
            indicator.className = 'position-fixed top-0 end-0 m-3 alert alert-success alert-sm';
            indicator.innerHTML = '<i class="fas fa-check me-2"></i>Brouillon sauvegardé';
            document.body.appendChild(indicator);
        }
        
        indicator.style.display = 'block';
        setTimeout(() => {
            indicator.style.display = 'none';
        }, 2000);
    }
});

// Utility functions
function formatCurrency(amount, currency = 'DA') {
    return new Intl.NumberFormat('fr-FR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount) + ' ' + currency;
}

function formatDate(date, format = 'dd/mm/yyyy') {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    
    return format
        .replace('dd', day)
        .replace('mm', month)
        .replace('yyyy', year);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Export functions for use in other scripts
window.WasteManagement = {
    formatCurrency,
    formatDate,
    showNotification
};