# Export Scripts Improvement Roadmap

This document outlines recommended improvements to the Pokemon Red/Blue data extraction scripts.

## Priority Levels

- **P0 (Critical)**: Blocking issues or major improvements
- **P1 (High)**: Important for maintainability and debugging
- **P2 (Medium)**: Quality of life improvements
- **P3 (Low)**: Nice to have optimizations

---

## Critical Issues (P0)

### 1. Hardcoded Tileset Mappings Are Fragile
**Location:** `create_zones_and_tiles.py` lines 175-182, 447-453

**Problem:** Tileset aliases (DOJO→GYM, MART→POKECENTER) are hardcoded in multiple places.

**Solution:**
```python
# Add to config.py or utils/tileset_utils.py
TILESET_ALIASES = {
    5: 7,   # DOJO -> GYM (uses same graphics)
    2: 6    # MART -> POKECENTER (similar interior graphics)
}
```

**Files to modify:**
- Create `export_scripts/config.py`
- Update `create_zones_and_tiles.py` to use config

---

### 2. Code Duplication: decode_2bpp_tile()
**Location:** `export_map.py` and `create_zones_and_tiles.py`

**Problem:** Same function implemented twice with identical code.

**Solution:**
Create `utils/tileset_utils.py`:
```python
def decode_2bpp_tile(tile_data):
    """Decode a 2bpp tile into a 2D array of pixel values (0-3)

    Each tile is 8x8 pixels, with 2 bits per pixel.
    Pixels are spread across neighboring bytes.
    """
    # ... implementation
```

**Files to modify:**
- Create `utils/tileset_utils.py`
- Update `export_map.py` to import from utils
- Update `create_zones_and_tiles.py` to import from utils

---

### 3. Missing Dependency Validation
**Location:** `export_map.py` line 402

**Problem:** `rgbgfx` tool only checked when actually needed, causing late failures.

**Solution:**
```python
def check_dependencies():
    """Verify all required tools are installed"""
    try:
        subprocess.run(["rgbgfx", "--version"],
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: rgbgfx tool not found. Install RGBDS:")
        print("  macOS: brew install rgbds")
        print("  Ubuntu: sudo apt-get install rgbds")
        return False

if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
    main()
```

**Files to modify:**
- `export_map.py`

---

## High Priority (P1)

### 4. Implement Logging Framework
**Location:** All export scripts

**Problem:** Using `print()` statements makes debugging difficult and output noisy.

**Solution:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('export.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Replace print statements
logger.info(f"Loaded {len(map_constants)} map constants")
logger.warning(f"No matching .blk file found for map {map_name}")
logger.error(f"Error parsing blockset file {blockset_path}: {e}")
```

**Files to modify:**
- All `.py` files in `export_scripts/`
- Create `utils/logger.py` for shared logging config

---

### 5. Centralized Configuration Management
**Location:** All export scripts

**Problem:** File paths and constants scattered throughout scripts.

**Solution:**
Create `export_scripts/config.py`:
```python
from pathlib import Path

# Project structure
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "pokemon.db"

# Pokemon game data paths
GAME_DATA_ROOT = PROJECT_ROOT / "pokemon-game-data"
MAPS_DIR = GAME_DATA_ROOT / "maps"
MAP_HEADERS_DIR = GAME_DATA_ROOT / "data/maps/headers"
MAP_CONSTANTS_FILE = GAME_DATA_ROOT / "constants/map_constants.asm"
TILESETS_DIR = GAME_DATA_ROOT / "gfx/tilesets"
BLOCKSETS_DIR = GAME_DATA_ROOT / "gfx/blocksets"
TILESET_CONSTANTS_FILE = GAME_DATA_ROOT / "constants/tileset_constants.asm"
POKEMON_DATA_DIR = GAME_DATA_ROOT / "data/pokemon"

# Export settings
TILE_IMAGES_DIR = "tile_images"
BATCH_SIZE = 1000
GAMEBOY_PALETTE = [(255, 255, 255), (192, 192, 192), (96, 96, 96), (0, 0, 0)]

# Tileset aliases
TILESET_ALIASES = {
    5: 7,   # DOJO -> GYM
    2: 6    # MART -> POKECENTER
}
```

**Files to modify:**
- Create `export_scripts/config.py`
- Update all export scripts to import from config

---

### 6. Script Execution Order Validation
**Location:** `create_zones_and_tiles.py`, other dependent scripts

**Problem:** Scripts have dependencies but don't validate prerequisites exist.

**Solution:**
```python
def check_prerequisites():
    """Verify required tables exist before running this script"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    required_tables = ['maps', 'tilesets', 'tiles_raw']
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    existing_tables = {row[0] for row in cursor.fetchall()}

    missing = set(required_tables) - existing_tables
    if missing:
        logger.error(f"Missing required tables: {missing}")
        logger.error("Run export_map.py first")
        conn.close()
        return False

    conn.close()
    return True

def main():
    if not check_prerequisites():
        sys.exit(1)
    # ... rest of script
```

**Files to modify:**
- `create_zones_and_tiles.py`
- `export_objects.py`
- `export_warps.py`
- Any other dependent scripts

---

### 7. Add Data Validation
**Location:** All export scripts

**Problem:** No validation that extracted data meets expected constraints.

**Solution:**
```python
def validate_map_data(map_data):
    """Validate map data is complete and correct"""
    errors = []

    if not map_data.get('tileset_id'):
        errors.append(f"Map {map_data['name']} has no tileset_id")

    if map_data['width'] <= 0 or map_data['height'] <= 0:
        errors.append(f"Map {map_data['name']} has invalid dimensions")

    expected_blocks = map_data['width'] * map_data['height']
    if len(map_data.get('blk_data', [])) != expected_blocks:
        errors.append(f"Map {map_data['name']} block count mismatch")

    return errors

# Use after extraction
errors = validate_map_data(map_info)
if errors:
    for error in errors:
        logger.warning(error)
```

**Files to modify:**
- Create `utils/validation.py`
- Add validation calls to `export_map.py`, `export_pokemon.py`, etc.

---

### 8. Improve Collision Detection Logic
**Location:** `export_map.py` lines 809-846

**Problem:** Fallback logic assumes blocks >= 30 are non-walkable, which is arbitrary.

**Solution:**
```python
def is_block_walkable(block_index, tileset_id, conn):
    """Determine if a block is walkable based on collision data."""
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM collision_tiles
         WHERE tileset_id = ? AND tile_id = ?",
        (tileset_id, block_index)
    )

    count = cursor.fetchone()[0]

    # If explicitly marked as collision tile, not walkable
    if count > 0:
        return False

    # Check if tileset has any collision data
    cursor.execute(
        "SELECT COUNT(*) FROM collision_tiles WHERE tileset_id = ?",
        (tileset_id,)
    )
    has_collision_data = cursor.fetchone()[0] > 0

    if not has_collision_data:
        # No collision data for this tileset - log warning
        logger.warning(
            f"No collision data for tileset {tileset_id}, "
            f"using heuristic for block {block_index}"
        )
        # Use heuristic: higher indices tend to be obstacles
        return block_index < 30

    # Has collision data but block not in list = walkable
    return True
```

**Files to modify:**
- `export_map.py`

---

## Medium Priority (P2)

### 9. Optimize Database Transactions
**Location:** All export scripts

**Problem:** Many individual inserts that could be batched better.

**Solution:**
```python
def bulk_insert_tiles(conn, tiles_data):
    """Efficiently insert tiles in batches"""
    BATCH_SIZE = 5000  # Larger batches for better performance

    with conn:  # Automatic transaction management
        cursor = conn.cursor()
        for i in range(0, len(tiles_data), BATCH_SIZE):
            batch = tiles_data[i:i+BATCH_SIZE]
            cursor.executemany(
                """INSERT INTO tiles
                   (x, y, local_x, local_y, map_id,
                    tile_image_id, is_overworld, is_walkable)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                batch
            )
            logger.debug(f"Inserted batch {i//BATCH_SIZE + 1}")
```

**Files to modify:**
- All scripts with database inserts
- Consider creating `utils/database.py` with batch insert helpers

---

### 10. Better Progress Indicators
**Location:** All export scripts using `sys.stdout.write()`

**Problem:** Inconsistent and basic progress updates.

**Solution:**
```bash
pip install tqdm
```

```python
from tqdm import tqdm

for tileset_id, tileset_name in tqdm(tilesets, desc="Processing tilesets"):
    # ... process tileset
    pass
```

**Files to modify:**
- `export_map.py`
- `create_zones_and_tiles.py`
- All scripts with loops

---

### 11. Add Unit Tests
**Location:** New directory

**Problem:** No automated testing of parsing logic.

**Solution:**
Create `export_scripts/tests/` directory:

```python
# tests/test_tileset_parsing.py
import unittest
from utils.tileset_utils import decode_2bpp_tile

class TestTilesetParsing(unittest.TestCase):
    def test_decode_2bpp_tile_all_white(self):
        """Test 2bpp decoding with all white pixels"""
        tile_data = bytes([0] * 16)
        pixels = decode_2bpp_tile(tile_data)

        self.assertEqual(len(pixels), 8)
        self.assertEqual(len(pixels[0]), 8)
        self.assertTrue(all(p == 0 for row in pixels for p in row))

    def test_decode_2bpp_tile_all_black(self):
        """Test 2bpp decoding with all black pixels"""
        tile_data = bytes([0xFF] * 16)
        pixels = decode_2bpp_tile(tile_data)

        self.assertTrue(all(p == 3 for row in pixels for p in row))

# tests/test_map_parsing.py
import unittest
from export_map import find_tileset_id, find_matching_blk_file

class TestMapParsing(unittest.TestCase):
    def test_tileset_id_lookup(self):
        """Test tileset ID lookup with various name formats"""
        constants = {
            'OVERWORLD': {'id': 0, 'name': 'OVERWORLD'},
            'GYM': {'id': 7, 'name': 'GYM'}
        }

        self.assertEqual(find_tileset_id('OVERWORLD', constants), 0)
        self.assertEqual(find_tileset_id('overworld', constants), 0)
        self.assertIsNone(find_tileset_id('NONEXISTENT', constants))
```

**Files to create:**
- `export_scripts/tests/__init__.py`
- `export_scripts/tests/test_tileset_parsing.py`
- `export_scripts/tests/test_map_parsing.py`
- `export_scripts/tests/test_pokemon_parsing.py`

---

### 12. Improve Documentation of Coordinate Systems
**Location:** `export_map.py` lines 976-1004

**Problem:** Y-coordinate inversion for overworld maps is confusing.

**Solution:**
Add detailed comments with ASCII diagrams:
```python
# For overworld maps, invert Y-coordinates to match game's coordinate system
#
# Original GameBoy coords:    Our database coords:
#     ^Y                           +Y
#     |                             |
#     |                             |
#     +---> X                       +---> X
#     (0,0) bottom-left             (0,0) top-left
#
# The game stores maps with Y=0 at bottom, but we want Y=0 at top
# This reverses rows so that the game's Y=0 becomes our bottom row
if is_overworld and blk_data:
    # Convert to 2D grid
    grid = [blk_bytes[y*width:(y+1)*width] for y in range(height)]

    # Reverse rows to invert Y-axis
    grid.reverse()

    # Flatten back to 1D
    blk_data = bytes([b for row in grid for b in row])
```

**Files to modify:**
- `export_map.py`
- Add to CLAUDE.md or create COORDINATE_SYSTEMS.md

---

### 13. Add Dry-Run Mode
**Location:** All export scripts

**Problem:** No way to test scripts without modifying database.

**Solution:**
```python
parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true',
                   help='Parse data but do not write to database')
args = parser.parse_args()

def main():
    if args.dry_run:
        logger.info("DRY RUN MODE - No database changes will be made")
        # ... parse and validate without DB writes
    else:
        # ... normal execution
```

**Files to modify:**
- All export scripts

---

## Low Priority (P3)

### 14. Optimize Image Hashing
**Location:** `create_zones_and_tiles.py` lines 125-129

**Problem:** MD5 hash on PNG bytes is slower than necessary.

**Solution:**
```python
def get_image_hash(img):
    """Generate fast hash from pixel data directly"""
    # Hash pixel data, not PNG-encoded bytes
    pixel_data = img.tobytes()
    return hashlib.md5(pixel_data).hexdigest()
```

**Files to modify:**
- `create_zones_and_tiles.py`

---

### 15. Add requirements.txt
**Location:** Project root

**Problem:** Python dependencies not documented.

**Solution:**
Create `requirements.txt`:
```txt
# Python dependencies for export scripts
Pillow>=10.0.0
tqdm>=4.65.0

# Development dependencies
pytest>=7.0.0
```

And `export_scripts/README.md` addition:
```markdown
## Python Dependencies

Install dependencies:
```bash
pip install -r requirements.txt
```

**Files to create:**
- `requirements.txt` in project root

---

### 16. Better Error Recovery
**Location:** All export scripts

**Problem:** Scripts fail completely on any error.

**Solution:**
```python
def safe_extract_map(map_name, map_info):
    """Extract map data with error handling"""
    try:
        # ... extraction logic
        return map_data, None
    except Exception as e:
        error_msg = f"Failed to extract map {map_name}: {e}"
        logger.error(error_msg)
        return None, error_msg

# Use in loop
failed_maps = []
for map_name, map_info in map_constants.items():
    map_data, error = safe_extract_map(map_name, map_info)
    if error:
        failed_maps.append((map_name, error))
        continue
    # ... process successful extraction

# Report failures at end
if failed_maps:
    logger.warning(f"Failed to extract {len(failed_maps)} maps")
    for map_name, error in failed_maps:
        logger.warning(f"  {map_name}: {error}")
```

**Files to modify:**
- All export scripts

---

## Implementation Checklist

### Phase 1: Foundation (P0 + Critical P1 items)
- [ ] Create `export_scripts/config.py` with centralized configuration
- [ ] Create `utils/tileset_utils.py` with shared tile functions
- [ ] Move `decode_2bpp_tile()` to utils and update imports
- [ ] Replace hardcoded tileset aliases with config
- [ ] Add dependency validation to `export_map.py`
- [ ] Implement logging framework across all scripts
- [ ] Create `utils/logger.py` for shared logging config

### Phase 2: Robustness (Remaining P1 items)
- [ ] Add prerequisite checking to dependent scripts
- [ ] Create `utils/validation.py` with data validation functions
- [ ] Add validation calls to all export scripts
- [ ] Improve collision detection logic with better warnings
- [ ] Update all scripts to use centralized config

### Phase 3: Quality of Life (P2 items)
- [ ] Optimize database transactions with better batching
- [ ] Add progress bars using tqdm
- [ ] Create test directory structure
- [ ] Write unit tests for parsing functions
- [ ] Add detailed coordinate system documentation
- [ ] Implement dry-run mode for all scripts

### Phase 4: Polish (P3 items)
- [ ] Create `requirements.txt`
- [ ] Optimize image hashing
- [ ] Add better error recovery
- [ ] Update README with improved documentation

---

## Notes

- Many of these improvements can be implemented incrementally
- Start with Phase 1 as it provides the foundation for other improvements
- The scripts are already well-structured; these changes focus on maintainability
- Consider creating a `dev` branch for testing these changes before merging to main
