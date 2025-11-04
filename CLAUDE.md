# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project extracts game data and graphics from the original Pokemon Red/Blue GameBoy game, recreates the game engine, and makes it online, dynamic, and multiplayer. The goal is to keep the game world and NPCs true to the original while adding new player-owned areas, reimagining combat mechanics, and making it online and social.

**Tech Stack:**
- Python scripts for data extraction from [pokered](https://github.com/pret/pokered) disassembled code
- Node.js/Express for the server (port 3000)
- Phaser 3 game engine with TypeScript for the browser client (port 8080)
- SQLite database (`pokemon.db`) for game data
- WebSocket for real-time NPC movement updates

## Development Commands

### Setup
```bash
# Clone with submodules (required for pokemon-game-data)
git clone https://github.com/brynnb/pokemon-online.git --recurse-submodules

# OR initialize submodules after cloning
git submodule update --init --recursive

# Install dependencies
npm install

# Export game data from pokemon-game-data submodule to pokemon.db
npm run export
```

### Running the Game
```bash
# Run both client and server together (recommended)
npm run start:all

# OR run separately:
# Client (Vite dev server on port 8080)
cd pokemon-phaser && npm run dev

# Server (Node.js on port 3000) with auto-reload
npm run dev

# Production build of client
cd pokemon-phaser && npm run build
```

### Data Export Scripts
```bash
cd export_scripts

# Main map export (creates database structure, extracts tilesets and collision data)
python export_map.py

# Process tiles (creates final tiles table with walkability)
python create_zones_and_tiles.py

# Additional exports (Pokemon, moves, items, NPCs, warps)
python export_pokemon.py
python export_moves.py
python export_items.py
python export_objects.py
python export_warps.py
```

**Note:** Export scripts require the `rgbgfx` tool from RGBDS project to convert PNG tilesets to 2bpp format.

## Architecture

### Server Architecture (Node.js)

**Entry Point:** `server/server.js`
- Creates Express app and HTTP server
- Initializes Database connection (`server/database.js`)
- Sets up WebSocket server (`server/websocket.js`)
- Initializes NPCMovementManager (`server/npcMovement.js`) as global singleton
- Configures routes via `server/routes.js`

**Key Components:**
- `server/database.js`: SQLite wrapper with promise-based API for tiles, maps, NPCs, items, warps
- `server/routes.js`: REST API endpoints for game data
- `server/websocket.js`: Real-time NPC position updates
- `server/npcMovement.js`: Manages all walking NPC movement logic and broadcasts positions via WebSocket

**Important:** The NPCMovementManager is stored in `global.npcMovementManager` and accessed by both routes and WebSocket handlers.

### Client Architecture (Phaser 3 + TypeScript)

**Entry Point:** `pokemon-phaser/src/main.ts`

**Structure:**
- `src/scenes/TileViewer.ts`: Main game scene
- `src/managers/`: Game systems (NpcManager, TileManager, SpriteManager, UiManager)
- `src/api/`: Service layer for server communication (mapService, npcService, tileService, etc.)
- `src/controllers/`: Input handling (CameraController)
- `src/renderers/`: Rendering logic (MapRenderer)

**Manager Pattern:** Managers are instantiated in the main scene and handle their respective game systems independently.

### Database Schema (pokemon.db)

**Core Tables:**
- `maps`: Map metadata (name, dimensions, tileset_id, is_overworld flag)
- `tiles`: Individual tile data with x/y coordinates and map_id
- `tile_images`: Tile image paths
- `tilesets`: Tileset information
- `objects`: NPCs and items with coordinates, sprite names, action types (STAY/WALK)
- `warps`: Map transition points
- `pokemon`, `moves`, `items`: Game data from original Pokemon Red/Blue

**Key Query Pattern:** Most queries filter by `is_overworld = 1` to only show overworld maps.

### Pokemon Red/Blue Map System

The original game uses a hierarchical tile system:
- **Tiles**: 8x8 pixel units (stored in 2bpp format)
- **Blocks**: 4x4 tiles (16x16 pixels per block = 2x2 in-game squares)
- **Maps**: Grid of block references stored in .blk files

**Data Flow:**
1. Export scripts parse pokered assembly files and tilesets
2. Tilesets converted from PNG to 2bpp (4 shades of gray, bits spread across byte pairs)
3. Blocksets define common 4x4 tile combinations
4. Map files contain byte references to blocks
5. Collision data determines tile walkability

**Map Connections:** Maps connect in cardinal directions with offset parameters (measured in blocks):
- North/South connections: x-axis offset (horizontal shift)
- East/West connections: y-axis offset (vertical shift)
- Positive offset = shift right/down, negative = shift left/up

### NPC Movement System

Walking NPCs are managed server-side:
- NPCMovementManager loads NPCs with `action_type = 'WALK'` from database
- NPCs move on interval with collision detection
- Position updates broadcast to all clients via WebSocket
- Clients render NPCs at server-provided positions

**Important:** NPC state is authoritative on server, clients only render positions.

## Project Structure Notes

- `pokemon-game-data/`: Git submodule with disassembled Pokemon Red source (MUST be initialized)
- `export_scripts/`: Python scripts to extract game data to pokemon.db
- `server/`: Node.js backend
- `pokemon-phaser/`: Phaser 3 client (TypeScript)
- `tile_images/`: Generated tile images (8x8 PNG files)
- `sprites/`: Character and NPC sprites
- `pokemon.db`: SQLite database generated by export scripts

## Common Development Tasks

### Modifying Server Code
Server uses nodemon for auto-reload. Changes to `server/**/*.js` trigger automatic restart.

### Working with Maps
Maps reference tilesets and blocks. To understand map rendering, see `documentation/maplogic.md` for detailed explanation of the tileset → blockset → map hierarchy.

### Database Changes
After modifying export scripts, regenerate the database:
```bash
npm run export  # or run individual export_*.py scripts
```

### WebSocket Testing
WebSocket messages use JSON format with `type` field. See `server/websocket.js` for available message types (subscribe, requestWalkingNpcs).

## Important Patterns

1. **Coordinate Systems**: Overworld maps have Y-coordinates inverted during export to match original game
2. **Tile Walkability**: Determined from collision_tile_ids.asm during export, stored in database
3. **Sprite Paths**: Sprites served via `/api/sprite/:name` endpoint with case-insensitive fallback
4. **API Responses**: All endpoints return JSON, errors include `{error: "message"}` format
