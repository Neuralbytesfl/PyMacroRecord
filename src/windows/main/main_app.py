import json
import sys  # Correctly import sys for argv
from tkinter import *
from os import path
from platform import system  # Correctly import platform functions
from time import time
from json import load
from threading import Thread
from PIL import Image
from pystray import Icon, MenuItem

from utils.not_windows import NotWindows
from windows.window import Window
from windows.main.menu_bar import MenuBar
from utils.user_settings import UserSettings
from utils.get_file import resource_path
from utils.warning_pop_up_save import confirm_save
from utils.record_file_management import RecordFileManagement
from utils.version import Version
from windows.others.new_ver_avalaible import NewVerAvailable
from hotkeys.hotkeys_manager import HotkeysManager
from macro import Macro

if system().lower() == "windows":
    from tkinter.ttk import *

class MainApp(Window):
    """Main window of the application"""

    def __init__(self, macro_file=None):
        super().__init__("PyMacroRecord", 350, 200)
        self.attributes("-topmost", 1)
        if system().lower() == "windows":
            icon_path = resource_path(path.join("assets", "logo.ico"))
            if isinstance(icon_path, list):
                icon_path = path.join(*icon_path)
            self.iconbitmap(icon_path)

        self.settings = UserSettings(self)

        self.lang = self.settings.get_config()["Language"]
        with open(resource_path(path.join('langs', self.lang + '.json')), encoding='utf-8') as f:
            self.text_content = json.load(f)

        self.text_content = self.text_content["content"]

        # For save message purpose
        self.macro_saved = False
        self.macro_recorded = False
        self.prevent_record = False

        self.version = Version(self.settings.get_config(), self)

        self.menu = MenuBar(self)  # Menu Bar
        self.macro = Macro(self)

        self.validate_cmd = self.register(self.validate_input)

        self.hotkeyManager = HotkeysManager(self)

        # Main Buttons (Start record, stop record, start playback, stop playback)

        # Play Button
        self.playImg = PhotoImage(file=resource_path(path.join("assets", "button", "play.png")))

        if macro_file:
            try:
                with open(macro_file, 'r') as record:
                    loaded_content = load(record)
                self.macro.import_record(loaded_content)
                self.playBtn = Button(self, image=self.playImg, command=self.macro.start_playback)
                self.macro_recorded = True
                self.macro_saved = True
            except Exception as e:
                print(f"Failed to load the macro file: {e}")
                self.playBtn = Button(self, image=self.playImg, state=DISABLED)
        else:
            self.playBtn = Button(self, image=self.playImg, state=DISABLED)
        self.playBtn.pack(side=LEFT, padx=50)

        # Record Button
        self.recordImg = PhotoImage(file=resource_path(path.join("assets", "button", "record.png")))
        self.recordBtn = Button(self, image=self.recordImg, command=self.macro.start_record)
        self.recordBtn.pack(side=RIGHT, padx=50)

        # Stop Button
        self.stopImg = PhotoImage(file=resource_path(path.join("assets", "button", "stop.png")))

        record_management = RecordFileManagement(self, self.menu)

        self.bind('<Control-Shift-S>', record_management.save_macro_as)
        self.bind('<Control-s>', record_management.save_macro)
        self.bind('<Control-l>', record_management.load_macro)
        self.bind('<Control-n>', record_management.new_macro)

        self.protocol("WM_DELETE_WINDOW", self.quit_software)
        if system().lower() != "darwin":
            Thread(target=self.systemTray).start()

        self.attributes("-topmost", 0)

        if system() != "Windows" and self.settings.first_time:
            NotWindows(self)

        if self.settings.get_config()["Others"]["Check_update"]:
            if self.version.new_version != "" and self.version.version != self.version.new_version:
                if time() > self.settings.get_config()["Others"]["Remind_new_ver_at"]:
                    NewVerAvailable(self, self.version.new_version)

        self.mainloop()

    def systemTray(self):
        """Just to show little icon on system tray"""
        image = Image.open(resource_path(path.join("assets", "logo.ico")))
        menu = (
            MenuItem('Show', action=self.deiconify, default=True),
        )
        self.icon = Icon("name", image, "PyMacroRecord", menu)
        self.icon.run()

    def validate_input(self, action, value_if_allowed):
        """Prevents from adding letters on an Entry label"""
        if action == "1":  # Insert
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        return True

    def quit_software(self, force=False):
        if not self.macro_saved and self.macro_recorded and not force:
            wantToSave = confirm_save(self)
            if wantToSave:
                RecordFileManagement(self, self.menu).save_macro()
            elif wantToSave is None:
                return
        if system().lower() != "darwin":
            self.icon.stop()
        if system().lower() == "linux":
            self.destroy()
        self.quit()
