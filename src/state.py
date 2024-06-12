from __future__ import annotations
from typing import TYPE_CHECKING

from gi.repository import Adw, Gtk  # type:ignore


if TYPE_CHECKING:
    from palette_bar import PaletteBar
    from drawing_area import DrawingArea

app_styles: str = """
flowboxchild {all:unset;padding:0px;margin:0px;}
.drawing-area {
    border-radius: 0px;
    border: solid 1px @borders;
}
"""


class State:
    icon_theme: Gtk.IconTheme
    # Widgets
    application: Adw.Application = None
    main_window: Adw.ApplicationWindow = None
    palette_bar: PaletteBar = None
    drawing_area: DrawingArea = None
    toolbar = None

    # Styles
    styles: str = app_styles
    css_provider: Gtk.CssProvider
    style_manager: Adw.StyleManager = Adw.StyleManager.get_default()

    canvas_size: int = 16
    pixel_data: list = []

    @classmethod
    def update_styles(cls):
        cls.css_provider.load_from_string(cls.styles)

    @classmethod
    def add_palette_item(cls, color: str) -> str:
        from utils import Utils

        if color in cls.styles:
            return (
                [line for line in State.styles.splitlines() if color in line][0]
                .strip(".")
                .split("{")[0]
            )
        style_class = Utils.generate_random_ascii_string(20)
        State.styles += (
            f".{style_class}{{background-color:{color};border: solid 2px @borders;}}\n"
        )
        cls.update_styles()
        return style_class

    @classmethod
    def set_primary_color(cls, hex: str) -> None:
        cls.primary_color_color = hex

    @classmethod
    def set_secondary_color(cls, hex: str) -> None:
        cls.primary_color_color = hex
