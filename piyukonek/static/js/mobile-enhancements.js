/**
 * Mobile Enhancement JavaScript for PIYUKONEK System
 * Provides touch-friendly interactions and mobile-specific functionality
 */

// Mobile Menu Management
class MobileMenuManager {
  constructor() {
    this.sidebar = null;
    this.overlay = null;
    this.toggle = null;
    this.isOpen = false;
    this.init();
  }

  init() {
    this.sidebar = document.querySelector('.sidebar');
    this.overlay = document.querySelector('.mobile-overlay');
    this.toggle = document.querySelector('.mobile-menu-toggle');
    
    if (this.sidebar && this.overlay && this.toggle) {
      this.bindEvents();
    }
  }

  bindEvents() {
    // Toggle button click
    if (this.toggle) {
      this.toggle.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleMenu();
      });
    }

    // Overlay click to close
    if (this.overlay) {
      this.overlay.addEventListener('click', (e) => {
        e.preventDefault();
        this.closeMenu();
      });
    }

    // Nav link clicks to close menu
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        this.closeMenu();
      });
    });

    // Window resize handler
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        this.closeMenu();
      }
    });

    // Touch gestures for mobile menu
    this.bindTouchGestures();
  }

  bindTouchGestures() {
    if (!this.sidebar) return;

    let startX = 0;
    let currentX = 0;
    let isDragging = false;

    this.sidebar.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      isDragging = true;
    }, { passive: true });

    this.sidebar.addEventListener('touchmove', (e) => {
      if (!isDragging) return;
      
      currentX = e.touches[0].clientX;
      const diffX = startX - currentX;
      
      // If swiping left and menu is open, close it
      if (diffX > 50 && this.isOpen) {
        this.closeMenu();
        isDragging = false;
      }
    }, { passive: true });

    this.sidebar.addEventListener('touchend', () => {
      isDragging = false;
    }, { passive: true });
  }

  toggleMenu() {
    if (this.isOpen) {
      this.closeMenu();
    } else {
      this.openMenu();
    }
  }

  openMenu() {
    if (this.sidebar && this.overlay) {
      this.sidebar.classList.add('mobile-open');
      this.overlay.classList.add('show');
      this.isOpen = true;
      
      // Prevent body scroll when menu is open
      document.body.style.overflow = 'hidden';
      
      // Add animation class
      this.sidebar.classList.add('mobile-slide-in');
    }
  }

  closeMenu() {
    if (this.sidebar && this.overlay) {
      this.sidebar.classList.remove('mobile-open');
      this.overlay.classList.remove('show');
      this.isOpen = false;
      
      // Restore body scroll
      document.body.style.overflow = '';
      
      // Remove animation class
      this.sidebar.classList.remove('mobile-slide-in');
    }
  }
}

// Touch-friendly Button Enhancements
class TouchButtonEnhancer {
  constructor() {
    this.init();
  }

  init() {
    this.enhanceButtons();
    this.enhanceCards();
    this.enhanceLinks();
  }

  enhanceButtons() {
    const buttons = document.querySelectorAll('.btn, button, .nav-link');
    
    buttons.forEach(button => {
      // Add touch feedback
      button.addEventListener('touchstart', (e) => {
        button.style.transform = 'scale(0.98)';
        button.style.transition = 'transform 0.1s ease';
      }, { passive: true });

      button.addEventListener('touchend', (e) => {
        button.style.transform = 'scale(1)';
      }, { passive: true });

      // Ensure minimum touch target size
      const rect = button.getBoundingClientRect();
      if (rect.height < 44 || rect.width < 44) {
        button.style.minHeight = '44px';
        button.style.minWidth = '44px';
        button.style.padding = '12px 16px';
      }
    });
  }

  enhanceCards() {
    const cards = document.querySelectorAll('.card, .concern-card, .stat-card, .action-card');
    
    cards.forEach(card => {
      card.addEventListener('touchstart', (e) => {
        card.style.transform = 'scale(0.98)';
        card.style.transition = 'transform 0.1s ease';
      }, { passive: true });

      card.addEventListener('touchend', (e) => {
        card.style.transform = 'scale(1)';
      }, { passive: true });
    });
  }

  enhanceLinks() {
    const links = document.querySelectorAll('a');
    
    links.forEach(link => {
      // Add touch feedback for links
      link.addEventListener('touchstart', (e) => {
        link.style.opacity = '0.7';
        link.style.transition = 'opacity 0.1s ease';
      }, { passive: true });

      link.addEventListener('touchend', (e) => {
        link.style.opacity = '1';
      }, { passive: true });
    });
  }
}

// Mobile Form Enhancements
class MobileFormEnhancer {
  constructor() {
    this.init();
  }

  init() {
    this.enhanceInputs();
    this.enhanceSelects();
    this.enhanceTextareas();
    this.addFormValidation();
  }

  enhanceInputs() {
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="number"]');
    
    inputs.forEach(input => {
      // Ensure proper font size to prevent zoom on iOS
      if (input.style.fontSize === '' || parseInt(input.style.fontSize) < 16) {
        input.style.fontSize = '16px';
      }

      // Add focus enhancement
      input.addEventListener('focus', (e) => {
        input.style.borderColor = '#4CAF50';
        input.style.boxShadow = '0 0 0 3px rgba(76, 175, 80, 0.1)';
      });

      input.addEventListener('blur', (e) => {
        input.style.borderColor = '#e5e7eb';
        input.style.boxShadow = 'none';
      });

      // Add touch-friendly padding
      input.style.minHeight = '44px';
      input.style.padding = '12px 16px';
    });
  }

  enhanceSelects() {
    const selects = document.querySelectorAll('select');
    
    selects.forEach(select => {
      select.style.minHeight = '44px';
      select.style.padding = '12px 16px';
      select.style.fontSize = '16px';
    });
  }

  enhanceTextareas() {
    const textareas = document.querySelectorAll('textarea');
    
    textareas.forEach(textarea => {
      textarea.style.minHeight = '120px';
      textarea.style.padding = '12px 16px';
      textarea.style.fontSize = '16px';
      textarea.style.fontFamily = 'inherit';
    });
  }

  addFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
      form.addEventListener('submit', (e) => {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
          if (!field.value.trim()) {
            isValid = false;
            field.style.borderColor = '#ef4444';
            field.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
            
            // Show error message
            this.showFieldError(field, 'This field is required');
          } else {
            field.style.borderColor = '#e5e7eb';
            field.style.boxShadow = 'none';
            this.hideFieldError(field);
          }
        });
        
        if (!isValid) {
          e.preventDefault();
        }
      });
    });
  }

  showFieldError(field, message) {
    let errorElement = field.parentNode.querySelector('.field-error');
    if (!errorElement) {
      errorElement = document.createElement('div');
      errorElement.className = 'field-error';
      errorElement.style.color = '#ef4444';
      errorElement.style.fontSize = '14px';
      errorElement.style.marginTop = '4px';
      field.parentNode.appendChild(errorElement);
    }
    errorElement.textContent = message;
  }

  hideFieldError(field) {
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
      errorElement.remove();
    }
  }
}

// Mobile Scroll Enhancements
class MobileScrollEnhancer {
  constructor() {
    this.init();
  }

  init() {
    this.enhanceScrollBehavior();
    this.addScrollToTop();
    this.optimizeScrollPerformance();
  }

  enhanceScrollBehavior() {
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        const targetId = link.getAttribute('href').substring(1);
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
  }

  addScrollToTop() {
    // Create scroll to top button
    const scrollToTopBtn = document.createElement('button');
    scrollToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollToTopBtn.className = 'scroll-to-top';
    scrollToTopBtn.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 50px;
      height: 50px;
      background: #4CAF50;
      color: white;
      border: none;
      border-radius: 50%;
      cursor: pointer;
      display: none;
      z-index: 1000;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      transition: all 0.3s ease;
    `;
    
    document.body.appendChild(scrollToTopBtn);
    
    // Show/hide scroll to top button
    window.addEventListener('scroll', () => {
      if (window.pageYOffset > 300) {
        scrollToTopBtn.style.display = 'block';
      } else {
        scrollToTopBtn.style.display = 'none';
      }
    });
    
    // Scroll to top functionality
    scrollToTopBtn.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  optimizeScrollPerformance() {
    // Throttle scroll events for better performance
    let ticking = false;
    
    const updateScrollElements = () => {
      // Add any scroll-based animations or updates here
      ticking = false;
    };
    
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(updateScrollElements);
        ticking = true;
      }
    }, { passive: true });
  }
}

// Mobile Notification System
class MobileNotificationManager {
  constructor() {
    this.notifications = [];
    this.init();
  }

  init() {
    this.createNotificationContainer();
  }

  createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'mobile-notifications';
    container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 2000;
      max-width: 350px;
    `;
    document.body.appendChild(container);
  }

  show(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `mobile-notification mobile-notification-${type}`;
    notification.style.cssText = `
      background: white;
      border-left: 4px solid ${this.getTypeColor(type)};
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 10px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      transform: translateX(100%);
      transition: transform 0.3s ease;
      max-width: 100%;
      word-wrap: break-word;
    `;
    
    notification.innerHTML = `
      <div style="display: flex; align-items: flex-start; gap: 12px;">
        <i class="fas ${this.getTypeIcon(type)}" style="color: ${this.getTypeColor(type)}; margin-top: 2px;"></i>
        <div style="flex: 1;">
          <p style="margin: 0; font-size: 14px; line-height: 1.4;">${message}</p>
        </div>
        <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: #6b7280; cursor: pointer; padding: 0; margin-left: 8px;">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;
    
    const container = document.getElementById('mobile-notifications');
    container.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    if (duration > 0) {
      setTimeout(() => {
        this.remove(notification);
      }, duration);
    }
    
    return notification;
  }

  remove(notification) {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }

  getTypeColor(type) {
    const colors = {
      success: '#22c55e',
      error: '#ef4444',
      warning: '#f59e0b',
      info: '#3b82f6'
    };
    return colors[type] || colors.info;
  }

  getTypeIcon(type) {
    const icons = {
      success: 'fa-check-circle',
      error: 'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
  }
}

// Initialize all mobile enhancements when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize mobile enhancements
  new MobileMenuManager();
  new TouchButtonEnhancer();
  new MobileFormEnhancer();
  new MobileScrollEnhancer();
  new MobileNotificationManager();
  
  // Add mobile-specific event listeners
  addMobileEventListeners();
});

// Additional mobile event listeners
function addMobileEventListeners() {
  // Prevent zoom on double tap
  let lastTouchEnd = 0;
  document.addEventListener('touchend', function (event) {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
      event.preventDefault();
    }
    lastTouchEnd = now;
  }, false);
  
  // Handle orientation change
  window.addEventListener('orientationchange', function() {
    setTimeout(() => {
      // Refresh layout after orientation change
      window.dispatchEvent(new Event('resize'));
    }, 100);
  });
  
  // Handle viewport changes
  const viewport = document.querySelector('meta[name="viewport"]');
  if (viewport) {
    // Ensure proper viewport settings for mobile
    viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
  }
}

// Export for global access
window.MobileNotificationManager = MobileNotificationManager;
