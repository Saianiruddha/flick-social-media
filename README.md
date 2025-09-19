# ⚡ FLICK - Modern Social Media Platform

A dynamic and engaging social media platform built with Django, featuring quick post sharing, instant user interactions, and a modern, energetic user experience that's all about capturing and sharing life's moments in a *flick*.

## ⚡ What Makes FLICK Special

### 🎨 Modern Design Philosophy
- **Energetic Color Palette**: Vibrant coral red (#FF6B6B) and fresh teal (#4ECDC4) gradients
- **Quick Interactions**: Smooth, bouncy animations that respond instantly to user actions
- **Dynamic Branding**: Custom FLICK logo with subtle glow animations
- **Responsive Gradients**: Beautiful gradient overlays and interactive elements

### 🚀 Enhanced User Experience
- **Heart Explosion Effects**: Animated emoji explosions when liking posts
- **Magnetic Card Hover**: 3D tilt effects on post cards for engaging interactions
- **Smart Navbar**: Auto-hiding navigation with blur effects based on scroll
- **Shimmer Effects**: Subtle light animations on hover for premium feel
- **Touch Gestures**: Mobile-optimized flick gestures with visual feedback

### 🌈 Interactive Animations
- **Scroll Reveal**: Staggered animations as content comes into view
- **Click Ripples**: Material Design-inspired ripple effects on all interactions
- **Form Focus**: Enhanced form field interactions with scaling effects
- **Loading States**: Beautiful spinner animations for async operations

## ✨ Core Features

### 🔐 User Authentication & Profiles
- User registration and login with enhanced validation
- Customizable user profiles with bio, profile picture, and additional fields
- Private account functionality
- Email notifications settings

### 📱 Post Management
- Create posts with images and captions
- Image upload with automatic resizing and validation
- Like/unlike posts with AJAX support
- Soft delete functionality for posts
- Image optimization (max 5MB, auto-resize)

### 💬 Social Interactions
- Comment system on posts
- Follow/unfollow users
- Real-time like counts and interactions
- User search functionality

### 🎨 Enhanced UI/UX
- Responsive Bootstrap design
- Dark/Light mode toggle
- Pagination for posts and profiles
- Real-time feedback with messages
- Mobile-optimized interface

### ⚡ Performance & Security
- Database query optimization with select_related/prefetch_related
- Image compression and resizing
- Environment-based configuration
- CSRF protection and security headers
- File upload validation and limits

### 🛠 Admin Panel
- Enhanced admin interface with thumbnails
- Bulk actions and filtering
- User statistics and content moderation
- Optimized admin queries

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- pip
- Virtual environment (recommended)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd FLICK
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
# Django Security Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Database Setup
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Collect Static Files (if needed)
```bash
python manage.py collectstatic
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to see the application.

## 📁 Project Structure
```
FLICK/
├── FLICK/               # Main project settings
│   ├── settings.py      # Enhanced with environment variables
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py
├── posts/               # Posts app
│   ├── models.py        # Post, Comment, Follow models
│   ├── views.py         # Enhanced views with pagination
│   ├── forms.py         # Enhanced forms with validation
│   ├── admin.py         # Enhanced admin configuration
│   └── urls.py
├── users/               # Users app
│   ├── models.py        # UserProfile model
│   ├── views.py         # User authentication views
│   ├── forms.py         # Enhanced user forms
│   ├── admin.py         # Enhanced user admin
│   └── urls.py
├── templates/           # Global templates
│   ├── base.html        # Base template with dark mode
│   └── home.html        # Landing page
├── static/              # Static files
│   ├── css/            # Stylesheets
│   └── images/         # Default images
├── media/              # User uploads
├── .env                # Environment variables
└── requirements.txt    # Dependencies
```

## 🔧 Configuration

### Database Options
- **SQLite** (default): No additional setup required
- **MySQL**: Uncomment mysqlclient in requirements.txt and update .env
- **PostgreSQL**: Add psycopg2-binary to requirements.txt

### Email Backend
- **Console** (default): Emails printed to console
- **SMTP**: Configure EMAIL_* settings in .env
- **Third-party**: AWS SES, SendGrid (see requirements.txt)

## 🎯 Usage

### For Users
1. **Sign Up**: Create an account with username and email
2. **Profile Setup**: Add bio, profile picture, and personal info
3. **Create Posts**: Share images with captions
4. **Interact**: Like posts, add comments, follow users
5. **Search**: Find users and posts using the search feature

### For Administrators
1. Access admin panel at `/admin/`
2. Manage users, posts, and comments
3. View statistics and moderate content
4. Bulk actions for content management

## 🧪 Testing

### Run Tests (when implemented)
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test posts
python manage.py test users

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deployment

### Production Settings
1. Set `DEBUG=False` in .env
2. Update `ALLOWED_HOSTS` with your domain
3. Configure production database
4. Set up email backend
5. Use a web server (Nginx + Gunicorn)

### Security Checklist
- [x] Environment variables for secrets
- [x] CSRF protection enabled
- [x] Secure headers configured
- [x] File upload validation
- [x] User input sanitization
- [x] Authentication required for actions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📝 License

This project is for educational purposes. Feel free to use and modify as needed.

## 🐛 Known Issues & Improvements

### Current Limitations
- Email verification not fully implemented
- Real-time notifications need WebSocket support
- Advanced search filters needed
- Story/highlights feature not implemented

### Future Enhancements
- [ ] Real-time notifications
- [ ] Story functionality
- [ ] Advanced search and filters
- [ ] Message/chat system
- [ ] Video post support
- [ ] Mobile app API
- [ ] Content reporting system
- [ ] Advanced analytics

## 📞 Support

For issues and questions:
1. Check the documentation
2. Look at existing issues
3. Create a new issue with details
4. Contact the development team

---

---

🎆 **Built with passion for modern web experiences**

**FLICK** - *Where every moment is worth sharing in a flick!* ⚡

**Happy Coding! 🎉**
#   f l i c k - s o c i a l - m e d i a  
 