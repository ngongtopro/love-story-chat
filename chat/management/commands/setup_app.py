from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection
import os
import sys


class Command(BaseCommand):
    help = 'Complete setup for Love Chat application (migrations, default users, etc.)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip running migrations'
        )
        parser.add_argument(
            '--skip-users',
            action='store_true', 
            help='Skip creating default users'
        )
        parser.add_argument(
            '--force-users',
            action='store_true',
            help='Force create/update default users'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Run in quiet mode'
        )
    
    def handle(self, *args, **options):
        quiet = options['quiet']
        skip_migrations = options['skip_migrations']
        skip_users = options['skip_users']
        force_users = options['force_users']
        
        if not quiet:
            self.stdout.write("🚀 Love Chat - Complete Application Setup")
            self.stdout.write("=" * 60)
        
        # Step 1: Test database connection
        if not quiet:
            self.stdout.write("\n📊 Step 1: Testing database connection...")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                if not quiet:
                    db_config = connection.settings_dict
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Database connected: {db_config['ENGINE']}")
                    )
                    if 'postgresql' in db_config['ENGINE']:
                        self.stdout.write(f"   Host: {db_config['HOST']}:{db_config['PORT']}")
                        self.stdout.write(f"   Database: {db_config['NAME']}")
                        self.stdout.write(f"   User: {db_config['USER']}")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Database connection failed: {e}")
            )
            sys.exit(1)
        
        # Step 2: Run migrations
        if not skip_migrations:
            if not quiet:
                self.stdout.write("\n🗄 Step 2: Running database migrations...")
            
            try:
                call_command('makemigrations', verbosity=0 if quiet else 1)
                call_command('migrate', verbosity=0 if quiet else 1)
                if not quiet:
                    self.stdout.write(self.style.SUCCESS("✅ Migrations completed"))
            except Exception as e:
                if not quiet:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Migration failed: {e}")
                    )
                # Don't exit, continue with setup
        else:
            if not quiet:
                self.stdout.write("⏭️  Skipping migrations")
        
        # Step 3: Setup default users
        if not skip_users:
            if not quiet:
                self.stdout.write("\n👥 Step 3: Setting up default users...")
            
            try:
                call_command(
                    'setup_default_users',
                    force=force_users,
                    quiet=quiet
                )
            except Exception as e:
                if not quiet:
                    self.stdout.write(
                        self.style.ERROR(f"❌ User setup failed: {e}")
                    )
        else:
            if not quiet:
                self.stdout.write("⏭️  Skipping user setup")
        
        # Step 4: Collect static files
        if not quiet:
            self.stdout.write("\n📦 Step 4: Collecting static files...")
        
        try:
            call_command('collectstatic', '--noinput', verbosity=0 if quiet else 1)
            if not quiet:
                self.stdout.write(self.style.SUCCESS("✅ Static files collected"))
        except Exception as e:
            if not quiet:
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Static files collection failed: {e}")
                )
        
        # Step 5: Final summary
        if not quiet:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("🎉 Love Chat Setup Complete!")
            self.stdout.write("=" * 60)
            
            # Display database info
            try:
                user_count = User.objects.count()
                self.stdout.write(f"📊 Database Statistics:")
                self.stdout.write(f"   • Users: {user_count}")
                
                # Try to get other model counts if they exist
                try:
                    from chat.models import PrivateChat, PrivateMessage
                    from caro_game.models import CaroGame
                    chat_count = PrivateChat.objects.count()
                    message_count = PrivateMessage.objects.count() 
                    game_count = CaroGame.objects.count()
                    self.stdout.write(f"   • Chats: {chat_count}")
                    self.stdout.write(f"   • Messages: {message_count}")
                    self.stdout.write(f"   • Games: {game_count}")
                except ImportError:
                    # Models not available yet
                    pass
                    
            except Exception as e:
                self.stdout.write(f"⚠️  Could not get database statistics: {e}")
            
            self.stdout.write("\n🌐 Ready to start!")
            self.stdout.write("   • Run: python manage.py runserver")
            self.stdout.write("   • Access: http://localhost:8000")
            self.stdout.write("   • Admin: http://localhost:8000/admin")
            
            if not skip_users:
                self.stdout.write("\n🔑 Default Login Credentials:")
                self.stdout.write("   • Admin: tinh / Abc13579")
                self.stdout.write("   • User: tramanh / Admin123")
        
        return "Setup completed successfully!"