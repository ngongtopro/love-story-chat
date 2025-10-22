import os
import sys
import subprocess
import threading
import signal
from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
from django.conf import settings


class Command(BaseCommand):
    help = 'Run Django development server and Vite dev server simultaneously'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=int,
            default=8000,
            help='Port for Django server (default: 8000)',
        )
        parser.add_argument(
            '--vite-port',
            type=int,
            default=5174,
            help='Port for Vite server (default: 5174)',
        )
        parser.add_argument(
            '--no-vite',
            action='store_true',
            help='Run only Django server without Vite',
        )

    def handle(self, *args, **options):
        self.django_port = options['port']
        self.vite_port = options['vite_port']
        self.no_vite = options['no_vite']
        self.processes = []
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            if not self.no_vite:
                self.start_vite_server()
            
            self.start_django_server()
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS('\n\nShutting down servers...')
            )
        finally:
            self.cleanup()

    def start_vite_server(self):
        """Start Vite development server"""
        frontend_path = os.path.join(
            settings.BASE_DIR, 
            'frontend'
        )
        
        if not os.path.exists(frontend_path):
            self.stdout.write(
                self.style.WARNING(
                    f'Frontend directory not found at {frontend_path}'
                )
            )
            return

        if not os.path.exists(os.path.join(frontend_path, 'package.json')):
            self.stdout.write(
                self.style.WARNING(
                    f'package.json not found in {frontend_path}'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting Vite dev server on port {self.vite_port}...'
            )
        )

        # Start Vite in a separate thread
        vite_thread = threading.Thread(
            target=self.run_vite,
            args=(frontend_path,)
        )
        vite_thread.daemon = True
        vite_thread.start()

    def run_vite(self, frontend_path):
        """Run Vite development server"""
        try:
            # Check if npm is available
            npm_cmd = 'npm.cmd' if os.name == 'nt' else 'npm'
            
            # Set environment variables for Vite
            env = os.environ.copy()
            env['PORT'] = str(self.vite_port)
            env['VITE_PORT'] = str(self.vite_port)
            
            # Run npm run dev
            process = subprocess.Popen(
                [npm_cmd, 'run', 'dev'],
                cwd=frontend_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append(process)
            
            # Stream output
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    self.stdout.write(
                        f'[Vite] {line.strip()}'
                    )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    'npm not found. Please install Node.js and npm.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error starting Vite server: {e}'
                )
            )

    def start_django_server(self):
        """Start Django development server"""
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting Django server on port {self.django_port}...'
            )
        )
        
        # Print helpful information
        self.print_server_info()
        
        # Run Django development server
        try:
            execute_from_command_line([
                'manage.py', 
                'runserver', 
                f'0.0.0.0:{self.django_port}'
            ])
        except KeyboardInterrupt:
            pass

    def print_server_info(self):
        """Print server information"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('🚀 Love Chat Development Servers')
        )
        self.stdout.write('='*60)
        
        self.stdout.write(
            f'📍 Django Backend:  http://localhost:{self.django_port}/'
        )
        self.stdout.write(
            f'📍 Django Admin:    http://localhost:{self.django_port}/admin/'
        )
        self.stdout.write(
            f'📍 API Endpoints:   http://localhost:{self.django_port}/api/'
        )
        
        if not self.no_vite:
            self.stdout.write(
                f'⚡ Vite Frontend:   http://localhost:{self.vite_port}/'
            )
            self.stdout.write(
                f'🔗 Proxy Requests:  Frontend → Backend'
            )
        
        self.stdout.write('='*60)
        self.stdout.write(
            '💡 Press Ctrl+C to stop all servers'
        )
        self.stdout.write('='*60 + '\n')

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.stdout.write(
            self.style.SUCCESS('\n\nReceived shutdown signal...')
        )
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Clean up processes"""
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error cleaning up process: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('All servers stopped.')
        )
