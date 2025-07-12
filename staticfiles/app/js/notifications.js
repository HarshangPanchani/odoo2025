// Notification System JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const notificationModal = document.getElementById('notificationsModal');
    const notificationBadge = document.getElementById('notification-badge');
    
    // Handle notification clicks
    if (notificationModal) {
        notificationModal.addEventListener('click', function(e) {
            if (e.target.classList.contains('list-group-item')) {
                e.preventDefault();
                
                const notificationId = e.target.getAttribute('href').split('/').pop();
                const isUnread = e.target.classList.contains('fw-bold');
                
                // Make AJAX request to mark as read
                if (isUnread) {
                    fetch(`/notifications/${notificationId}/mark-read/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Update the notification item
                            e.target.classList.remove('fw-bold');
                            e.target.style.background = '';
                            e.target.style.borderLeft = '';
                            
                            // Update badge count
                            updateNotificationBadge(data.unread_count);
                            
                            // Navigate to the target URL
                            setTimeout(() => {
                                window.location.href = e.target.getAttribute('href');
                            }, 300);
                        }
                    })
                    .catch(error => {
                        console.error('Error marking notification as read:', error);
                        // Fallback to direct navigation
                        window.location.href = e.target.getAttribute('href');
                    });
                } else {
                    // Already read, just navigate
                    window.location.href = e.target.getAttribute('href');
                }
            }
        });
    }
    
    // Function to update notification badge
    function updateNotificationBadge(count) {
        if (notificationBadge) {
            if (count > 0) {
                notificationBadge.textContent = count;
                notificationBadge.style.display = 'block';
            } else {
                notificationBadge.style.display = 'none';
            }
        }
    }
    
    // Function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Auto-refresh notifications every 30 seconds
    setInterval(function() {
        if (notificationModal && !notificationModal.classList.contains('show')) {
            fetch('/notifications/count/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                updateNotificationBadge(data.unread_count);
            })
            .catch(error => {
                console.error('Error fetching notification count:', error);
            });
        }
    }, 30000);
}); 