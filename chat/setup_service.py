import os
import logging
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


class AppSetupService:
    """Service to handle automatic app setup on startup"""
    
    @staticmethod
    def check_and_setup():
        """Check if app needs setup and run it automatically"""
        
        # Skip setup in certain conditions
        if AppSetupService._should_skip_setup():
            return
        
        try:
            logger.info("🔧 Love Chat: Checking application setup...")
            
            # Test database connection first
            if not AppSetupService._test_db_connection():
                logger.warning("❌ Database connection failed. Skipping auto-setup.")
                return
            
            # Check if setup is needed
            if AppSetupService._needs_setup():
                logger.info("🚀 Running automatic application setup...")
                
                try:
                    call_command('setup_app', quiet=True)
                    logger.info("✅ Application setup completed successfully!")
                except Exception as e:
                    logger.error(f"❌ Auto-setup failed: {e}")
            else:
                logger.info("✅ Application already configured.")
                
        except Exception as e:
            logger.error(f"❌ Setup check failed: {e}")
    
    @staticmethod
    def _should_skip_setup():
        """Check if setup should be skipped"""
        # Skip during migrations
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return True
        
        # Skip if explicitly disabled
        if os.environ.get('SKIP_AUTO_SETUP', '').lower() in ['true', '1', 'yes']:
            return True
            
        # Skip in production by default (unless forced)
        if not os.environ.get('DEBUG', 'False').lower() in ['true', '1'] and \
           not os.environ.get('FORCE_AUTO_SETUP', '').lower() in ['true', '1']:
            return True
            
        return False
    
    @staticmethod
    def _test_db_connection():
        """Test if database connection is working"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except (OperationalError, Exception):
            return False
    
    @staticmethod
    def _needs_setup():
        """Check if application needs setup"""
        try:
            # Check if any users exist
            user_count = User.objects.count()
            
            # If no users, definitely need setup
            if user_count == 0:
                return True
            
            # Check if default users exist
            default_users_exist = User.objects.filter(
                username__in=['tinh', 'tramanh']
            ).count() >= 1
            
            if not default_users_exist:
                return True
                
            return False
            
        except (OperationalError, Exception) as e:
            logger.warning(f"Could not check setup status: {e}")
            return False


def auto_setup_on_ready():
    """Function to be called when Django app is ready"""
    try:
        AppSetupService.check_and_setup()
    except Exception as e:
        logger.error(f"Auto-setup failed: {e}")