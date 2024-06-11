import cairo
from gi.repository import Adw, Gtk  # type:ignore

from state import State
from utils import Utils


class DrawingArea(Adw.Bin):
    cur_pos: list[int, int] = None

    def __init__(self) -> None:
        super().__init__()
        State.drawing_area = self
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_cursor_from_name("cell")
        self.add_css_class("drawing-area")

        self.grid_size: int = 20  # Size of each grid cell (pixels)

        self.drawing_area: Gtk.DrawingArea = Gtk.DrawingArea(
            halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER
        )
        self.drawing_area.set_content_width(State.canvas_size * self.grid_size)
        self.drawing_area.set_content_height(State.canvas_size * self.grid_size)
        self.drawing_area.set_draw_func(self.on_draw)

        self.set_child(self.drawing_area)

        State.pixel_data = [
            [(255, 255, 255, 0)] * State.canvas_size for _ in range(State.canvas_size)
        ]  # Initialize all pixels to transparent

        # Use a GtkGestureClick to handle button press events
        self.click_ctrl: Gtk.GestureClick = Gtk.GestureClick.new()
        self.click_ctrl.connect("pressed", self.on_button_press)
        self.drawing_area.add_controller(self.click_ctrl)

        # Motion ctrl
        self.motion_ctrl = Gtk.EventControllerMotion()
        self.motion_ctrl.connect("motion", self.__on_pointer_motion)
        self.motion_ctrl.connect("leave", self.__on_pointer_leave)
        self.drawing_area.add_controller(self.motion_ctrl)

    def __on_pointer_motion(self, _, x: float, y: float):
        # Return if pointer is outside area
        if x < 0 or y < 0:
            return
        # Get new x y pos
        new_cur_pos: list[int] = [int(x // self.grid_size), int(y // self.grid_size)]
        # Return if new and old pos is same
        if new_cur_pos == self.cur_pos:
            return
        self.cur_pos = new_cur_pos
        # If button is clicked - continue drawing
        if (
            self.click_ctrl.get_current_button() == 1
            and new_cur_pos[0] < State.canvas_size
            and new_cur_pos[1] < State.canvas_size
        ):
            State.pixel_data[new_cur_pos[1]][new_cur_pos[0]] = Utils.hex_to_rgba(
                State.current_color
            )
        self.drawing_area.queue_draw()

    def __on_pointer_leave(self, _):
        self.cur_pos = None
        self.drawing_area.queue_draw()

    def on_draw(
        self,
        drawing_area: Gtk.DrawingArea,
        cr: cairo.Context,
        width: int,
        height: int,
    ) -> None:
        for x in range(State.canvas_size):
            for y in range(State.canvas_size):
                cr.set_source_rgba(*Utils.rgba_to_float(*State.pixel_data[y][x]))
                cr.rectangle(
                    x * self.grid_size,
                    y * self.grid_size,
                    self.grid_size,
                    self.grid_size,
                )
                cr.fill()
                # cr.set_source_rgba(0.8, 0.8, 0.8, 1)  # Draw grid lines
                # cr.rectangle(
                #     x * self.grid_size,
                #     y * self.grid_size,
                #     self.grid_size,
                #     self.grid_size,
                # )
                # cr.stroke()
        # Draw cursor cell
        if self.cur_pos:
            cr.set_source_rgba(
                *Utils.rgba_to_float(*Utils.hex_to_rgba(State.current_color))
            )
            cr.rectangle(
                self.cur_pos[0] * self.grid_size,
                self.cur_pos[1] * self.grid_size,
                self.grid_size,
                self.grid_size,
            )
            cr.fill()

    def on_button_press(
        self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float
    ) -> None:
        grid_x: int = int(x // self.grid_size)
        grid_y: int = int(y // self.grid_size)
        if 0 <= grid_x < State.canvas_size and 0 <= grid_y < State.canvas_size:
            State.pixel_data[grid_y][grid_x] = Utils.hex_to_rgba(
                State.current_color
            )  # Toggle pixel
            self.drawing_area.queue_draw()  # Redraw the drawing area
