from gi.repository import Gtk, Adw, Gdk  # type:ignore


class Box(Gtk.Box):
    def __init__(self, children: list[str], **kwargs):
        super().__init__(**kwargs)
        for child in children:
            self.append(child)
