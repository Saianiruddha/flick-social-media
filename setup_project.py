#!/usr/bin/env python
"""
Setup script for INSTACLONE project
Run this after making all the changes to set up the project properly
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_project():
    """Setup the Django project with all necessary configurations"""
    
    print("🚀 Setting up INSTACLONE Django project...")
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'INSTACLONE.settings')
    django.setup()
    
    try:
        print("📦 Installing required packages...")
        os.system('pip install -r requirements.txt')
        
        print("🔧 Creating migrations for posts app...")
        execute_from_command_line(['manage.py', 'makemigrations', 'posts'])
        
        print("🔧 Creating migrations for users app...")
        execute_from_command_line(['manage.py', 'makemigrations', 'users'])
        
        print("🔧 Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("📁 Creating media directories...")
        os.makedirs('media/posts', exist_ok=True)
        os.makedirs('media/profiles', exist_ok=True)
        
        print("📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        print("✅ Project setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Create a superuser: python manage.py createsuperuser")
        print("2. Run the development server: python manage.py runserver")
        print("3. Visit http://127.0.0.1:8000/ to see your application")
        print("\n🧪 To run tests:")
        print("python manage.py test")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False
    
    return True

if __name__ == '__main__':
    setup_project()