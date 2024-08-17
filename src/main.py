from windows import MainApp
from sys import platform, argv

if platform.lower() == "win32":
    import ctypes
    PROCESS_PER_MONITOR_DPI_AWARE = 2
    ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

if __name__ == "__main__":
    # Check if a file is passed as an argument
    macro_file = argv[1] if len(argv) > 1 else None
    MainApp(macro_file=macro_file)
