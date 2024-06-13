from gi.repository import Gdk, Gtk, Xdp  # type:ignore
from state import State
from utils import Utils


class ToolbarTool(Gtk.Button):
    def __init__(self, tooltip: str, icon_name: str) -> None:
        super().__init__()
        # Create cursor
        self.cursor: Gdk.Cursor = Gdk.Cursor.new_from_texture(
            Gdk.Texture.new_from_file(
                Gtk.IconTheme.get_for_display(self.get_display())
                .lookup_icon(
                    icon_name,
                    None,
                    16,
                    1,
                    Gtk.TextDirection.LTR,
                    Gtk.IconLookupFlags.FORCE_SYMBOLIC,
                )
                .get_file()
            ),
            10,
            10,
            None,
        )
        # Set icon
        self.set_icon_name(icon_name)
        # Set tooltip
        self.set_tooltip_text(tooltip)

    def do_clicked(self) -> None:
        State.toolbar.current_tool = self
        State.drawing_area.set_cursor(self.cursor)


class Zoom(Gtk.Box):
    def __init__(self) -> None:
        super().__init__()
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_valign(Gtk.Align.END)
        self.set_vexpand(True)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)

        self.plus_btn: Gtk.Button = Gtk.Button(
            icon_name="grid-plus-symbolic", css_classes=["circular", "flat"]
        )
        self.plus_btn.connect("clicked", self.__on_plus_clicked)
        self.append(self.plus_btn)

        self.label: Gtk.Label = Gtk.Label(label="100")
        self.append(self.label)

        self.minus_btn: Gtk.Button = Gtk.Button(
            icon_name="grid-minus-symbolic", css_classes=["circular", "flat"]
        )
        self.minus_btn.connect("clicked", self.__on_minus_clicked)
        self.append(self.minus_btn)

    def update_ui(self):
        self.minus_btn.set_sensitive(State.drawing_area.grid_size - 5 > 0)

    def __on_plus_clicked(self, _) -> None:
        State.drawing_area.grid_size += 5
        State.drawing_area.drawing_area.set_content_width(
            State.drawing_area.canvas_size * State.drawing_area.grid_size
        )
        State.drawing_area.drawing_area.set_content_height(
            State.drawing_area.canvas_size * State.drawing_area.grid_size
        )
        self.update_ui()

    def __on_minus_clicked(self, _) -> None:
        State.drawing_area.grid_size -= 5
        State.drawing_area.drawing_area.set_content_width(
            State.drawing_area.canvas_size * State.drawing_area.grid_size
        )
        State.drawing_area.drawing_area.set_content_height(
            State.drawing_area.canvas_size * State.drawing_area.grid_size
        )
        self.update_ui()


class Pencil(ToolbarTool):
    def __init__(self) -> None:
        super().__init__("Pencil", "grid-pencil-symbolic")

    def draw(self):
        pass


class Eraser(ToolbarTool):
    def __init__(self) -> None:
        super().__init__("Eraser", "grid-eraser-symbolic")


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
    current_tool: Gtk.Button

    def __init__(self) -> None:
        super().__init__()
        State.toolbar = self
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add_css_class("toolbar")

        self.append(Pencil())
        self.append(Eraser())
        self.append(ColorPicker())
        self.append(Zoom())
