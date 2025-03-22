from pathlib import Path
from core import ZephyrusLoggerCore
from gui import ZephyrusLoggerGUI

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    core = ZephyrusLoggerCore(script_dir)
    gui = ZephyrusLoggerGUI(core)
    gui.run()
