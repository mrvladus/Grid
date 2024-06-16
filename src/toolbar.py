from gi.repository import Gdk, Gtk, Xdp  # type:ignore
from state import State
import utils as Utils


class ToolbarTool(Gtk.Button):
    def __init__(self, tooltip: str, icon_name: str) -> None:
        super().__init__()
        self.set_icon_name(icon_name)
        self.set_tooltip_text(tooltip)

    def do_clicked(self) -> None:
        State.toolbar.current_tool = self

    def left_click(x: int, y: int) -> None: ...

    def left_click_hold(self, x: int, y: int) -> None: ...

    def right_click(x: int, y: int) -> None: ...

    def right_click_hold(self, x: int, y: int) -> None: ...


class Zoom(Gtk.Box):
    def __init__(self) -> None:
        super().__init__()
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_valign(Gtk.Align.END)
        self.set_vexpand(True)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(5)

        self.plus_btn: Gtk.Button = Gtk.Button(
            icon_name="grid-plus-symbolic", tooltip_text="Zoom In"
        )
        self.plus_btn.connect("clicked", self.__on_plus_clicked)
        self.plus_btn.add_controller(Utils.button_shortcut("<Control>equal"))
        self.append(self.plus_btn)

        self.minus_btn: Gtk.Button = Gtk.Button(
            icon_name="grid-minus-symbolic", tooltip_text="Zoom Out"
        )
        self.minus_btn.connect("clicked", self.__on_minus_clicked)
        self.minus_btn.add_controller(Utils.button_shortcut("<Control>minus"))
        self.append(self.minus_btn)

        # Scroll ctrl
        scroll_ctrl = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.VERTICAL
        )
        scroll_ctrl.connect("scroll", self.__on_mouse_scroll)
        State.drawing_area.add_controller(scroll_ctrl)

    def update_ui(self):
        self.minus_btn.set_sensitive(State.drawing_area.grid_size - 2 > 0)
        self.plus_btn.set_sensitive(State.drawing_area.grid_size + 2 < 40)

    def __on_plus_clicked(self, _) -> None:
        State.drawing_area.grid_size += 2
        State.drawing_area.drawing_area.set_content_width(
            State.drawing_area.canvas_size * State.drawing_area.grid_size
        )
        State.drawing_area.drawing_area.set_content_height(
            State.drawing_area.canvas_size * State.drawing_area.grid_size
        )
        self.update_ui()

    def __on_minus_clicked(self, _) -> None:
        State.drawing_area.grid_size -= 2
        State.drawing_area.drawing_area.set_content_width(
            State.drawing_area.canvas_size * State.drawing_area.grid_size
        )
        State.drawing_area.drawing_area.set_content_height(
            State.drawing_area.canvas_size * State.drawing_area.grid_size
        )
        self.update_ui()

    def __on_mouse_scroll(self, ec: Gtk.EventControllerScroll, _x: float, y: float):
        if ec.get_current_event_state() == Gdk.ModifierType.CONTROL_MASK:
            if y < 0 and self.plus_btn.get_sensitive():
                self.__on_plus_clicked(None)
            elif y > 0 and self.minus_btn.get_sensitive():
                self.__on_minus_clicked(None)


class Pencil(ToolbarTool):
    def __init__(self) -> None:
        super().__init__("Pencil", "grid-pencil-symbolic")
        State.toolbar.current_tool = self

    def left_click(self, x: int, y: int):
        if (
            0 <= x < State.drawing_area.canvas_size
            and 0 <= y < State.drawing_area.canvas_size
        ):
            State.drawing_area.pixel_data[y][x] = Utils.hex_to_rgba(
                State.palette_bar.primary_color
            )
            State.drawing_area.drawing_area.queue_draw()

    def left_click_hold(self, x: int, y: int) -> None:
        self.left_click(x, y)

    def right_click(self, x: int, y: int):
        if (
            0 <= x < State.drawing_area.canvas_size
            and 0 <= y < State.drawing_area.canvas_size
        ):
            State.drawing_area.pixel_data[y][x] = Utils.hex_to_rgba(
                State.palette_bar.secondary_color
            )
            State.drawing_area.drawing_area.queue_draw()

    def right_click_hold(self, x: int, y: int) -> None:
        self.right_click(x, y)


class Eraser(ToolbarTool):
    def __init__(self) -> None:
        super().__init__("Eraser", "grid-eraser-symbolic")

    def left_click(self, x: int, y: int):
        if (
            0 <= x < State.drawing_area.canvas_size
            and 0 <= y < State.drawing_area.canvas_size
        ):
            State.drawing_area.pixel_data[y][x] = (255, 255, 255, 0)
            State.drawing_area.drawing_area.queue_draw()

    def right_click(self, x: int, y: int):
        self.left_click(x, y)


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
    current_tool: ToolbarTool

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
