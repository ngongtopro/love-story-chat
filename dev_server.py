#!/usr/bin/env python
"""
Love Chat Development Server Launcher

This script automatically starts both Django backend and Vite frontend servers.
Usage:
    python dev_server.py                    # Start both servers
    python dev_server.py --no-vite         # Start only Django
    python dev_server.py --port 8080       # Custom Django port
    python dev_server.py --vite-port 3000  # Custom Vite port
"""

import os
import sys
import argparse
import subprocess
import signal
import time


def main():
    parser = argparse.ArgumentParser(
        description='Start Love Chat development servers'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=8000,
        help='Django server port (default: 8000)'
    )
    parser.add_argument(
        '--vite-port',
        type=int, 
        default=5174,
        help='Vite server port (default: 5174)'
    )
    parser.add_argument(
        '--no-vite',
        action='store_true',
        help='Start only Django server'
    )
    parser.add_argument(
        '--production',
        action='store_true',
        help='Build frontend for production'
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print('❌ Error: manage.py not found. Please run from Django project root.')
        sys.exit(1)
    
    # Build frontend if production mode
    if args.production:
        print('🏗️  Building frontend for production...')
        build_frontend()
        return
    
    # Start development servers
    print('🚀 Starting Love Chat Development Environment...')
    print(f'📍 Django will run on: http://localhost:{args.port}')
    
    if not args.no_vite:
        print(f'⚡ Vite will run on: http://localhost:{args.vite_port}')
    
    print('='*50)
    
    try:
        # Use our custom runserver command
        cmd = [
            sys.executable, 
            'manage.py', 
            'runserver', 
            f'0.0.0.0:{args.port}'
        ]
        
        if args.no_vite:
            cmd.append('--no-vite')
        else:
            cmd.extend(['--vite-port', str(args.vite_port)])
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print('\n🛑 Shutting down servers...')
    except Exception as e:
        print(f'❌ Error: {e}')
        sys.exit(1)


def build_frontend():
    """Build frontend for production"""
    frontend_path = os.path.join(os.getcwd(), 'frontend')
    
    if not os.path.exists(frontend_path):
        print('❌ Frontend directory not found')
        return
    
    try:
        npm_cmd = 'npm.cmd' if os.name == 'nt' else 'npm'
        
        # Install dependencies
        print('📦 Installing frontend dependencies...')
        subprocess.run([npm_cmd, 'install'], cwd=frontend_path, check=True)
        
        # Build for production
        print('🔨 Building frontend...')
        subprocess.run([npm_cmd, 'run', 'build'], cwd=frontend_path, check=True)
        
        print('✅ Frontend built successfully!')
        print('📁 Build output in: frontend/dist/')
        
    except subprocess.CalledProcessError as e:
        print(f'❌ Build failed: {e}')
        sys.exit(1)
    except FileNotFoundError:
        print('❌ npm not found. Please install Node.js')
        sys.exit(1)


if __name__ == '__main__':
    main()
