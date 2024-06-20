import random
import string
import cairo
from gi.repository import GdkPixbuf, Gtk  # type:ignore
from state import State


def generate_random_ascii_string(length: int) -> str:
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def rgba_to_hex(rgba: tuple[int, int, int, int]) -> str:
    r, g, b, a = rgba
    return "#{:02x}{:02x}{:02x}{:02x}".format(r, g, b, a)


def hex_to_rgba(hex_code: str) -> tuple[float, float, float, float]:
    """Convert HEX to RGBA 0-1 floats tuple"""
    hex_code = hex_code.lstrip("#")
    length = len(hex_code)
    rgb = [int(hex_code[i : i + 2], 16) / 255.0 for i in range(0, 6, 2)]
    alpha = int(hex_code[6:8], 16) / 255.0 if length == 8 else 1.0
    return (*rgb, alpha)


def get_pallete_colors_from_file(image_path: str) -> list[str]:
    # Load the image
    pixbuf: GdkPixbuf.Pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)

    # Get image dimensions and properties
    width: int = pixbuf.get_width()
    height: int = pixbuf.get_height()
    n_channels: int = pixbuf.get_n_channels()
    rowstride: int = pixbuf.get_rowstride()
    pixels: bytes = pixbuf.get_pixels()

    # Extract colors
    colors: list[str] = []
    for y in range(height):
        for x in range(width):
            offset: int = y * rowstride + x * n_channels
            color_rgb: list[int] = list(pixels[offset : offset + n_channels])
            if len(color_rgb) == 3:
                color_rgb.append(255)
            color_hex: str = rgba_to_hex(tuple(color_rgb))
            if color_hex not in colors:
                colors.append(color_hex)
    colors.sort()
    return colors


def load_png(path: str) -> list[list[str]]:
    # Load the image
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)

    # Get image properties
    width = pixbuf.get_width()
    height = pixbuf.get_height()
    rowstride = pixbuf.get_rowstride()
    n_channels = pixbuf.get_n_channels()
    pixels = pixbuf.get_pixels()

    # Initialize the 2D array for HEX values
    hex_array = []

    for y in range(height):
        row = []
        for x in range(width):
            offset = y * rowstride + x * n_channels
            r = pixels[offset]
            g = pixels[offset + 1]
            b = pixels[offset + 2]
            if n_channels == 4:
                a = pixels[offset + 3]
                hex_value = f"#{r:02X}{g:02X}{b:02X}{a:02X}"
            else:
                hex_value = f"#{r:02X}{g:02X}{b:02X}"
            row.append(hex_value)
        hex_array.append(row)

    return hex_array


def save_png(path: str):
    # Create a Cairo surface to draw on
    surface: cairo.ImageSurface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32,
        State.drawing_area.canvas_size.x,
        State.drawing_area.canvas_size.y,
    )
    cr: cairo.Context = cairo.Context(surface)

    # Draw the pixel data onto the surface
    for x in range(State.drawing_area.canvas_size.x):
        for y in range(State.drawing_area.canvas_size.y):
            cr.set_source_rgba(*hex_to_rgba(State.drawing_area.pixel_data[y][x]))
            cr.rectangle(x, y, 1, 1)
            cr.fill()

    surface.write_to_png(path)


def button_shortcut(*shortcuts: list[str]) -> Gtk.ShortcutController:
    ctrl: Gtk.ShortcutController = Gtk.ShortcutController.new()
    ctrl.set_scope(Gtk.ShortcutScope.GLOBAL)
    for shortcut in shortcuts:
        ctrl.add_shortcut(
            Gtk.Shortcut(
                action=Gtk.ShortcutAction.parse_string("activate"),
                trigger=Gtk.ShortcutTrigger.parse_string(shortcut),
            )
        )
    return ctrl


def get_children(obj: Gtk.Widget) -> list[Gtk.Widget]:
    """
    Get list of widget's children
    """

    children: list[Gtk.Widget] = []
    child: Gtk.Widget = obj.get_first_child()
    while child:
        children.append(child)
        child = child.get_next_sibling()
    return children
