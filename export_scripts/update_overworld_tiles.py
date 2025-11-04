import sqlite3
import sys
import os
from pathlib import Path

# Add the parent directory to the path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger, log_script_start, log_script_end

# Set up logger
logger = setup_logger(__name__)

# Get the project root directory (parent of the script's directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "pokemon.db"


def update_overworld_tiles():
    """Update tiles to mark them as overworld based on their map's is_overworld flag"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all maps marked as overworld
    cursor.execute("SELECT id, name FROM maps WHERE is_overworld = 1")
    overworld_maps = cursor.fetchall()

    if not overworld_maps:
        logger.info("No maps marked as overworld found in the database.")
        conn.close()
        return

    logger.info(f"Found {len(overworld_maps)} maps marked as overworld:")
    for map_id, map_name in overworld_maps:
        logger.info(f"  - Map {map_id}: {map_name}")

    # Count tiles in overworld maps
    cursor.execute(
        """
        SELECT COUNT(*) FROM tiles 
        WHERE map_id IN (SELECT id FROM maps WHERE is_overworld = 1)
        """
    )
    total_tiles = cursor.fetchone()[0]

    if total_tiles == 0:
        logger.info("No tiles found in overworld maps.")
        conn.close()
        return

    logger.info(f"Found {total_tiles} tiles in overworld maps.")

    # Update tiles to mark them as overworld
    cursor.execute(
        """
        UPDATE tiles 
        SET is_overworld = 1 
        WHERE map_id IN (SELECT id FROM maps WHERE is_overworld = 1)
        """
    )

    # Commit the changes
    conn.commit()

    # Verify the update
    cursor.execute("SELECT COUNT(*) FROM tiles WHERE is_overworld = 1")
    updated_tiles = cursor.fetchone()[0]

    logger.info(f"Updated {updated_tiles} tiles to be marked as overworld.")

    conn.close()


if __name__ == "__main__":
    log_script_start(logger, "update_overworld_tiles.py")
    try:
        update_overworld_tiles()
        log_script_end(logger, "update_overworld_tiles.py", success=True)
    except Exception as e:
        logger.error(f"Script failed with error: {e}", exc_info=True)
        log_script_end(logger, "update_overworld_tiles.py", success=False)
        raise
