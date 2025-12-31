import WebSocket from "ws";
import readline from "readline"

const ws = new WebSocket("ws://localhost:8602");

const optionsTable = "M - Freeze Mouse\nK - Freeze Keyboard\nUM - Unfreeze Mouse\nUK - Unfreeze Keyboard\nV - Video\nLC - List Clients";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function connect() {
  ws.on("open", () => {
    console.log("-------------------------- ADM CLIENT --------------------------\n")
    console.log("Connected to server\n");
    ws.send("ADM");

    console.log(optionsTable);

    rl.on("line", (input) => {
      const command = input.trim()

      if (command === "LC" || command === "lc") {
        ws.send("LIST_CLIENTS");
        console.log("\nRequested client list");
        return;
      }

      let sep = null;
      if (command.includes("|")) sep = "|";

      if (!sep) {
        console.log("Invalid format. Use UUID|M");
        return;
      }

      const uuid = command.split(sep)[0].toLowerCase();
      const key = command.split(sep)[1].toUpperCase();

      switch (key) {
        case "M":
          ws.send(`${uuid}|FREEZE_MOUSE`);
          console.log("Sent: FREEZE_MOUSE");
          break;
        case "K":
          ws.send(`${uuid}|FREEZE_KEYBOARD`);
          console.log("Sent: FREEZE_KEYBOARD");
          break;
        case "UM":
          ws.send(`${uuid}|UNFREEZE_MOUSE`);
          console.log("Sent: UNFREEZE_MOUSE");
          break;
        case "UK":
          ws.send(`${uuid}|UNFREEZE_KEYBOARD`);
          console.log("Sent: UNFREEZE_KEYBOARD");
          break;
        case "V":
          ws.send(`${uuid}|VIDEO`);
          console.log("Sent: VIDEO");
          break;
        default:
          console.log("Invalid command. Options are:\n" + optionsTable);
      }
    });
  });

  ws.on("message", (data) => {
    console.log("\nMessage:", data.toString());
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
