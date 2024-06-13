from __future__ import annotations
from typing import TYPE_CHECKING

from gi.repository import Adw, Gtk  # type:ignore


if TYPE_CHECKING:
    from palette_bar import PaletteBar
    from drawing_area import DrawingArea
    from toolbar import Toolbar

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
    toolbar: Toolbar = None

    # Styles
    styles: str = app_styles
    css_provider: Gtk.CssProvider
    style_manager: Adw.StyleManager = Adw.StyleManager.get_default()
