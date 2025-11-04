# Export Scripts Documentation

This directory contains Python scripts that extract and process data from the original Pokémon Red/Blue game files and convert them into a SQLite database format for use in the online game.

## Overview

The export scripts parse the disassembled Pokémon Red/Blue source code from the `pokemon-game-data` submodule and convert various game data into a structured SQLite database (`pokemon.db`).

## Prerequisites

- Python 3.7+
- `rgbgfx` tool (from RGBDS project) for converting PNG tilesets to 2bpp format
- The `pokemon-game-data` submodule must be initialized

## Scripts Overview

### Core Export Scripts

#### `export_map.py` (Main Script)
**Purpose**: Extracts map data, tilesets, and collision information from the original game.

**What it does**:
- Parses map constants and headers from assembly files
- Extracts tileset data (PNG images and 2bpp files)
- Parses collision data from `collision_tile_ids.asm`
- Creates the main database structure
- Populates `tiles_raw` table with walkability data

**Key Features**:
- Automatically generates 2bpp files from PNG tilesets if needed
- Determines walkability based on original game collision data
- Handles overworld map coordinate inversion
- Creates map connection data

**Usage**:
```bash
cd export_scripts
python export_map.py
```

#### `create_zones_and_tiles.py`
**Purpose**: Processes raw tile data into the final `tiles` table with proper walkability.

**What it does**:
- Extracts unique tile images from tilesets
- Creates the final `tiles` table from `tiles_raw` data
- Applies collision detection to determine walkability
- Handles duplicate tile detection and optimization

**Usage**:
```bash
cd export_scripts
python create_zones_and_tiles.py
```

### Data Export Scripts

#### `export_pokemon.py`
**Purpose**: Extracts Pokémon data including stats, moves, and evolution information.

#### `export_moves.py`
**Purpose**: Extracts move data including power, accuracy, and effects.

#### `export_items.py`
**Purpose**: Extracts item data including descriptions and effects.

#### `export_objects.py`
**Purpose**: Extracts object/NPC data from the game.

#### `export_warps.py`
**Purpose**: Extracts warp point data for map transitions.

### Utility Scripts

#### `update_zone_coordinates.py`
**Purpose**: Updates zone coordinate data in the database.

#### `update_object_coordinates.py`
**Purpose**: Updates object coordinate data in the database.

#### `update_overworld_tiles.py`
**Purpose**: Updates overworld tile data.

#### `move_files.py`
**Purpose**: Utility for moving and organizing files.

## Database Schema

The scripts create several key tables:

### Core Tables
- **`maps`**: Map metadata (name, dimensions, tileset, etc.)
- **`tilesets`**: Tileset information and file paths
- **`tiles_raw`**: Raw tile data with walkability information
- **`tiles`**: Final processed tile data
- **`collision_tiles`**: Collision data from original game
- **`map_connections`**: Map transition data

### Game Data Tables
- **`pokemon`**: Pokémon species data
- **`moves`**: Move data
- **`items`**: Item data
- **`objects`**: NPC/object data
- **`warps`**: Warp point data

## Typical Workflow

1. **Initial Setup**:
   ```bash
   # Ensure pokemon-game-data submodule is initialized
   git submodule update --init --recursive
   
   # Install dependencies
   npm install
   ```

2. **Export Map Data**:
   ```bash
   cd export_scripts
   python export_map.py
   ```

3. **Create Final Tiles**:
   ```bash
   python create_zones_and_tiles.py
   ```

4. **Export Game Data** (optional):
   ```bash
   python export_pokemon.py
   python export_moves.py
   python export_items.py
   python export_objects.py
   python export_warps.py
   ```

## File Structure

```
export_scripts/
├── README.md                    # This file
├── export_map.py               # Main map export script
├── create_zones_and_tiles.py   # Tile processing script
├── export_pokemon.py           # Pokémon data export
├── export_moves.py             # Move data export
├── export_items.py             # Item data export
├── export_objects.py           # Object data export
├── export_warps.py             # Warp data export
├── update_*.py                 # Various update scripts
├── move_files.py               # File organization utility
├── export.js                   # Node.js export script
└── tile_images/                # Generated tile images
```

## Key Concepts

### Walkability System
The scripts implement a walkability system based on the original game's collision detection:
- Collision data is parsed from `collision_tile_ids.asm`
- Each tileset has specific tile IDs that are non-walkable
- The `is_walkable` field is calculated during export and stored in the database

### Tileset Processing
- PNG tilesets are converted to 2bpp format using `rgbgfx`
- Tiles are 8x8 pixels, blocks are 2x2 tiles (16x16 pixels)
- Maps reference blocks, which reference tiles

### Coordinate System
- Overworld maps have their Y-coordinates inverted during export
- This matches the original game's coordinate system

## Troubleshooting

### Common Issues

1. **Missing rgbgfx tool**:
   ```bash
   # Install RGBDS (includes rgbgfx)
   # On macOS: brew install rgbds
   # On Ubuntu: sudo apt-get install rgbds
   ```

2. **Missing pokemon-game-data**:
   ```bash
   git submodule update --init --recursive
   ```

3. **Permission errors**:
   ```bash
   # Ensure write permissions to export_scripts directory
   chmod +w export_scripts/
   ```

### Debugging

- Check the console output for warnings and errors
- Verify that `pokemon.db` is created successfully
- Use SQLite commands to inspect the database:
  ```bash
  sqlite3 ../pokemon.db ".tables"
  sqlite3 ../pokemon.db "SELECT COUNT(*) FROM tiles"
  ```

## Performance Notes

- The export process can take several minutes for large datasets
- The `tiles_raw` table can contain 20,000+ entries
- Tile image extraction is optimized to handle duplicates efficiently
- Database operations are batched for better performance

## Contributing

When modifying export scripts:
1. Test with a small subset of data first
2. Verify database schema changes are backward compatible
3. Update this documentation if adding new scripts or changing workflows
4. Ensure the `pokemon.db` file is properly generated 