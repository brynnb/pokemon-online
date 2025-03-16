const express = require("express");
const path = require("path");
const fs = require("fs");

function setupRoutes(app, db, npcMovementManager) {
  // API endpoint to get tile images
  app.get("/api/tile-images", async (req, res) => {
    try {
      const rows = await db.getTileImages();
      res.json(rows);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // Add a specific endpoint to get a tile image by ID
  app.get("/api/tile-image/:id", async (req, res) => {
    const tileId = req.params.id;

    // Validate that tileId is a number
    if (isNaN(parseInt(tileId))) {
      return res.status(400).send("Invalid tile ID");
    }

    try {
      // Get the image path from the database
      const row = await db.getTileImageById(tileId);

      if (!row) {
        // Fall back to the old calculation method if not in database
        const adjustedTileId = parseInt(tileId) - 1;
        const imagePath = path.join(
          __dirname,
          "..",
          "tile_images",
          `tile_${adjustedTileId}.png`
        );

        if (fs.existsSync(imagePath)) {
          res.setHeader("Cache-Control", "public, max-age=86400");
          return res.sendFile(imagePath);
        }

        // If all else fails, send the fallback image
        const fallbackPath = path.join(
          __dirname,
          "..",
          "tile_images",
          "tile_0.png"
        );
        if (fs.existsSync(fallbackPath)) {
          return res.sendFile(fallbackPath);
        } else {
          return res.status(404).send("Tile image not found");
        }
      }

      // Get the image path from the database
      const dbImagePath = row.image_path;

      // Convert the relative path to an absolute path
      const imagePath = path.join(__dirname, "..", dbImagePath);

      // Check if the file exists
      if (fs.existsSync(imagePath)) {
        res.setHeader("Cache-Control", "public, max-age=86400");
        res.sendFile(imagePath);
      } else {
        // Try the calculated path as a fallback
        const adjustedTileId = parseInt(tileId) - 1;
        const calculatedPath = path.join(
          __dirname,
          "..",
          "tile_images",
          `tile_${adjustedTileId}.png`
        );

        if (fs.existsSync(calculatedPath)) {
          res.setHeader("Cache-Control", "public, max-age=86400");
          return res.sendFile(calculatedPath);
        }

        // If all else fails, send the fallback image
        const fallbackPath = path.join(
          __dirname,
          "..",
          "tile_images",
          "tile_0.png"
        );
        if (fs.existsSync(fallbackPath)) {
          return res.sendFile(fallbackPath);
        } else {
          return res.status(404).send("Tile image not found");
        }
      }
    } catch (err) {
      console.error(`Database error for tile ${tileId}:`, err);
      return res.status(500).send("Database error");
    }
  });

  // Add an endpoint to serve sprite images
  app.get("/api/sprite/:name", (req, res) => {
    const spriteName = req.params.name;

    // Validate the sprite name to prevent directory traversal
    if (!spriteName || spriteName.includes("..") || spriteName.includes("/")) {
      console.error(`Invalid sprite name: ${spriteName}`);
      return res.status(400).send("Invalid sprite name");
    }

    // Construct the path to the sprite
    const spritePath = path.join(__dirname, "..", "sprites", spriteName);

    // Check if the file exists
    if (fs.existsSync(spritePath)) {
      res.setHeader("Cache-Control", "public, max-age=86400");
      return res.sendFile(spritePath);
    } else {
      // Try lowercase version as fallback
      const lowercasePath = path.join(
        __dirname,
        "..",
        "sprites",
        spriteName.toLowerCase()
      );
      console.log(`Trying lowercase path: ${lowercasePath}`);

      if (fs.existsSync(lowercasePath)) {
        console.log(`Sprite found at lowercase path: ${lowercasePath}`);
        res.setHeader("Cache-Control", "public, max-age=86400");
        return res.sendFile(lowercasePath);
      }

      // List available sprites for debugging
      try {
        const availableSprites = fs.readdirSync(
          path.join(__dirname, "..", "sprites")
        );
      } catch (err) {
        console.error(`Error listing sprites directory: ${err}`);
      }

      console.error(`Sprite not found: ${spriteName}`);
      return res.status(404).send("Sprite not found");
    }
  });

  // API endpoint to get tiles for a specific map
  app.get("/api/tiles/:mapId", async (req, res) => {
    const mapId = req.params.mapId;
    try {
      const rows = await db.getTilesByMapId(mapId);
      res.json(rows);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // API endpoint to get map info
  app.get("/api/map-info/:mapId", async (req, res) => {
    const mapId = req.params.mapId;
    try {
      const row = await db.getMapInfo(mapId);
      res.json(row);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // API endpoint to get items
  app.get("/api/items", async (req, res) => {
    try {
      const rows = await db.getItems();
      res.json(rows);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // API endpoint to get NPCs
  app.get("/api/npcs", async (req, res) => {
    try {
      const rows = await db.getNPCs();
      res.json(rows);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // API endpoint to get walking NPCs specifically
  app.get("/api/walking-npcs", async (req, res) => {
    try {
      const rows = await db.getWalkingNPCs();
      res.json(rows);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // API endpoint to get all current walking NPCs with their current positions
  app.get("/api/walking-npcs/current", (req, res) => {
    if (global.npcMovementManager) {
      const npcs = global.npcMovementManager.getAllNPCs();
      if (npcs && npcs.length > 0) {
        res.json(npcs);
      } else {
        res.status(404).json({ error: "No walking NPCs found" });
      }
    } else {
      res.status(404).json({ error: "NPC movement manager not initialized" });
    }
  });

  // API endpoint to get a specific walking NPC by ID
  app.get("/api/walking-npc/:id", (req, res) => {
    const npcId = parseInt(req.params.id);

    if (isNaN(npcId)) {
      return res.status(400).json({ error: "Invalid NPC ID" });
    }

    if (global.npcMovementManager) {
      const npc = global.npcMovementManager.getNPC(npcId);
      if (npc) {
        res.json(npc);
      } else {
        res.status(404).json({ error: `NPC with ID ${npcId} not found` });
      }
    } else {
      res.status(404).json({ error: "NPC movement manager not initialized" });
    }
  });

  // API endpoint to reset all walking NPCs to their original positions
  app.post("/api/walking-npcs/reset", (req, res) => {
    if (global.npcMovementManager) {
      global.npcMovementManager.resetToOriginalPosition();
      res.json({
        success: true,
        message: "All NPCs reset to original positions",
      });
    } else {
      res.status(404).json({ error: "NPC movement manager not initialized" });
    }
  });

  // API endpoint to reset a specific walking NPC to its original position
  app.post("/api/walking-npc/:id/reset", (req, res) => {
    const npcId = parseInt(req.params.id);

    if (isNaN(npcId)) {
      return res.status(400).json({ error: "Invalid NPC ID" });
    }

    if (global.npcMovementManager) {
      const success =
        global.npcMovementManager.resetNPCToOriginalPosition(npcId);
      if (success) {
        res.json({
          success: true,
          message: `NPC ${npcId} reset to original position`,
        });
      } else {
        res.status(404).json({
          error: `NPC with ID ${npcId} not found or could not be reset`,
        });
      }
    } else {
      res.status(404).json({ error: "NPC movement manager not initialized" });
    }
  });

  // For backward compatibility - redirect to the new endpoint
  app.get("/api/walking-npc/current", (req, res) => {
    if (global.npcMovementManager) {
      const npcs = global.npcMovementManager.getAllNPCs();
      if (npcs && npcs.length > 0) {
        // Return the first NPC for backward compatibility
        res.json(npcs[0]);
      } else {
        res.status(404).json({ error: "No walking NPC found" });
      }
    } else {
      res.status(404).json({ error: "NPC movement manager not initialized" });
    }
  });

  // For backward compatibility - redirect to the new endpoint
  app.post("/api/walking-npc/reset", (req, res) => {
    if (global.npcMovementManager) {
      global.npcMovementManager.resetToOriginalPosition();
      const npcs = global.npcMovementManager.getAllNPCs();
      res.json({
        success: true,
        npc: npcs && npcs.length > 0 ? npcs[0] : null,
        message: "All NPCs reset to original positions",
      });
    } else {
      res.status(404).json({ error: "No walking NPC found" });
    }
  });

  // API endpoint to get overworld maps
  app.get("/api/overworld-maps", async (req, res) => {
    try {
      const rows = await db.getOverworldMaps();
      res.json(rows || []);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // API endpoint to get warps
  app.get("/api/warps", async (req, res) => {
    try {
      const rows = await db.getWarps();
      res.json(rows);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // Catch-all route to serve the main index.html for client-side routing
  app.get("*", (req, res) => {
    res.sendFile(path.join(__dirname, "../pokemon-phaser", "index.html"));
  });
}

module.exports = setupRoutes;
