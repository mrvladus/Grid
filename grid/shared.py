from typing import Any, Callable
from gi.repository import Gtk, Adw  # type:ignore


class Button(Gtk.Button):
    def __init__(self, on_click: Callable, **kwargs):
        super().__init__(**kwargs)
        self.connect("clicked", on_click)


class Box(Gtk.Box):
    def __init__(self, children: list[Gtk.Widget], **kwargs):
        super().__init__(**kwargs)
        for child in children:
            self.append(child)


def ToolbarView(
    top_bars: list[Gtk.Widget] = None,
    bottom_bars: list[Gtk.Widget] = None,
    **tb_kwargs,
) -> Adw.ToolbarView:
    toolbar_view: Adw.ToolbarView = Adw.ToolbarView(**tb_kwargs)
    if top_bars:
        for bar in top_bars:
            toolbar_view.add_top_bar(bar)
    if bottom_bars:
        for bar in bottom_bars:
            toolbar_view.add_bottom_bar(bar)
    return toolbar_view
