# StackIt - A Minimal Q&A Forum Platform

StackIt is a modern, user-friendly question-and-answer platform designed for collaborative learning and structured knowledge sharing. Built with Django and featuring a clean, responsive interface, StackIt provides all the essential features needed for a thriving Q&A community.

## Features

### Core Features
- **Ask Questions**: Create detailed questions with rich text editor support
- **Answer Questions**: Provide comprehensive answers with formatting options
- **Voting System**: Upvote and downvote questions and answers
- **Accept Answers**: Question authors can mark the best answer as accepted
- **Tagging System**: Organize content with relevant tags
- **Search & Filter**: Find questions by keywords and tags
- **User Profiles**: View user activity, reputation, and contributions

### Rich Text Editor
- Bold, Italic, Strikethrough formatting
- Numbered and bullet lists
- Code blocks and blockquotes
- Image and video embedding
- Text alignment options
- Link insertion

### User Management
- User registration and authentication
- Google OAuth integration
- User profiles with avatars and bios
- Reputation system
- User badges and achievements

### Notification System
- Real-time notifications for answers and comments
- Mention system using @username
- Notification bell with unread count
- Email notifications (configurable)

### Admin Features
- Content moderation dashboard
- User management (ban/unban)
- Question approval system
- Analytics and reporting
- System monitoring

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (production-ready databases supported)
- **Frontend**: Bootstrap 5, jQuery
- **Rich Text Editor**: Quill.js
- **Authentication**: django-allauth with Google OAuth
- **Icons**: Font Awesome 6

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stackit
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Configuration

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs: `http://localhost:8000/accounts/google/login/callback/`
6. Update settings with your credentials

### Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Usage

### For Users
1. **Register/Login**: Create an account or sign in with Google
2. **Ask Questions**: Use the "Ask Question" button to post new questions
3. **Answer Questions**: Browse questions and provide helpful answers
4. **Vote**: Upvote good content and downvote inappropriate content
5. **Accept Answers**: Mark the best answer to your question
6. **Build Reputation**: Earn points through helpful contributions

### For Admins
1. **Access Admin Panel**: Use your superuser credentials
2. **Moderate Content**: Review and approve/reject questions
3. **Manage Users**: Ban/unban users who violate policies
4. **Monitor Activity**: View analytics and system information

## Project Structure

```
stackit/
├── app/                    # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View functions and classes
│   ├── forms.py           # Form definitions
│   ├── admin.py           # Admin interface configuration
│   ├── urls.py            # URL patterns
│   ├── signals.py         # Django signals
│   ├── context_processors.py  # Template context processors
│   ├── templatetags/      # Custom template tags
│   └── templates/         # HTML templates
├── project/               # Django project settings
│   ├── settings.py        # Project configuration
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── static/                # Static files (CSS, JS, images)
├── media/                 # User-uploaded files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Database Models

### Core Models
- **User**: Extended Django User model with profiles
- **Question**: Questions with title, description, and tags
- **Answer**: Answers to questions with voting
- **Comment**: Comments on answers
- **Tag**: Categories for organizing content
- **Vote**: Voting system for questions and answers
- **Notification**: User notifications system

### Relationships
- Users can ask multiple questions and provide multiple answers
- Questions can have multiple answers and tags
- Answers can have multiple comments
- Users can vote on questions and answers
- Notifications link users to relevant content

## API Endpoints

### Authentication
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout
- `POST /register/` - User registration

### Questions
- `GET /` - List all questions
- `GET /question/<id>/` - View question details
- `POST /ask/` - Create new question
- `POST /question/<id>/vote/` - Vote on question

### Answers
- `POST /question/<id>/answer/` - Post answer
- `POST /answer/<id>/vote/` - Vote on answer
- `POST /answer/<id>/accept/` - Accept answer
- `POST /answer/<id>/comment/` - Add comment

### User Management
- `GET /profile/<username>/` - View user profile
- `POST /profile/edit/` - Edit profile
- `GET /notifications/` - View notifications

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation

## Roadmap

### Planned Features
- [ ] Real-time chat functionality
- [ ] Advanced search with filters
- [ ] Question categories and subcategories
- [ ] User reputation badges
- [ ] Email notifications
- [ ] Mobile app
- [ ] API for third-party integrations
- [ ] Advanced analytics dashboard
- [ ] Content moderation tools
- [ ] Multi-language support

### Performance Improvements
- [ ] Database query optimization
- [ ] Caching implementation
- [ ] CDN integration
- [ ] Image optimization
- [ ] Lazy loading for better UX

---

**StackIt** - Empowering communities through knowledge sharing. 