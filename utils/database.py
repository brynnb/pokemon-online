"""
Database utility functions for optimized batch inserts and transaction management.

This module provides efficient database operations for the Pokemon export scripts,
including bulk inserts with configurable batch sizes and PRAGMA optimizations.
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Tuple, Any, Optional

logger = logging.getLogger(__name__)


class BulkInsertOptimizer:
    """
    Context manager for optimizing SQLite during bulk insert operations.

    Temporarily disables safety features for maximum write performance,
    then restores them afterward.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.original_settings = {}

    def __enter__(self):
        """Enable performance optimizations for bulk inserts."""
        cursor = self.conn.cursor()

        # Store original settings
        self.original_settings['synchronous'] = cursor.execute(
            'PRAGMA synchronous'
        ).fetchone()[0]
        self.original_settings['journal_mode'] = cursor.execute(
            'PRAGMA journal_mode'
        ).fetchone()[0]

        # Apply performance optimizations
        cursor.execute('PRAGMA synchronous = OFF')  # Don't wait for OS writes
        cursor.execute('PRAGMA journal_mode = MEMORY')  # Keep journal in memory
        cursor.execute('PRAGMA cache_size = -64000')  # Use 64MB cache
        cursor.execute('PRAGMA temp_store = MEMORY')  # Temp tables in memory

        logger.debug("Enabled bulk insert optimizations")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original database settings."""
        cursor = self.conn.cursor()

        # Restore original settings
        cursor.execute(
            f"PRAGMA synchronous = {self.original_settings['synchronous']}"
        )
        cursor.execute(
            f"PRAGMA journal_mode = {self.original_settings['journal_mode']}"
        )

        logger.debug("Restored original database settings")
        return False


@contextmanager
def get_optimized_connection(db_path: str, bulk_insert_mode: bool = False):
    """
    Context manager for database connections with optional bulk insert optimizations.

    Args:
        db_path: Path to SQLite database file
        bulk_insert_mode: If True, enables performance optimizations for bulk inserts

    Yields:
        sqlite3.Connection: Database connection

    Example:
        with get_optimized_connection('pokemon.db', bulk_insert_mode=True) as conn:
            bulk_insert_tiles(conn, tiles_data)
    """
    conn = sqlite3.connect(db_path)

    try:
        if bulk_insert_mode:
            with BulkInsertOptimizer(conn):
                yield conn
        else:
            yield conn
    finally:
        conn.close()


def bulk_insert(
    conn: sqlite3.Connection,
    table: str,
    columns: List[str],
    data: List[Tuple[Any, ...]],
    batch_size: int = 5000,
    use_transaction: bool = True
) -> int:
    """
    Efficiently insert large amounts of data in batches.

    Args:
        conn: Database connection
        table: Table name
        columns: List of column names
        data: List of tuples containing row data
        batch_size: Number of rows per batch (default: 5000)
        use_transaction: Wrap inserts in explicit transaction (default: True)

    Returns:
        Total number of rows inserted

    Example:
        tiles_data = [
            (x, y, map_id, tile_image_id, is_walkable),
            ...
        ]
        bulk_insert(
            conn, 'tiles',
            ['x', 'y', 'map_id', 'tile_image_id', 'is_walkable'],
            tiles_data,
            batch_size=5000
        )
    """
    if not data:
        logger.warning(f"No data provided for bulk insert into {table}")
        return 0

    cursor = conn.cursor()
    total_inserted = 0

    # Build SQL statement
    placeholders = ', '.join(['?' for _ in columns])
    column_names = ', '.join(columns)
    sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

    # Execute in batches
    num_batches = (len(data) + batch_size - 1) // batch_size

    try:
        if use_transaction:
            cursor.execute('BEGIN TRANSACTION')

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            cursor.executemany(sql, batch)
            total_inserted += len(batch)

            batch_num = i // batch_size + 1
            if batch_num % 10 == 0 or batch_num == num_batches:
                logger.info(
                    f"Inserted batch {batch_num}/{num_batches} "
                    f"({total_inserted:,}/{len(data):,} rows) into {table}"
                )

        if use_transaction:
            conn.commit()

        logger.info(
            f"Successfully inserted {total_inserted:,} rows into {table}"
        )

    except Exception as e:
        if use_transaction:
            conn.rollback()
        logger.error(f"Error during bulk insert into {table}: {e}")
        raise

    return total_inserted


def bulk_insert_or_ignore(
    conn: sqlite3.Connection,
    table: str,
    columns: List[str],
    data: List[Tuple[Any, ...]],
    batch_size: int = 5000
) -> int:
    """
    Bulk insert with INSERT OR IGNORE to skip duplicates.

    Args:
        conn: Database connection
        table: Table name
        columns: List of column names
        data: List of tuples containing row data
        batch_size: Number of rows per batch (default: 5000)

    Returns:
        Total number of rows processed (may be fewer than inserted due to duplicates)
    """
    if not data:
        return 0

    cursor = conn.cursor()

    # Build SQL statement with OR IGNORE
    placeholders = ', '.join(['?' for _ in columns])
    column_names = ', '.join(columns)
    sql = f"INSERT OR IGNORE INTO {table} ({column_names}) VALUES ({placeholders})"

    try:
        cursor.execute('BEGIN TRANSACTION')

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            cursor.executemany(sql, batch)

            if (i // batch_size + 1) % 10 == 0:
                logger.debug(f"Processed batch {i // batch_size + 1}")

        conn.commit()
        logger.info(f"Processed {len(data):,} rows into {table} (OR IGNORE)")

    except Exception as e:
        conn.rollback()
        logger.error(f"Error during bulk insert OR IGNORE into {table}: {e}")
        raise

    return len(data)


def bulk_insert_or_replace(
    conn: sqlite3.Connection,
    table: str,
    columns: List[str],
    data: List[Tuple[Any, ...]],
    batch_size: int = 5000
) -> int:
    """
    Bulk insert with INSERT OR REPLACE to update duplicates.

    Args:
        conn: Database connection
        table: Table name
        columns: List of column names
        data: List of tuples containing row data
        batch_size: Number of rows per batch (default: 5000)

    Returns:
        Total number of rows processed
    """
    if not data:
        return 0

    cursor = conn.cursor()

    # Build SQL statement with OR REPLACE
    placeholders = ', '.join(['?' for _ in columns])
    column_names = ', '.join(columns)
    sql = f"INSERT OR REPLACE INTO {table} ({column_names}) VALUES ({placeholders})"

    try:
        cursor.execute('BEGIN TRANSACTION')

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            cursor.executemany(sql, batch)

            if (i // batch_size + 1) % 10 == 0:
                logger.debug(f"Processed batch {i // batch_size + 1}")

        conn.commit()
        logger.info(f"Processed {len(data):,} rows into {table} (OR REPLACE)")

    except Exception as e:
        conn.rollback()
        logger.error(f"Error during bulk insert OR REPLACE into {table}: {e}")
        raise

    return len(data)


@contextmanager
def defer_indexes(conn: sqlite3.Connection, table: str):
    """
    Context manager to drop and recreate indexes for faster bulk inserts.

    WARNING: Only use this for tables that will be completely rebuilt.

    Args:
        conn: Database connection
        table: Table name to defer indexes for

    Example:
        with defer_indexes(conn, 'tiles'):
            bulk_insert(conn, 'tiles', columns, data)
    """
    cursor = conn.cursor()

    # Get existing indexes
    cursor.execute(f"""
        SELECT sql FROM sqlite_master
        WHERE type = 'index' AND tbl_name = ?
        AND sql IS NOT NULL
    """, (table,))

    indexes = [row[0] for row in cursor.fetchall()]

    # Drop indexes
    for index_sql in indexes:
        # Extract index name from CREATE INDEX statement
        index_name = index_sql.split()[2]
        cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
        logger.debug(f"Dropped index: {index_name}")

    try:
        yield
    finally:
        # Recreate indexes
        for index_sql in indexes:
            cursor.execute(index_sql)
            logger.debug(f"Recreated index from SQL: {index_sql[:50]}...")

        conn.commit()


def vacuum_database(conn: sqlite3.Connection):
    """
    Vacuum database to reclaim space and optimize performance.

    Args:
        conn: Database connection
    """
    logger.info("Vacuuming database...")
    conn.execute('VACUUM')
    logger.info("Database vacuumed successfully")


def analyze_database(conn: sqlite3.Connection):
    """
    Analyze database to update query optimizer statistics.

    Args:
        conn: Database connection
    """
    logger.info("Analyzing database...")
    conn.execute('ANALYZE')
    logger.info("Database analyzed successfully")
