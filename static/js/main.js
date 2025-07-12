// Main JavaScript for StackIt Q&A Platform

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 70
            }, 1000);
        }
    });

    // Voting functionality
    $('.vote-btn').on('click', function(e) {
        e.preventDefault();
        
        var btn = $(this);
        var type = btn.data('type');
        var id = btn.data('id');
        var vote = btn.data('vote');
        
        // Add loading state
        btn.addClass('loading');
        
        $.ajax({
            url: `/${type}/${id}/vote/`,
            method: 'POST',
            data: {
                vote_type: vote,
                csrfmiddlewaretoken: getCookie('csrftoken')
            },
            success: function(data) {
                // Update vote count
                if (type === 'question') {
                    $('#question-vote-count').text(data.vote_count);
                } else {
                    $(`#answer-vote-count-${id}`).text(data.vote_count);
                }
                
                // Update button states
                var container = btn.closest('.voting');
                container.find('.vote-btn').removeClass('btn-primary').addClass('btn-outline-secondary');
                
                if (data.user_vote === vote) {
                    btn.removeClass('btn-outline-secondary').addClass('btn-primary');
                }
                
                // Show success message
                showToast('Vote recorded successfully!', 'success');
            },
            error: function(xhr) {
                showToast('Error recording vote. Please try again.', 'error');
            },
            complete: function() {
                btn.removeClass('loading');
            }
        });
    });

    // Accept answer functionality
    $('.accept-btn').on('click', function(e) {
        e.preventDefault();
        
        var btn = $(this);
        var answerId = btn.data('answer-id');
        
        if (confirm('Are you sure you want to accept this answer?')) {
            btn.addClass('loading');
            
            $.ajax({
                url: `/answer/${answerId}/accept/`,
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: getCookie('csrftoken')
                },
                success: function(data) {
                    if (data.success) {
                        location.reload();
                    }
                },
                error: function(xhr) {
                    showToast('Error accepting answer. Please try again.', 'error');
                },
                complete: function() {
                    btn.removeClass('loading');
                }
            });
        }
    });

    // Mark notification as read
    $('.notification-item').on('click', function() {
        var notificationId = $(this).data('notification-id');
        var item = $(this);
        
        $.ajax({
            url: `/notifications/${notificationId}/read/`,
            method: 'POST',
            data: {
                csrfmiddlewaretoken: getCookie('csrftoken')
            },
            success: function(data) {
                if (data.success) {
                    item.removeClass('unread');
                    updateNotificationCount();
                }
            }
        });
    });

    // Search functionality with debouncing
    var searchTimeout;
    $('#search-input').on('input', function() {
        clearTimeout(searchTimeout);
        var query = $(this).val();
        
        searchTimeout = setTimeout(function() {
            if (query.length >= 2) {
                performSearch(query);
            }
        }, 300);
    });

    // Tag input functionality
    $('.tag-input').on('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            var tag = $(this).val().trim();
            if (tag) {
                addTag(tag);
                $(this).val('');
            }
        }
    });

    // Remove tag
    $(document).on('click', '.tag-remove', function() {
        var tag = $(this).data('tag');
        removeTag(tag);
    });

    // Rich text editor initialization
    if (typeof Quill !== 'undefined') {
        initializeRichTextEditor();
    }

    // Auto-save draft functionality
    if ($('#question-form').length) {
        autoSaveDraft();
    }

    // Real-time notification updates
    if ($('.notification-dropdown').length) {
        updateNotificationsPeriodically();
    }
});

// Utility functions

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showToast(message, type) {
    var toastClass = type === 'success' ? 'bg-success' : 'bg-danger';
    var toast = $(`
        <div class="toast align-items-center text-white ${toastClass} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('.toast-container').append(toast);
    var bsToast = new bootstrap.Toast(toast[0]);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

function updateNotificationCount() {
    $.get('/notifications/count/', function(data) {
        var badge = $('.notification-badge');
        if (data.count > 0) {
            badge.text(data.count).show();
        } else {
            badge.hide();
        }
    });
}

function performSearch(query) {
    $.get('/search/', { q: query }, function(data) {
        $('#search-results').html(data);
    });
}

function addTag(tagName) {
    var tags = getTags();
    if (tags.indexOf(tagName) === -1 && tags.length < 5) {
        tags.push(tagName);
        renderTags(tags);
    }
}

function removeTag(tagName) {
    var tags = getTags();
    var index = tags.indexOf(tagName);
    if (index > -1) {
        tags.splice(index, 1);
        renderTags(tags);
    }
}

function getTags() {
    var tagsInput = $('#tags-input');
    return tagsInput.val() ? tagsInput.val().split(',') : [];
}

function renderTags(tags) {
    var container = $('.tags-container');
    container.empty();
    
    tags.forEach(function(tag) {
        container.append(`
            <span class="badge bg-secondary me-1 mb-1">
                ${tag}
                <span class="tag-remove" data-tag="${tag}">&times;</span>
            </span>
        `);
    });
    
    $('#tags-input').val(tags.join(','));
}

function initializeRichTextEditor() {
    var toolbarOptions = [
        ['bold', 'italic', 'underline', 'strike'],
        ['blockquote', 'code-block'],
        [{ 'header': 1 }, { 'header': 2 }],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
        [{ 'script': 'sub'}, { 'script': 'super' }],
        [{ 'indent': '-1'}, { 'indent': '+1' }],
        [{ 'direction': 'rtl' }],
        [{ 'size': ['small', false, 'large', 'huge'] }],
        [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
        [{ 'color': [] }, { 'background': [] }],
        [{ 'font': [] }],
        [{ 'align': [] }],
        ['clean'],
        ['link', 'image', 'video']
    ];

    var quill = new Quill('#editor', {
        theme: 'snow',
        modules: {
            toolbar: toolbarOptions
        },
        placeholder: 'Start writing...'
    });

    // Update hidden input on form submit
    $('form').on('submit', function() {
        $('#description-input').val(quill.root.innerHTML);
    });
}

function autoSaveDraft() {
    var form = $('#question-form');
    var title = $('#id_title');
    var description = $('#description-input');
    
    var saveDraft = function() {
        var draft = {
            title: title.val(),
            description: description.val(),
            timestamp: new Date().toISOString()
        };
        localStorage.setItem('question_draft', JSON.stringify(draft));
    };
    
    // Save draft every 30 seconds
    setInterval(saveDraft, 30000);
    
    // Save on form change
    form.on('input', saveDraft);
    
    // Load draft on page load
    var draft = localStorage.getItem('question_draft');
    if (draft) {
        draft = JSON.parse(draft);
        if (draft.title) title.val(draft.title);
        if (draft.description) {
            description.val(draft.description);
            if (typeof Quill !== 'undefined') {
                var quill = Quill.find(document.querySelector('#editor'));
                if (quill) {
                    quill.root.innerHTML = draft.description;
                }
            }
        }
    }
    
    // Clear draft on successful submit
    form.on('submit', function() {
        localStorage.removeItem('question_draft');
    });
}

function updateNotificationsPeriodically() {
    setInterval(function() {
        $.get('/notifications/check/', function(data) {
            if (data.has_new) {
                updateNotificationCount();
                showToast('You have new notifications!', 'info');
            }
        });
    }, 30000); // Check every 30 seconds
}

// Keyboard shortcuts
$(document).on('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        $('#search-input').focus();
    }
    
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        var form = $(e.target).closest('form');
        if (form.length) {
            form.submit();
        }
    }
});

// Lazy loading for images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
} 