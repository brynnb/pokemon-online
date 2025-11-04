"""
Tileset utility functions for Pokemon game data extraction.

This module provides shared utilities for working with Pokemon Red/Blue tilesets,
including functions for decoding 2bpp tile data.
"""


def decode_2bpp_tile(tile_data):
    """Decode a 2bpp tile into a 2D array of pixel values (0-3)

    Each tile is 8x8 pixels, with 2 bits per pixel.
    Pixels are spread across neighboring bytes.

    Args:
        tile_data: A bytes object containing 16 bytes of 2bpp tile data

    Returns:
        A 2D list (8x8) of pixel values ranging from 0-3, where:
        0 = white, 1 = light gray, 2 = dark gray, 3 = black
    """
    pixels = []

    # Process 16 bytes (8 rows of 2 bytes each)
    for row in range(8):
        row_pixels = []
        # Each row is represented by 2 bytes
        byte1 = tile_data[row * 2]
        byte2 = tile_data[row * 2 + 1]

        # Process each bit in the bytes
        for bit in range(8):
            # Extract the bit from each byte (from MSB to LSB)
            bit_pos = 7 - bit
            bit1 = (byte1 >> bit_pos) & 1
            bit2 = (byte2 >> bit_pos) & 1

            # Combine the bits to get the pixel value (0-3)
            pixel_value = (bit2 << 1) | bit1
            row_pixels.append(pixel_value)

        pixels.append(row_pixels)

    return pixels
