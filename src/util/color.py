def color_theme_to_rgb(color_theme):
    """Convert a profile's color_theme dict to an RGB tuple."""
    return (color_theme["r"], color_theme["g"], color_theme["b"])


def hex_to_rgb(hex_str):
    """Convert '#ff8000' to (255, 128, 0)."""
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """Convert (255, 128, 0) to '#ff8000'."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
