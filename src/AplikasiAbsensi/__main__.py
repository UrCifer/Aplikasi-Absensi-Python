import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import main

if __name__ == "__main__":
    main().main_loop()