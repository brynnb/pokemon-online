const WebSocket = require("ws");

function setupWebSocket(server) {
  const wss = new WebSocket.Server({ server });

  // WebSocket connection handler
  wss.on("connection", (ws, req) => {
    console.log("New client connected");

    // Send initial connection message
    ws.send(
      JSON.stringify({ type: "connection", message: "Connected to server" })
    );

    // Handle client messages
    ws.on("message", (message) => {
      try {
        const data = JSON.parse(message);

        // Handle different message types if needed
        if (data.type === "subscribe") {
          // Client is subscribing to updates
          ws.send(
            JSON.stringify({
              type: "subscribed",
              message: "Subscribed to tile updates",
            })
          );
        } else if (data.type === "requestWalkingNpcs") {
          // Client is requesting the current list of walking NPCs
          if (global.npcMovementManager) {
            const walkingNpcs = global.npcMovementManager.getAllNPCs();
            ws.send(
              JSON.stringify({
                type: "walkingNpcsList",
                npcs: walkingNpcs,
              })
            );
          } else {
            ws.send(
              JSON.stringify({
                type: "walkingNpcsList",
                npcs: [],
                error: "NPC movement manager not initialized",
              })
            );
          }
        }
      } catch (error) {
        console.error("Error processing message:", error);
      }
    });
  });

  return wss;
}

module.exports = setupWebSocket;
