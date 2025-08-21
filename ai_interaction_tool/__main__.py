# Support for python -m ai_interaction_tool
import sys
import os

# Add parent directory to path to support imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main

if __name__ == "__main__":
    sys.exit(main())
