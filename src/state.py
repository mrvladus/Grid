from __future__ import annotations
from typing import TYPE_CHECKING

from gi.repository import Adw, Gtk  # type:ignore


if TYPE_CHECKING:
    from palette_bar import PaletteBar
    from drawing_area import DrawingArea

app_styles: str = """
.drawing-area {
    border-radius: 0px;
    border: solid 1px @borders;
}

.palette-bar {
    border-radius: 12px;
    border: solid 1px @borders;
    margin: 0px 12px 12px 12px;
    background-color: @card_shade_color;
}

.palette-bar overshoot, .palette-bar undershoot{
    all: unset;
}

.default-color {
    background-color: #000000ff;
}
"""


class State:
    icon_theme: Gtk.IconTheme
    # Widgets
    application: Adw.Application = None
    main_window: Adw.ApplicationWindow = None
    palette_bar: PaletteBar = None
    drawing_area: DrawingArea = None

    # Styles
    styles: str = app_styles
    css_provider: Gtk.CssProvider
    style_manager: Adw.StyleManager = Adw.StyleManager.get_default()

    current_color: str = "#000000ff"
    canvas_size: int = 4
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
        State.styles += f".{style_class}{{background-color:{color};border: solid 1px shade({color}, 0.9);}}\n"
        cls.update_styles()
        return style_class

    @classmethod
    def set_current_solor(cls, hex: str) -> None:
        cls.current_color = hex
        print(cls.current_color)
