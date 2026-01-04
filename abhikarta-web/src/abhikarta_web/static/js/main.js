/**
 * Abhikarta-LLM Main JavaScript
 * 
 * Copyright © 2025-2030, All Rights Reserved
 * Ashutosh Sinha
 * Email: ajsinha@gmail.com
 */

$(document).ready(function() {
    // Initialize DataTables with default settings
    if ($.fn.DataTable) {
        $('.data-table').DataTable({
            pageLength: 10,
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search...",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                paginate: {
                    first: '<i class="bi bi-chevron-double-left"></i>',
                    previous: '<i class="bi bi-chevron-left"></i>',
                    next: '<i class="bi bi-chevron-right"></i>',
                    last: '<i class="bi bi-chevron-double-right"></i>'
                }
            },
            dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                 '<"row"<"col-sm-12"tr>>' +
                 '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>'
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
    
    // Confirm delete actions
    $(document).on('click', '.btn-delete', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
            return false;
        }
    });
    
    // Form validation feedback
    $('form').on('submit', function() {
        var form = $(this);
        if (form[0].checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.addClass('was-validated');
    });
    
    // Tooltip initialization
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popover initialization
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle active nav links
    var currentPath = window.location.pathname;
    $('.navbar-nav .nav-link').each(function() {
        var linkPath = $(this).attr('href');
        if (currentPath === linkPath) {
            $(this).addClass('active');
        }
    });
    
    // JSON syntax highlighting (if any code blocks)
    $('pre.json').each(function() {
        try {
            var json = JSON.parse($(this).text());
            $(this).text(JSON.stringify(json, null, 2));
        } catch (e) {
            // Not valid JSON, leave as is
        }
    });
    
    // Copy to clipboard functionality
    $(document).on('click', '.btn-copy', function() {
        var target = $(this).data('target');
        var text = $(target).text();
        
        navigator.clipboard.writeText(text).then(function() {
            var btn = $(this);
            var originalText = btn.html();
            btn.html('<i class="bi bi-check"></i> Copied!');
            setTimeout(function() {
                btn.html(originalText);
            }, 2000);
        }.bind(this));
    });
    
    // Toggle password visibility
    $(document).on('click', '.toggle-password', function() {
        var input = $($(this).data('target'));
        var icon = $(this).find('i');
        
        if (input.attr('type') === 'password') {
            input.attr('type', 'text');
            icon.removeClass('bi-eye').addClass('bi-eye-slash');
        } else {
            input.attr('type', 'password');
            icon.removeClass('bi-eye-slash').addClass('bi-eye');
        }
    });
    
    // Auto-resize textarea
    $('textarea.auto-resize').each(function() {
        this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
    }).on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    console.log('Abhikarta-LLM initialized');
});

/**
 * Show loading spinner overlay
 */
function showLoading() {
    $('body').append('<div class="spinner-overlay"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');
}

/**
 * Hide loading spinner overlay
 */
function hideLoading() {
    $('.spinner-overlay').remove();
}

/**
 * Show toast notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, warning, info)
 */
function showToast(message, type) {
    type = type || 'info';
    var alertClass = type === 'error' ? 'danger' : type;
    var iconClass = {
        'success': 'bi-check-circle',
        'error': 'bi-exclamation-triangle',
        'warning': 'bi-exclamation-circle',
        'info': 'bi-info-circle'
    }[type] || 'bi-info-circle';
    
    var toast = $('<div class="alert alert-' + alertClass + ' alert-dismissible fade show position-fixed" ' +
                  'style="top: 80px; right: 20px; z-index: 9999; min-width: 300px;">' +
                  '<i class="bi ' + iconClass + ' me-2"></i>' + message +
                  '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                  '</div>');
    
    $('body').append(toast);
    
    setTimeout(function() {
        toast.alert('close');
    }, 5000);
}

/**
 * Format date string
 * @param {string} dateStr - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateStr) {
    if (!dateStr) return '-';
    var date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

/**
 * API helper function
 * @param {string} url - API endpoint
 * @param {string} method - HTTP method
 * @param {object} data - Request data
 * @returns {Promise} API response
 */
function apiCall(url, method, data) {
    return $.ajax({
        url: url,
        method: method || 'GET',
        contentType: 'application/json',
        data: data ? JSON.stringify(data) : null,
        dataType: 'json'
    });
}
