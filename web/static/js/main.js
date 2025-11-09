/**
 * Abhikarta LLM Platform - Main JavaScript
 * 
 * Copyright © 2025-2030, All Rights Reserved
 * Ashutosh Sinha
 * Email: ajsinha@gmail.com
 * 
 * Legal Notice:
 * This document and the associated software architecture are proprietary and confidential.
 * Unauthorized copying, distribution, modification, or use of this document or the software
 * system it describes is strictly prohibited without explicit written permission from the
 * copyright holder.
 * 
 * Patent Pending: Certain architectural patterns and implementations described in this
 * document may be subject to patent applications.
 */

(function($) {
    'use strict';
    
    // ==================== Document Ready ====================
    $(document).ready(function() {
        console.log('Abhikarta LLM Platform - Initialized');
        
        // Initialize tooltips
        initializeTooltips();
        
        // Initialize popovers
        initializePopovers();
        
        // Auto-dismiss alerts
        autoFismissAlerts();
        
        // Confirm actions
        setupConfirmActions();
        
        // Add loading animation to buttons
        setupLoadingButtons();
        
        // Add fade-in animation to elements
        addFadeInAnimations();
    });
    
    // ==================== Tooltip Initialization ====================
    function initializeTooltips() {
        var tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // ==================== Popover Initialization ====================
    function initializePopovers() {
        var popoverTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="popover"]')
        );
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // ==================== Auto-dismiss Alerts ====================
    function autoFismissAlerts() {
        $('.alert:not(.alert-permanent)').each(function() {
            var alert = $(this);
            setTimeout(function() {
                alert.fadeOut('slow', function() {
                    alert.remove();
                });
            }, 5000); // 5 seconds
        });
    }
    
    // ==================== Confirm Actions ====================
    function setupConfirmActions() {
        $('[data-confirm]').on('click', function(e) {
            var message = $(this).data('confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    }
    
    // ==================== Loading Buttons ====================
    function setupLoadingButtons() {
        $('form').on('submit', function() {
            var submitBtn = $(this).find('button[type="submit"]');
            var originalText = submitBtn.html();
            
            submitBtn.prop('disabled', true);
            submitBtn.html(
                '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>' +
                'Processing...'
            );
            
            // Restore button after 30 seconds (timeout)
            setTimeout(function() {
                submitBtn.prop('disabled', false);
                submitBtn.html(originalText);
            }, 30000);
        });
    }
    
    // ==================== Fade-in Animations ====================
    function addFadeInAnimations() {
        $('.card, .alert').each(function(index) {
            $(this).css({
                'opacity': '0',
                'transform': 'translateY(20px)'
            }).delay(index * 50).animate({
                'opacity': '1'
            }, 500, function() {
                $(this).css('transform', 'translateY(0)');
            });
        });
    }
    
    // ==================== Utility Functions ====================
    
    /**
     * Show a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type of notification (success, error, warning, info)
     */
    window.showToast = function(message, type) {
        type = type || 'info';
        var alertClass = 'alert-' + (type === 'error' ? 'danger' : type);
        
        var toast = $('<div>')
            .addClass('alert ' + alertClass + ' alert-dismissible fade show')
            .attr('role', 'alert')
            .css({
                'position': 'fixed',
                'top': '20px',
                'right': '20px',
                'z-index': '9999',
                'min-width': '300px',
                'animation': 'slideInRight 0.5s'
            })
            .html(
                '<i class="fas fa-' + getIconForType(type) + ' me-2"></i>' +
                message +
                '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>'
            );
        
        $('body').append(toast);
        
        setTimeout(function() {
            toast.fadeOut('slow', function() {
                toast.remove();
            });
        }, 5000);
    };
    
    /**
     * Get icon class for notification type
     * @param {string} type - Notification type
     * @returns {string} Font Awesome icon class
     */
    function getIconForType(type) {
        switch(type) {
            case 'success': return 'check-circle';
            case 'error': return 'exclamation-circle';
            case 'warning': return 'exclamation-triangle';
            case 'info': return 'info-circle';
            default: return 'info-circle';
        }
    }
    
    /**
     * Format date to readable string
     * @param {Date} date - Date object
     * @returns {string} Formatted date string
     */
    window.formatDate = function(date) {
        if (!(date instanceof Date)) {
            date = new Date(date);
        }
        
        var options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return date.toLocaleDateString('en-US', options);
    };
    
    /**
     * Validate email format
     * @param {string} email - Email address
     * @returns {boolean} True if valid
     */
    window.validateEmail = function(email) {
        var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    };
    
    /**
     * Show loading overlay
     */
    window.showLoading = function() {
        var overlay = $('<div>')
            .attr('id', 'loading-overlay')
            .css({
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'width': '100%',
                'height': '100%',
                'background': 'rgba(0, 0, 0, 0.5)',
                'z-index': '9999',
                'display': 'flex',
                'justify-content': 'center',
                'align-items': 'center'
            })
            .html(
                '<div class="spinner-border text-light" style="width: 3rem; height: 3rem;" role="status">' +
                '<span class="visually-hidden">Loading...</span>' +
                '</div>'
            );
        
        $('body').append(overlay);
    };
    
    /**
     * Hide loading overlay
     */
    window.hideLoading = function() {
        $('#loading-overlay').fadeOut('fast', function() {
            $(this).remove();
        });
    };
    
    /**
     * Debounce function
     * @param {function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {function} Debounced function
     */
    window.debounce = function(func, wait) {
        var timeout;
        return function executedFunction() {
            var context = this;
            var args = arguments;
            var later = function() {
                timeout = null;
                func.apply(context, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    // ==================== AJAX Setup ====================
    
    // Setup AJAX defaults
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            // Add CSRF token if needed
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                var csrfToken = $('meta[name="csrf-token"]').attr('content');
                if (csrfToken) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX Error:', status, error);
            if (xhr.status === 401) {
                window.location.href = '/login';
            } else if (xhr.status === 403) {
                showToast('Access denied', 'error');
            } else if (xhr.status === 500) {
                showToast('Server error occurred', 'error');
            }
        }
    });
    
    // ==================== Keyboard Shortcuts ====================
    
    $(document).on('keydown', function(e) {
        // Ctrl/Cmd + K for search (if implemented)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            // Trigger search modal or input focus
            console.log('Search shortcut triggered');
        }
        
        // ESC to close modals
        if (e.key === 'Escape') {
            $('.modal').modal('hide');
        }
    });
    
    // ==================== Session Timeout Warning ====================
    
    // Warn user before session expires (if session timeout is 1 hour)
    var sessionTimeout = 3600000; // 1 hour in milliseconds
    var warningTime = sessionTimeout - 300000; // Show warning 5 minutes before
    
    setTimeout(function() {
        showToast('Your session will expire in 5 minutes. Please save your work.', 'warning');
    }, warningTime);
    
    // ==================== Console Warning ====================
    
    console.log(
        '%cStop!',
        'color: red; font-size: 50px; font-weight: bold;'
    );
    console.log(
        '%cThis is a browser feature intended for developers. If someone told you to copy and paste something here, it is a scam and will give them access to your account.',
        'color: #333; font-size: 16px;'
    );
    console.log(
        '%cAbhikarta LLM Platform © 2025-2030 Ashutosh Sinha. All Rights Reserved.',
        'color: #667eea; font-size: 12px;'
    );
    
})(jQuery);
