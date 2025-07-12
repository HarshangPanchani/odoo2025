// Follow/Unfollow functionality
document.addEventListener('DOMContentLoaded', function() {
    const followButtons = document.querySelectorAll('.follow-btn');
    
    followButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('href');
            const button = this;
            const originalText = button.innerHTML;
            
            // Show loading state
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            button.disabled = true;
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update button text and class
                    if (data.action === 'followed') {
                        button.innerHTML = '<i class="fas fa-user-minus"></i> Unfollow';
                        button.classList.remove('btn-primary');
                        button.classList.add('btn-outline-light');
                    } else {
                        button.innerHTML = '<i class="fas fa-user-plus"></i> Follow';
                        button.classList.remove('btn-outline-light');
                        button.classList.add('btn-primary');
                    }
                    
                    // Update follower count if available
                    const followerCountElement = document.querySelector('.follower-count');
                    if (followerCountElement && data.follower_count !== undefined) {
                        followerCountElement.textContent = data.follower_count;
                    }
                    
                    // Show success message
                    showToast(data.message, 'success');
                } else {
                    showToast(data.error || 'An error occurred', 'error');
                    button.innerHTML = originalText;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred', 'error');
                button.innerHTML = originalText;
            })
            .finally(() => {
                button.disabled = false;
            });
        });
    });
    
    // Highlight @username mentions
    highlightMentions();
});

// Function to highlight @username mentions
function highlightMentions() {
    const contentElements = document.querySelectorAll('.question-content, .answer-content, .bio-content');
    
    contentElements.forEach(element => {
        const text = element.innerHTML;
        const highlightedText = text.replace(/@(\w+)/g, '<a href="/profile/$1/" class="mention-link">@$1</a>');
        element.innerHTML = highlightedText;
    });
}

// Toast notification function
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        padding: 12px 20px;
        border-radius: 4px;
        color: white;
        font-weight: 500;
        max-width: 300px;
        word-wrap: break-word;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    // Set background color based on type
    switch(type) {
        case 'success':
            toast.style.backgroundColor = '#28a745';
            break;
        case 'error':
            toast.style.backgroundColor = '#dc3545';
            break;
        case 'warning':
            toast.style.backgroundColor = '#ffc107';
            toast.style.color = '#212529';
            break;
        default:
            toast.style.backgroundColor = '#17a2b8';
    }
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Add CSS for mention links
const style = document.createElement('style');
style.textContent = `
    .mention-link {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 2px 4px;
        border-radius: 3px;
        text-decoration: none;
        font-weight: 500;
    }
    
    .mention-link:hover {
        background-color: #bbdefb;
        color: #1565c0;
        text-decoration: none;
    }
`;
document.head.appendChild(style); 

// Initialize CKEditor for reply forms
function initializeCKEditorForReply(formId) {
    const textarea = document.querySelector(`#reply-form-${formId} textarea.ckeditor-reply`);
    if (textarea && !textarea.hasAttribute('data-ckeditor-initialized')) {
        // Mark as initialized to prevent double initialization
        textarea.setAttribute('data-ckeditor-initialized', 'true');
        
        // Initialize CKEditor
        if (typeof CKEDITOR !== 'undefined') {
            CKEDITOR.replace(textarea, {
                height: 150,
                width: '100%',
                toolbar: [
                    ['Bold', 'Italic', 'Underline', 'Strike'],
                    ['NumberedList', 'BulletedList'],
                    ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
                    ['Link', 'Unlink'],
                    ['Image'],
                    ['Emoji'],
                    ['Format', 'Font', 'FontSize'],
                    ['TextColor', 'BGColor'],
                    ['Smiley', 'SpecialChar']
                ],
                removePlugins: 'stylesheetparser',
                allowedContent: true,
                extraPlugins: 'emoji'
            });
        }
    }
}

// Handle reply button clicks
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('reply-btn')) {
        const answerId = e.target.getAttribute('data-answer-id');
        const replyForm = document.getElementById(`reply-form-${answerId}`);
        
        if (replyForm) {
            replyForm.style.display = 'block';
            // Initialize CKEditor for the reply form
            initializeCKEditorForReply(answerId);
        }
    }
    
    if (e.target.classList.contains('cancel-reply')) {
        const answerId = e.target.getAttribute('data-answer-id');
        const replyForm = document.getElementById(`reply-form-${answerId}`);
        
        if (replyForm) {
            replyForm.style.display = 'none';
            // Destroy CKEditor instance if it exists
            const textarea = replyForm.querySelector('textarea.ckeditor-reply');
            if (textarea && textarea.hasAttribute('data-ckeditor-initialized')) {
                const editorId = textarea.getAttribute('id');
                if (typeof CKEDITOR !== 'undefined' && CKEDITOR.instances[editorId]) {
                    CKEDITOR.instances[editorId].destroy();
                }
                textarea.removeAttribute('data-ckeditor-initialized');
            }
        }
    }
});

// Handle view replies button clicks
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('view-replies-btn')) {
        const answerId = e.target.getAttribute('data-answer-id');
        const repliesContainer = document.getElementById(`replies-${answerId}`);
        const button = e.target;
        
        if (repliesContainer) {
            if (repliesContainer.style.display === 'none' || repliesContainer.style.display === '') {
                repliesContainer.style.display = 'block';
                button.innerHTML = '<i class="fas fa-comments me-1"></i>Hide replies';
            } else {
                repliesContainer.style.display = 'none';
                const replyCount = button.getAttribute('data-reply-count');
                if (replyCount > 0) {
                    button.innerHTML = `<i class="fas fa-comments me-1"></i>View ${replyCount} repl${replyCount == 1 ? 'y' : 'ies'}`;
                } else {
                    button.innerHTML = '<i class="fas fa-comments me-1"></i>View replies';
                }
            }
        }
    }
}); 