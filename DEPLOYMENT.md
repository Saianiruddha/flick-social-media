# 🚀 INSTACLONE Deployment Guide

This guide covers deploying your INSTACLONE application to production.

## 📋 Pre-Deployment Checklist

### Security
- [ ] Set `DEBUG = False` in production environment
- [ ] Generate a new `SECRET_KEY` for production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up HTTPS (SSL certificate)
- [ ] Configure secure headers
- [ ] Review user input validation
- [ ] Set up proper error logging

### Database
- [ ] Set up production database (PostgreSQL recommended)
- [ ] Run migrations on production database
- [ ] Set up database backups
- [ ] Configure connection pooling if needed

### Static Files & Media
- [ ] Configure static file serving (WhiteNoise or CDN)
- [ ] Set up media file storage (AWS S3 or similar)
- [ ] Optimize images and assets
- [ ] Configure proper CORS settings

### Performance
- [ ] Enable database query optimization
- [ ] Set up caching (Redis/Memcached)
- [ ] Configure proper database indexes
- [ ] Optimize image processing
- [ ] Set up monitoring and logging

## 🔧 Environment Configuration

### Production Settings
Create a production-specific settings file or use environment variables:

```python
# Production settings example
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_ROOT = '/path/to/static'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (AWS S3 example)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
```

### Required Environment Variables
```bash
# Security
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=instaclone_prod
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_HOST=your_db_host
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

## 🌐 Deployment Options

### Option 1: Traditional VPS/Server
1. **Server Setup**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx postgresql
   
   # Create virtual environment
   python3 -m venv /path/to/venv
   source /path/to/venv/bin/activate
   
   # Install requirements
   pip install -r requirements.txt
   pip install gunicorn psycopg2-binary
   ```

2. **Database Setup**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE instaclone_prod;
   CREATE USER instaclone_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE instaclone_prod TO instaclone_user;
   ```

3. **Django Setup**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   python manage.py createsuperuser
   ```

4. **Gunicorn Configuration**
   ```bash
   # /etc/systemd/system/instaclone.service
   [Unit]
   Description=INSTACLONE Django app
   After=network.target
   
   [Service]
   User=your_user
   Group=www-data
   WorkingDirectory=/path/to/instaclone
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind unix:/path/to/instaclone.sock INSTACLONE.wsgi:application
   
   [Install]
   WantedBy=multi-user.target
   ```

5. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;
       
       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           root /path/to/instaclone;
       }
       
       location /media/ {
           root /path/to/instaclone;
       }
       
       location / {
           include proxy_params;
           proxy_pass http://unix:/path/to/instaclone.sock;
       }
   }
   ```

### Option 2: Cloud Platforms

#### Heroku
1. **Procfile**
   ```
   web: gunicorn INSTACLONE.wsgi
   release: python manage.py migrate
   ```

2. **Runtime**
   ```
   python-3.11.0
   ```

3. **Deployment**
   ```bash
   heroku create your-app-name
   heroku config:set DEBUG=False
   heroku config:set SECRET_KEY=your-secret-key
   heroku addons:create heroku-postgresql:mini
   git push heroku main
   ```

#### AWS Elastic Beanstalk
1. **Configure .ebextensions**
2. **Set up RDS for database**
3. **Configure S3 for static/media files**
4. **Deploy using EB CLI**

#### Docker Deployment
1. **Dockerfile**
   ```dockerfile
   FROM python:3.11
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8000
   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "INSTACLONE.wsgi:application"]
   ```

2. **docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     web:
       build: .
       ports:
         - "8000:8000"
       depends_on:
         - db
       environment:
         - DB_HOST=db
     
     db:
       image: postgres:13
       environment:
         POSTGRES_DB: instaclone
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: password
   ```

## 🔍 Monitoring & Maintenance

### Logging
- Set up centralized logging (ELK stack, Sentry)
- Monitor error rates and performance
- Set up alerts for critical issues

### Backups
- Regular database backups
- Media file backups
- Configuration backups

### Updates
- Regular security updates
- Django version updates
- Dependency updates

### Performance Monitoring
- Database query monitoring
- Response time monitoring
- Resource usage monitoring

## 🆘 Troubleshooting

### Common Issues
1. **Static files not loading**
   - Check `STATIC_ROOT` and `STATIC_URL` settings
   - Ensure `collectstatic` was run
   - Verify web server configuration

2. **Database connection errors**
   - Check database credentials
   - Verify network connectivity
   - Check database server status

3. **Media files not uploading**
   - Check file permissions
   - Verify media storage configuration
   - Check available disk space

4. **Performance issues**
   - Review database queries
   - Check server resources
   - Implement caching

### Debug Commands
```bash
# Check Django configuration
python manage.py check --deploy

# Test database connection
python manage.py dbshell

# View logs
tail -f /var/log/nginx/error.log
journalctl -u instaclone -f

# Performance profiling
python manage.py runserver --debug
```

## 📞 Support

For deployment issues:
1. Check Django deployment documentation
2. Review cloud provider specific guides
3. Consult community forums
4. Consider professional deployment services

---

**Good luck with your deployment! 🎉**