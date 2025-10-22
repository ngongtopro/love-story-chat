import os
import sys
import subprocess
import threading
import signal
import time
from django.core.management.commands.runserver import Command as RunserverCommand
from django.conf import settings


class Command(RunserverCommand):
    help = 'Run Django server with Vite dev server automatically'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--no-vite',
            action='store_true',
            help='Run only Django server without Vite',
        )
        parser.add_argument(
            '--vite-port',
            type=int,
            default=5174,
            help='Port for Vite server (default: 5174)',
        )

    def handle(self, *args, **options):
        self.no_vite = options.get('no_vite', False)
        self.vite_port = options.get('vite_port', 5174)
        self.vite_process = None

        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            if not self.no_vite:
                self.start_vite_server()
                time.sleep(2)  # Give Vite time to start
            
            self.print_startup_info()
            
            # Call parent's handle method to start Django server
            super().handle(*args, **options)
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS('\n\nShutting down servers...')
            )
        finally:
            self.cleanup()

    def start_vite_server(self):
        """Start Vite development server in background"""
        # Find frontend directory
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

        try:
            # Determine npm command based on OS
            npm_cmd = 'npm.cmd' if os.name == 'nt' else 'npm'
            
            # Set environment variables
            env = os.environ.copy()
            env['FORCE_COLOR'] = '1'  # Enable colors in Vite output
            
            # Start Vite process
            self.vite_process = subprocess.Popen(
                [npm_cmd, 'run', 'dev', '--port', str(self.vite_port)],
                cwd=frontend_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )

            # Start thread to monitor Vite output
            vite_thread = threading.Thread(
                target=self.monitor_vite_output,
                daemon=True
            )
            vite_thread.start()

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Vite server starting on port {self.vite_port}...'
                )
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    '❌ npm not found. Please install Node.js and npm.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Error starting Vite: {e}'
                )
            )

    def monitor_vite_output(self):
        """Monitor Vite process output"""
        if not self.vite_process:
            return
            
        try:
            while True:
                line = self.vite_process.stdout.readline()
                if not line:
                    break
                    
                line = line.strip()
                if line:
                    # Filter and format Vite messages
                    if 'Local:' in line or 'ready in' in line:
                        self.stdout.write(f'[Vite] {line}')
                    elif 'hmr update' in line or 'page reload' in line:
                        # Suppress too many HMR messages
                        pass
                    elif any(keyword in line.lower() for keyword in ['error', 'warn', 'fail']):
                        self.stdout.write(
                            self.style.ERROR(f'[Vite] {line}')
                        )
                        
        except Exception:
            pass

    def print_startup_info(self):
        """Print startup information"""
        self.stdout.write('\n' + '='*70)
        self.stdout.write(
            self.style.SUCCESS('🚀 Love Chat Development Environment')
        )
        self.stdout.write('='*70)
        
        # Get Django server info
        django_port = self.default_port
        if hasattr(self, 'addr') and ':' in self.addr:
            django_port = self.addr.split(':')[1]
        elif hasattr(self, 'port'):
            django_port = self.port
        
        self.stdout.write(
            f'🌐 Django Backend:   http://localhost:{django_port}/'
        )
        self.stdout.write(
            f'⚙️  Django Admin:    http://localhost:{django_port}/admin/'
        )
        self.stdout.write(
            f'📡 API Root:         http://localhost:{django_port}/api/'
        )
        
        if not self.no_vite:
            self.stdout.write(
                f'⚡ Vite Frontend:    http://localhost:{self.vite_port}/'
            )
            self.stdout.write(
                f'🔗 Auto Proxy:      Frontend ⟷ Backend'
            )
        
        self.stdout.write('='*70)
        self.stdout.write('💡 Features:')
        self.stdout.write('   • Hot Module Replacement (HMR)')
        self.stdout.write('   • Auto browser refresh')
        self.stdout.write('   • API proxy configuration')
        self.stdout.write('   • TypeScript compilation')
        self.stdout.write('='*70)
        self.stdout.write(
            '🛑 Press Ctrl+C to stop all servers'
        )
        self.stdout.write('='*70 + '\n')

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Clean up Vite process"""
        if self.vite_process and self.vite_process.poll() is None:
            try:
                if os.name == 'nt':
                    # Windows: Send Ctrl+C signal
                    self.vite_process.send_signal(signal.CTRL_C_EVENT)
                else:
                    # Unix: Send SIGTERM
                    self.vite_process.terminate()
                
                # Wait for process to terminate
                self.vite_process.wait(timeout=5)
                
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't respond
                self.vite_process.kill()
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Warning during cleanup: {e}')
                )
            
            finally:
                self.stdout.write(
                    self.style.SUCCESS('✅ All servers stopped.')
                )
