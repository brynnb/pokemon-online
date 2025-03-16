const sqlite3 = require("sqlite3").verbose();
const path = require("path");

class Database {
  constructor(dbPath) {
    this.db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error("Error connecting to the database:", err.message);
      }
    });
  }

  // Generic query methods
  all(query, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(query, params, (err, rows) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(rows);
      });
    });
  }

  get(query, params = []) {
    return new Promise((resolve, reject) => {
      this.db.get(query, params, (err, row) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(row);
      });
    });
  }

  run(query, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(query, params, function (err) {
        if (err) {
          reject(err);
          return;
        }
        resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  // Tile-related queries
  getTileImages() {
    return this.all("SELECT id, image_path FROM tile_images");
  }

  getTileImageById(tileId) {
    return this.get("SELECT image_path FROM tile_images WHERE id = ?", [
      tileId,
    ]);
  }

  getTilesByMapId(mapId) {
    return this.all(
      "SELECT t.id, t.x, t.y, t.tile_image_id, t.local_x, t.local_y, t.map_id, m.name as map_name FROM tiles t JOIN maps m ON t.map_id = m.id WHERE t.map_id = ?",
      [mapId]
    );
  }

  getTileAt(x, y, mapId) {
    return this.get(
      "SELECT * FROM tiles WHERE x = ? AND y = ? AND map_id = ?",
      [x, y, mapId]
    );
  }

  // Map-related queries
  getMapInfo(mapId) {
    return this.get(
      "SELECT id, name, tileset_id, is_overworld FROM maps WHERE id = ?",
      [mapId]
    );
  }

  getOverworldMaps() {
    return this.all("SELECT id, name FROM maps WHERE is_overworld = 1");
  }

  // Item-related queries
  getItems() {
    return this.all(
      `SELECT o.id, o.x, o.y, o.map_id, o.item_id, i.name, i.short_name as description 
       FROM objects o
       JOIN items i ON o.item_id = i.id
       JOIN maps m ON o.map_id = m.id
       WHERE o.object_type = 'item' AND m.is_overworld = 1`
    );
  }

  // NPC-related queries
  getNPCs() {
    return this.all(
      `SELECT o.id, o.x, o.y, o.map_id, o.sprite_name, o.name, o.action_type, o.action_direction 
       FROM objects o
       JOIN maps m ON o.map_id = m.id
       WHERE o.object_type = 'npc' AND m.is_overworld = 1 AND (o.action_type = 'STAY' OR o.action_type = 'WALK')`
    );
  }

  getWalkingNPCs() {
    return this.all(
      `SELECT o.id, o.x, o.y, o.map_id, o.sprite_name, o.name, o.action_type, o.action_direction 
       FROM objects o
       JOIN maps m ON o.map_id = m.id
       WHERE o.object_type = 'npc' AND m.is_overworld = 1 AND o.action_type = 'WALK'`
    );
  }

  getNPCById(npcId) {
    return this.get(
      `SELECT o.id, o.x, o.y, o.map_id, o.sprite_name, o.name, o.action_type, o.action_direction 
       FROM objects o
       JOIN maps m ON o.map_id = m.id
       WHERE o.id = ?`,
      [npcId]
    );
  }

  checkCollision(x, y, mapId, npcId) {
    return this.get(
      `SELECT * FROM objects 
       WHERE x = ? AND y = ? AND map_id = ? AND id != ?`,
      [x, y, mapId, npcId]
    ).then((row) => !!row);
  }

  // Warp-related queries
  getWarps() {
    return this.all(
      `SELECT w.id, w.source_map_id as map_id, w.x, w.y, 
              w.destination_map_id, w.destination_map, w.destination_x, w.destination_y
       FROM warps w
       JOIN maps m ON w.source_map_id = m.id
       WHERE w.x IS NOT NULL AND w.y IS NOT NULL AND m.is_overworld = 1`
    );
  }

  // Close the database connection
  close() {
    return new Promise((resolve, reject) => {
      this.db.close((err) => {
        if (err) {
          reject(err);
          return;
        }
        resolve();
      });
    });
  }
}

module.exports = Database;
