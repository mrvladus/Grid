import random
import string
import cairo
from gi.repository import GdkPixbuf  # type:ignore
from state import State


class Utils:
    @classmethod
    def generate_random_ascii_string(cls, length: int) -> str:
        return "".join(random.choice(string.ascii_letters) for _ in range(length))

    @classmethod
    def rgba_to_hex(cls, rgba: tuple[int, int, int, int]) -> str:
        r, g, b, a = rgba
        return "#{:02x}{:02x}{:02x}{:02x}".format(r, g, b, a)

    @classmethod
    def rgba_to_float(cls, r, g, b, a):
        return r / 255.0, g / 255.0, b / 255.0, a / 255.0

    @classmethod
    def hex_to_rgba(cls, hex_code: str) -> tuple[int, int, int, int]:
        hex_code = hex_code.lstrip("#")
        r: int = int(hex_code[0:2], 16)
        g: int = int(hex_code[2:4], 16)
        b: int = int(hex_code[4:6], 16)
        a: int = int(hex_code[6:8], 16) if len(hex_code) > 6 else 255
        return (r, g, b, a)

    @classmethod
    def get_pallete_colors_from_file(cls, image_path: str) -> list[str]:
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
                color_hex: str = cls.rgba_to_hex(color_rgb)
                if color_hex not in colors:
                    colors.append(color_hex)
        colors.sort()
        return colors

    @classmethod
    def save_png(self, *_):
        # Create a Cairo surface to draw on
        surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, State.canvas_size, State.canvas_size
        )
        cr = cairo.Context(surface)

        # Draw the pixel data onto the surface
        for x in range(State.canvas_size):
            for y in range(State.canvas_size):
                cr.set_source_rgba(*Utils.rgba_to_float(*State.pixel_data[y][x]))
                cr.rectangle(x, y, 1, 1)
                cr.fill()

        surface.write_to_png("pixel_image.png")
