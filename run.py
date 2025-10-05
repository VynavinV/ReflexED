"""
Application entry point.
Run the Flask development server.
"""
from app import create_app
import os
import sys

app = create_app()

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    
    # Disable reloader to prevent interruptions during file generation
    # You can manually restart if you edit code
    use_reloader = os.getenv('USE_RELOADER', '0') == '1'
    
    print(f"""
    ╔═══════════════════════════════════════╗
    ║     ReflexED API Server Starting     ║
    ╠═══════════════════════════════════════╣
    ║  Environment: {os.getenv('FLASK_ENV', 'development').ljust(24)}║
    ║  URL: http://{host}:{port}{' ' * (23 - len(host) - len(str(port)))}║
    ║  Docs: http://{host}:{port}/api{' ' * (19 - len(host) - len(str(port)))}║
    ╚═══════════════════════════════════════╝
    """)
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=use_reloader
    )
