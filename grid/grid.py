from __future__ import annotations

import gi  # type:ignore

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("Xdp", "1.0")

from gi.repository import Adw, Gio  # type:ignore  # noqa: E402
from state import State  # noqa: E402
from window import Window  # noqa: E402


class Application(Adw.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id="io.github.mrvladus.Grid",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        State.application = self

    def do_activate(self) -> None:
        win = Window()
        win.present()


Application().run()
