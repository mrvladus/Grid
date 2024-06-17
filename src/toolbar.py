import cairo
from gi.repository import Gdk, Gtk, Xdp  # type:ignore
from state import State
import utils as Utils


class ButtonTool(Gtk.Button):
    def __init__(
        self, tooltip: str = None, icon_name: str = None, shortcut: str = None
    ) -> None:
        super().__init__()
        self.set_icon_name(icon_name)
        if tooltip:
            self.set_tooltip_text(tooltip)
        if shortcut:
            self.add_controller(Utils.button_shortcut(shortcut))


class DrawTool(ButtonTool):
    def __init__(
        self, tooltip: str = None, icon_name: str = None, shortcut: str = None
    ) -> None:
        super().__init__(tooltip, icon_name, shortcut)

    def do_clicked(self) -> None:
        State.toolbar.deactivate_buttons()
        State.toolbar.current_tool = self
        self.add_css_class("toolbar-btn-active")

    def left_click(self, x: int, y: int) -> None: ...

    def left_click_hold(self, x: int, y: int) -> None: ...

    def left_click_release(self, x: int, y: int) -> None: ...

    def right_click(self, x: int, y: int) -> None: ...

    def right_click_hold(self, x: int, y: int) -> None: ...

    def right_click_release(self, x: int, y: int) -> None: ...

    def draw_overlay(self, cr: cairo.Context) -> None: ...


class CustomTool: ...


class Zoom(Gtk.Box, CustomTool):
    def __init__(self) -> None:
        super().__init__()
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_valign(Gtk.Align.END)
        self.set_vexpand(True)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(5)

        self.plus_btn: Gtk.Button = Gtk.Button(
            icon_name="grid-plus-symbolic", tooltip_text="Zoom In (Ctrl+Plus)"
        )
        self.plus_btn.connect("clicked", self.__on_plus_clicked)
        self.plus_btn.add_controller(Utils.button_shortcut("<Control>equal"))
        self.append(self.plus_btn)

        self.minus_btn: Gtk.Button = Gtk.Button(
            icon_name="grid-minus-symbolic", tooltip_text="Zoom Out (Ctrl+Minus)"
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


class Pencil(DrawTool):
    def __init__(self) -> None:
        super().__init__("Pencil (P)", "grid-pencil-symbolic", "P")

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


class Line(DrawTool):
    start_pos: tuple[int, int] = None
    current_pos: tuple[int, int] = None

    def __init__(self):
        super().__init__("Line (L)", "grid-line-symbolic", "L")

    def left_click(self, x: int, y: int) -> None:
        self.start_pos = (x, y)
        self.current_pos = (x, y)

    def left_click_hold(self, x: int, y: int) -> None:
        self.current_pos = (x, y)
        State.drawing_area.drawing_area.queue_draw()

    def left_click_release(self, x: int, y: int) -> None:
        if self.start_pos:
            end_pos = (x, y)
            self.draw_line(self.start_pos, end_pos)
            self.start_pos = None
            self.current_pos = None
            State.drawing_area.drawing_area.queue_draw()

    def right_click(self, x: int, y: int) -> None:
        self.left_click(x, y)

    def right_click_hold(self, x: int, y: int) -> None:
        self.left_click_hold(x, y)

    def right_click_release(self, x: int, y: int) -> None:
        self.left_click_release(x, y)

    def draw_overlay(self, cr: cairo.Context):
        if not self.start_pos and not self.current_pos:
            return

        x0, y0 = self.start_pos
        x1, y1 = self.current_pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        if State.drawing_area.left_click_ctrl.get_current_button() == 1:
            cr.set_source_rgba(
                *Utils.rgba_to_float(
                    *Utils.hex_to_rgba(State.palette_bar.primary_color)
                )
            )
        elif State.drawing_area.right_click_ctrl.get_current_button() == 3:
            cr.set_source_rgba(
                *Utils.rgba_to_float(
                    *Utils.hex_to_rgba(State.palette_bar.secondary_color)
                )
            )

        while True:
            cr.rectangle(
                x0 * State.drawing_area.grid_size,
                y0 * State.drawing_area.grid_size,
                State.drawing_area.grid_size,
                State.drawing_area.grid_size,
            )
            cr.fill()
            if (x0 == x1) and (y0 == y1):
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_line(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> None:
        x0, y0 = start_pos
        x1, y1 = end_pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        cs: int = State.drawing_area.canvas_size - 1

        if State.drawing_area.left_click_ctrl.get_current_button() == 1:
            color = Utils.hex_to_rgba(State.palette_bar.primary_color)
        elif State.drawing_area.right_click_ctrl.get_current_button() == 3:
            color = Utils.hex_to_rgba(State.palette_bar.secondary_color)

        while True:
            if x0 > cs or x0 < 0 or y0 > cs or y0 < 0:
                break
            State.drawing_area.pixel_data[y0][x0] = color
            if (x0 == x1) and (y0 == y1):
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        State.drawing_area.queue_draw()


class Eraser(DrawTool):
    def __init__(self) -> None:
        super().__init__("Eraser (E)", "grid-eraser-symbolic", "E")

    def left_click(self, x: int, y: int) -> None:
        if (
            0 <= x < State.drawing_area.canvas_size
            and 0 <= y < State.drawing_area.canvas_size
        ):
            State.drawing_area.pixel_data[y][x] = (255, 255, 255, 0)
            State.drawing_area.drawing_area.queue_draw()

    def left_click_hold(self, x: int, y: int) -> None:
        self.left_click(x, y)

    def right_click(self, x: int, y: int) -> None:
        self.left_click(x, y)

    def right_click_hold(self, x: int, y: int) -> None:
        self.left_click(x, y)


class ColorPicker(ButtonTool):
    def __init__(self) -> None:
        super().__init__("Color Picker (C)", "grid-color-picker-symbolic", "C")

    def do_clicked(self):
        def __on_selected(portal: Xdp.Portal, task):
            color: Gdk.RGBA = Gdk.RGBA()
            color.red, color.green, color.blue = portal.pick_color_finish(task)
            color.alpha = 1
            color_rgba = color.to_string().strip("rgba()").split(",")
            State.palette_bar.primary_color = Utils.rgba_to_hex(
                [int(c) for c in color_rgba] + [255]
            )

        Xdp.Portal().pick_color(None, None, __on_selected)


class Toolbar(Gtk.Box):
    tools: list = [Pencil, Line, Eraser, ColorPicker, Zoom]
    current_tool: ButtonTool | DrawTool

    def __init__(self) -> None:
        super().__init__()
        State.toolbar = self
        self.__setup_styles()
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add_css_class("toolbar")
        for tool in self.tools:
            self.append(tool())
        Utils.get_children(self)[0].do_clicked()

    def __setup_styles(self):
        self.styles: str = """
        .toolbar-btn-active {
            background-color: @borders;
        }
        """

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_string(self.styles)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def deactivate_buttons(self) -> None:
        for btn in Utils.get_children(self):
            btn.remove_css_class("toolbar-btn-active")
