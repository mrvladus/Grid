import cairo
from gi.repository import Adw, Gtk, Gdk  # type:ignore

from state import State
import utils as Utils


class DrawingArea(Adw.Bin):
    cur_pos: list[int, int] = None
    grid_size: int = 20
    canvas_size: int = 16
    pixel_data: list = []

    def __init__(self) -> None:
        super().__init__()
        State.drawing_area = self
        self.__build_ui()

    def __build_ui(self) -> None:
        self.drawing_area: Gtk.DrawingArea = Gtk.DrawingArea(
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            css_classes=["drawing-area"],
            cursor=Gdk.Cursor(name="cell"),
        )
        self.drawing_area.set_content_width(self.canvas_size * self.grid_size)
        self.drawing_area.set_content_height(self.canvas_size * self.grid_size)
        self.drawing_area.set_draw_func(self.on_draw)

        self.pixel_data = [
            [(255, 255, 255, 0)] * self.canvas_size for _ in range(self.canvas_size)
        ]  # Initialize all pixels to transparent

        self.left_click_ctrl: Gtk.GestureClick = Gtk.GestureClick(button=1)
        self.left_click_ctrl.connect("pressed", self.__on_left_click)
        self.drawing_area.add_controller(self.left_click_ctrl)

        self.right_click_ctrl: Gtk.GestureClick = Gtk.GestureClick(button=3)
        self.right_click_ctrl.connect("pressed", self.__on_right_click)
        self.drawing_area.add_controller(self.right_click_ctrl)

        # Motion ctrl
        self.motion_ctrl = Gtk.EventControllerMotion()
        self.motion_ctrl.connect("motion", self.__on_pointer_motion)
        self.motion_ctrl.connect("leave", self.__on_pointer_leave)
        self.drawing_area.add_controller(self.motion_ctrl)

        self.set_child(self.drawing_area)

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
        if new_cur_pos[0] < self.canvas_size and new_cur_pos[1] < self.canvas_size:
            if self.left_click_ctrl.get_current_button() == 1:
                self.pixel_data[new_cur_pos[1]][new_cur_pos[0]] = Utils.hex_to_rgba(
                    State.palette_bar.primary_color
                )
            elif self.right_click_ctrl.get_current_button() == 3:
                self.pixel_data[new_cur_pos[1]][new_cur_pos[0]] = Utils.hex_to_rgba(
                    State.palette_bar.secondary_color
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
        for x in range(self.canvas_size):
            for y in range(self.canvas_size):
                cr.set_source_rgba(*Utils.rgba_to_float(*self.pixel_data[y][x]))
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
                *Utils.rgba_to_float(
                    *Utils.hex_to_rgba(State.palette_bar.primary_color)
                )
            )
            cr.rectangle(
                self.cur_pos[0] * self.grid_size,
                self.cur_pos[1] * self.grid_size,
                self.grid_size,
                self.grid_size,
            )
            cr.fill()

    def __on_left_click(
        self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float
    ) -> None:
        grid_x: int = int(x // self.grid_size)
        grid_y: int = int(y // self.grid_size)
        if 0 <= grid_x < self.canvas_size and 0 <= grid_y < self.canvas_size:
            self.pixel_data[grid_y][grid_x] = Utils.hex_to_rgba(
                State.palette_bar.primary_color
            )
            self.drawing_area.queue_draw()

    def __on_right_click(
        self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float
    ) -> None:
        grid_x: int = int(x // self.grid_size)
        grid_y: int = int(y // self.grid_size)
        if 0 <= grid_x < self.canvas_size and 0 <= grid_y < self.canvas_size:
            self.pixel_data[grid_y][grid_x] = Utils.hex_to_rgba(
                State.palette_bar.secondary_color
            )
            self.drawing_area.queue_draw()
