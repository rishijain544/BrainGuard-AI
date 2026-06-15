import sys
import os

# Add parent directory and backend directory to path so imports work correctly
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from backend.fastapi_backend import app
