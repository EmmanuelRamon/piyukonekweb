// Session Management JavaScript
(function() {
    'use strict';
    
    // Session timeout settings (30 minutes)
    const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes in milliseconds
    const WARNING_TIME = 5 * 60 * 1000; // 5 minutes warning before timeout
    
    let sessionTimer;
    let warningTimer;
    let isTabActive = true;
    
    // Initialize session management
    function initSessionManager() {
        // Set up activity tracking
        document.addEventListener('click', resetSessionTimer);
        document.addEventListener('keypress', resetSessionTimer);
        document.addEventListener('scroll', resetSessionTimer);
        document.addEventListener('mousemove', resetSessionTimer);
        
        // Handle tab visibility changes
        document.addEventListener('visibilitychange', handleVisibilityChange);
        
        // Handle page unload (tab close)
        window.addEventListener('beforeunload', handleTabClose);
        
        // Handle page focus/blur
        window.addEventListener('focus', handlePageFocus);
        window.addEventListener('blur', handlePageBlur);
        
        // Start session timer
        startSessionTimer();
        
        // Check session status every minute
        setInterval(checkSessionStatus, 60000);
    }
    
    // Reset session timer on user activity
    function resetSessionTimer() {
        if (sessionTimer) {
            clearTimeout(sessionTimer);
        }
        if (warningTimer) {
            clearTimeout(warningTimer);
        }
        
        startSessionTimer();
        
        // Update session activity on server
        updateSessionActivity();
    }
    
    // Start session timer
    function startSessionTimer() {
        // Set warning timer (5 minutes before timeout)
        warningTimer = setTimeout(showSessionWarning, SESSION_TIMEOUT - WARNING_TIME);
        
        // Set session timeout
        sessionTimer = setTimeout(handleSessionTimeout, SESSION_TIMEOUT);
    }
    
    // Handle tab visibility changes
    function handleVisibilityChange() {
        if (document.hidden) {
            isTabActive = false;
        } else {
            isTabActive = true;
            resetSessionTimer();
        }
    }
    
    // Handle page focus
    function handlePageFocus() {
        isTabActive = true;
        resetSessionTimer();
    }
    
    // Handle page blur
    function handlePageBlur() {
        isTabActive = false;
    }
    
    // Handle tab close
    function handleTabClose(event) {
        // Send logout request to server
        fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({action: 'tab_close'})
        }).catch(error => {
            console.log('Logout request failed:', error);
        });
    }
    
    // Show session warning
    function showSessionWarning() {
        if (!isTabActive) return;
        
        const warningDiv = document.createElement('div');
        warningDiv.id = 'session-warning';
        warningDiv.innerHTML = `
            <div class="session-warning-content">
                <h4>⚠️ Session Timeout Warning</h4>
                <p>Your session will expire in 5 minutes due to inactivity.</p>
                <p>Click anywhere to extend your session.</p>
                <button onclick="extendSession()" class="btn btn-primary">Extend Session</button>
                <button onclick="logoutNow()" class="btn btn-secondary">Logout Now</button>
            </div>
        `;
        
        warningDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        document.body.appendChild(warningDiv);
        
        // Auto-hide after 30 seconds if no action
        setTimeout(() => {
            if (document.getElementById('session-warning')) {
                document.getElementById('session-warning').remove();
            }
        }, 30000);
    }
    
    // Handle session timeout
    function handleSessionTimeout() {
        if (!isTabActive) return;
        
        // Remove warning if it exists
        const warningDiv = document.getElementById('session-warning');
        if (warningDiv) {
            warningDiv.remove();
        }
        
        // Show timeout message
        const timeoutDiv = document.createElement('div');
        timeoutDiv.id = 'session-timeout';
        timeoutDiv.innerHTML = `
            <div class="session-timeout-content">
                <h4>⏰ Session Expired</h4>
                <p>Your session has expired due to inactivity.</p>
                <p>You will be redirected to the login page.</p>
            </div>
        `;
        
        timeoutDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        `;
        
        document.body.appendChild(timeoutDiv);
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
            window.location.href = '/login';
        }, 3000);
    }
    
    // Extend session
    function extendSession() {
        const warningDiv = document.getElementById('session-warning');
        if (warningDiv) {
            warningDiv.remove();
        }
        
        resetSessionTimer();
        
        // Show success message
        showMessage('Session extended successfully!', 'success');
    }
    
    // Logout now
    function logoutNow() {
        window.location.href = '/logout';
    }
    
    // Update session activity on server
    function updateSessionActivity() {
        fetch('/update_session_activity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({action: 'update_activity'})
        }).catch(error => {
            console.log('Session activity update failed:', error);
        });
    }
    
    // Check session status
    function checkSessionStatus() {
        fetch('/check_session_status', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'expired') {
                handleSessionTimeout();
            }
        })
        .catch(error => {
            console.log('Session status check failed:', error);
        });
    }
    
    // Show message utility
    function showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type}`;
        messageDiv.textContent = message;
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10001;
            padding: 15px;
            border-radius: 5px;
            color: white;
            background: ${type === 'success' ? '#28a745' : '#007bff'};
        `;
        
        document.body.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
    
    // Make functions globally available
    window.extendSession = extendSession;
    window.logoutNow = logoutNow;
    
    // Initialize when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSessionManager);
    } else {
        initSessionManager();
    }
    
})(); 