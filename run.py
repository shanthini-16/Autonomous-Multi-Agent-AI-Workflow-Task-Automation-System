import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app import app
from backend.config import Config

if __name__ == "__main__":
    print("=" * 70)
    print(" Autonomous Multi-Agent AI Workflow & Task Automation System")
    print(f" Server starting on http://{Config.HOST}:{Config.PORT}")
    print(f" Theme Colors: Mocha Brown ({Config.MOCHA_BROWN}) | Champagne Gold ({Config.CHAMPAGNE_GOLD}) | Burnt Amber ({Config.BURNT_AMBER})")
    print("=" * 70)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)
