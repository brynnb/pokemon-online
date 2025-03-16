const express = require("express");
const cors = require("cors");
const path = require("path");
const http = require("http");
const Database = require("./database");
const setupRoutes = require("./routes");
const setupWebSocket = require("./websocket");
const NPCMovementManager = require("./npcMovement");

const app = express();
const PORT = process.env.PORT || 3000;
const server = http.createServer(app);

// Enable CORS for all routes
app.use(cors());

// Serve static files from the pokemon-phaser directory
app.use(express.static(path.join(__dirname, "../pokemon-phaser")));

// Initialize database connection
const db = new Database("pokemon.db");

// Initialize WebSocket server
const wss = setupWebSocket(server);

// Global reference to the NPC movement manager
global.npcMovementManager = null;

// Setup routes
setupRoutes(app, db, global.npcMovementManager);

// Start the server
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);

  // Initialize the NPC movement manager
  global.npcMovementManager = new NPCMovementManager(db, wss);
  global.npcMovementManager.initialize().catch((err) => {
    console.error("Failed to initialize NPC movement manager:", err);
  });
});

// Handle process termination
process.on("SIGINT", async () => {
  try {
    await db.close();
    console.log("Database connection closed");
    process.exit(0);
  } catch (err) {
    console.error("Error closing the database:", err.message);
    process.exit(1);
  }
});
