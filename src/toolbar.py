from gi.repository import Gdk, Gtk, Xdp  # type:ignore
from state import State
from utils import Utils


class Pencil(Gtk.Button):
    def __init__(self) -> None:
        super().__init__()
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_icon_name("grid-pencil-symbolic")
        self.set_tooltip_text("Pencil")


class ColorPicker(Gtk.Button):
    def __init__(self) -> None:
        super().__init__()
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_icon_name("grid-color-picker-symbolic")
        self.set_tooltip_text("Color Picker")

    def do_clicked(self):
        def __on_selected(portal: Xdp.Portal, task):
            color: Gdk.RGBA = Gdk.RGBA()
            color.red, color.green, color.blue = portal.pick_color_finish(task)
            color_rgba = color.to_string().strip("rgba()").split(",")
            State.set_current_solor(
                Utils.rgba_to_hex([int(c) for c in color_rgba] + [255])
            )

        Xdp.Portal().pick_color(None, None, __on_selected)


class Toolbar(Gtk.Box):
    def __init__(self) -> None:
        super().__init__()
        State.toolbar = self
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add_css_class("toolbar")

        self.append(Pencil())
        self.append(ColorPicker())
