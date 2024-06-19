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


def hex_to_rgba(hex_code: str) -> tuple[int, int, int, int]:
    """Convert HEX to RGBA 0-1 floats tuple"""
    hex_code = hex_code.lstrip("#")
    r: int = int(hex_code[0:2], 16)
    g: int = int(hex_code[2:4], 16)
    b: int = int(hex_code[4:6], 16)
    a: int = int(hex_code[6:8], 16) if len(hex_code) > 6 else 255
    return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)


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


def save_png(path: str):
    # Create a Cairo surface to draw on
    surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32,
        State.drawing_area.canvas_size,
        State.drawing_area.canvas_size,
    )
    cr = cairo.Context(surface)

    # Draw the pixel data onto the surface
    for x in range(State.drawing_area.canvas_size):
        for y in range(State.drawing_area.canvas_size):
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
