from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
import os


class Command(BaseCommand):
    help = 'Setup default users for Love Chat application'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force create users even if they already exist'
        )
        parser.add_argument(
            '--quiet',
            action='store_true', 
            help='Run in quiet mode with minimal output'
        )
    
    def handle(self, *args, **options):
        quiet = options['quiet']
        force = options['force']
        
        if not quiet:
            self.stdout.write("🚀 Love Chat - Default Users Setup")
            self.stdout.write("=" * 50)
        
        # Check if any users exist
        user_count = User.objects.count()
        
        if user_count > 0 and not force:
            if not quiet:
                self.stdout.write(
                    self.style.WARNING(f"📊 Found {user_count} existing users. Skipping setup.")
                )
                self.stdout.write("💡 Use --force to create users anyway.")
            return
        
        created_users = []
        
        # Define default users
        default_users = [
            {
                'username': 'tinh',
                'password': 'Abc13579', 
                'email': 'tinh@lovechat.com',
                'first_name': 'Tinh',
                'last_name': 'Admin',
                'is_superuser': True,
                'is_staff': True,
                'display_name': 'Tinh (Admin)',
                'bio': 'System Administrator - Love Chat founder and developer'
            },
            {
                'username': 'tramanh',
                'password': 'Admin123',
                'email': 'tramanh@lovechat.com', 
                'first_name': 'Tra',
                'last_name': 'Manh',
                'is_superuser': False,
                'is_staff': False,
                'display_name': 'Tra Manh',
                'bio': 'Love Chat user - Testing and feedback specialist'
            },
            {
                'username': 'admin',
                'password': 'Abc13579', 
                'email': 'admin@lovechat.com',
                'first_name': 'Admin',
                'last_name': '',
                'is_superuser': True,
                'is_staff': True,
                'display_name': 'Admin (Superuser)',
                'bio': 'System Administrator - Love Chat founder and developer'
            }
        ]
        
        try:
            with transaction.atomic():
                for user_data in default_users:
                    username = user_data['username']
                    
                    # Check if user already exists
                    if User.objects.filter(username=username).exists():
                        if force:
                            # Update existing user
                            user = User.objects.get(username=username)
                            user.set_password(user_data['password'])
                            user.email = user_data['email']
                            user.first_name = user_data['first_name']
                            user.last_name = user_data['last_name']
                            user.is_superuser = user_data['is_superuser']
                            user.is_staff = user_data['is_staff']
                            user.save()
                            
                            # Update profile if exists
                            if hasattr(user, 'profile'):
                                user.profile.display_name = user_data['display_name']
                                user.profile.bio = user_data['bio']
                                user.profile.save()
                            
                            if not quiet:
                                status = "👑 SUPERUSER" if user_data['is_superuser'] else "👤 USER"
                                self.stdout.write(
                                    self.style.SUCCESS(f"🔄 Updated {status}: {username}")
                                )
                        else:
                            if not quiet:
                                self.stdout.write(
                                    self.style.WARNING(f"⚠️  User {username} already exists. Skipping.")
                                )
                        continue
                    
                    # Create new user
                    user = User.objects.create_user(
                        username=username,
                        password=user_data['password'],
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name']
                    )
                    
                    # Set admin privileges
                    if user_data['is_superuser']:
                        user.is_superuser = True
                        user.is_staff = True
                        user.save()
                    
                    # Update profile if UserProfile model exists
                    try:
                        from chat.models import UserProfile
                        profile, created = UserProfile.objects.get_or_create(user=user)
                        profile.display_name = user_data['display_name']
                        profile.bio = user_data['bio']
                        profile.save()
                    except ImportError:
                        # UserProfile model doesn't exist yet
                        pass
                    
                    created_users.append({
                        'username': username,
                        'is_superuser': user_data['is_superuser']
                    })
                    
                    if not quiet:
                        status = "👑 SUPERUSER" if user_data['is_superuser'] else "👤 USER"
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Created {status}: {username}")
                        )
                
                if not quiet:
                    self.stdout.write("=" * 50)
                    self.stdout.write(
                        self.style.SUCCESS(f"🎉 Setup complete! Created {len(created_users)} users.")
                    )
                    
                    if created_users:
                        self.stdout.write("\n📋 Login Credentials:")
                        for user_info in created_users:
                            user_type = "Admin" if user_info['is_superuser'] else "User"
                            password = "Abc13579" if user_info['is_superuser'] else "Admin123"
                            self.stdout.write(f"  {user_type}: {user_info['username']} / {password}")
                        
                        self.stdout.write("\n🌐 Access URLs:")
                        self.stdout.write("  • App: http://localhost:8000")
                        self.stdout.write("  • Admin: http://localhost:8000/admin (superuser only)")
                        
                        self.stdout.write("\n💡 Next Steps:")
                        self.stdout.write("  1. Start the server: python manage.py runserver")
                        self.stdout.write("  2. Login with the credentials above")
                        self.stdout.write("  3. Start chatting!")
                
        except Exception as e:
            if not quiet:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error creating default users: {e}")
                )
            raise e