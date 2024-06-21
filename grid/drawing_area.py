import cairo
from gi.repository import Adw, Gtk, Gdk  # type:ignore

from state import State
import utils as Utils
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


class DrawingArea(Adw.Bin):
    cur_pos: list[int, int] = None
    prev_pos: list[int, int] = None
    grid_size: int = 20
    canvas_size: Point = Point(16, 16)
    pixel_data: list[tuple[int]] = []
    cached_surface: cairo.Surface = None

    def __init__(self) -> None:
        super().__init__()
        State.drawing_area = self
        self.__setup_styles()
        self.__build_ui()

    def __build_ui(self) -> None:
        self.add_css_class("drawing-area-container")

        # Create the drawing area widget
        self.drawing_area: Gtk.DrawingArea = Gtk.DrawingArea(
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            css_classes=["drawing-area"],
            cursor=Gdk.Cursor(name="cell"),
        )

        # Create and configure the left click gesture controller
        self.left_click_ctrl: Gtk.GestureClick = Gtk.GestureClick(button=1)
        self.left_click_ctrl.connect(
            "pressed",
            lambda _g, _n, x, y: State.toolbar.current_tool.left_click(
                int(x // self.grid_size), int(y // self.grid_size)
            ),
        )
        self.left_click_ctrl.connect(
            "released",
            lambda _g, _n, x, y: State.toolbar.current_tool.left_click_release(
                int(x // self.grid_size), int(y // self.grid_size)
            ),
        )
        self.drawing_area.add_controller(self.left_click_ctrl)

        # Create and configure the right click gesture controller
        self.right_click_ctrl: Gtk.GestureClick = Gtk.GestureClick(button=3)
        self.right_click_ctrl.connect(
            "pressed",
            lambda _g, _n, x, y: State.toolbar.current_tool.right_click(
                int(x // self.grid_size), int(y // self.grid_size)
            ),
        )
        self.right_click_ctrl.connect(
            "released",
            lambda _g, _n, x, y: State.toolbar.current_tool.right_click_release(
                int(x // self.grid_size), int(y // self.grid_size)
            ),
        )
        self.drawing_area.add_controller(self.right_click_ctrl)

        # Create and configure the motion controller
        self.motion_ctrl = Gtk.EventControllerMotion()
        self.motion_ctrl.connect("motion", self.__on_pointer_motion)
        self.motion_ctrl.connect("leave", self.__on_pointer_leave)
        self.drawing_area.add_controller(self.motion_ctrl)

        self.set_child(self.drawing_area)

    def load_image(self, pixel_data: list[list[str]]) -> None:
        self.pixel_data = pixel_data
        self.canvas_size.x = len(pixel_data[0])
        self.canvas_size.y = len(pixel_data)
        self.update_canvas_size()

        # Create a cached surface for the pixel data
        self.cached_surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32,
            self.canvas_size.x * self.grid_size,
            self.canvas_size.y * self.grid_size,
        )
        self.redraw_cached_surface()

        self.drawing_area.set_draw_func(self.on_draw)
        self.drawing_area.queue_draw()

    def update_canvas_size(self):
        # Set the size of the drawing area based on the grid size and canvas size
        self.drawing_area.set_content_width(self.canvas_size.x * self.grid_size)
        self.drawing_area.set_content_height(self.canvas_size.y * self.grid_size)

    def redraw_cached_surface(self):
        ctx = cairo.Context(self.cached_surface)
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
        for y, row in enumerate(self.pixel_data):
            for x, color in enumerate(row):
                ctx.set_source_rgba(*color)
                ctx.rectangle(
                    x * self.grid_size,
                    y * self.grid_size,
                    self.grid_size,
                    self.grid_size,
                )
                ctx.fill()

    def __setup_styles(self) -> None:
        self.styles: str = """
        .drawing-area {
            border-radius: 0px;
            border: solid 1px @borders;
        }
        """

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_string(self.styles)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def __interpolate_positions(self, start_pos: list[int], end_pos: list[int]) -> None:
        # Determine the tool action based on the current button pressed
        if self.left_click_ctrl.get_current_button() == 1:
            tool_action = State.toolbar.current_tool.left_click_hold
        elif self.right_click_ctrl.get_current_button() == 3:
            tool_action = State.toolbar.current_tool.right_click_hold
        else:
            return

        # Bresenham's line algorithm for interpolation between points
        x0, y0 = start_pos
        x1, y1 = end_pos
        dx: int = abs(x1 - x0)
        dy: int = abs(y1 - y0)
        sx: int = 1 if x0 < x1 else -1
        sy: int = 1 if y0 < y1 else -1
        err: int = dx - dy

        while True:
            tool_action(x0, y0)  # Apply the tool action at the current position
            if (x0 == x1) and (y0 == y1):
                break
            e2: int = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def __on_pointer_motion(self, _, x: float, y: float) -> None:
        new_pos: list[int] = [int(x // self.grid_size), int(y // self.grid_size)]
        if self.cur_pos:
            self.__interpolate_positions(
                self.cur_pos, new_pos
            )  # Interpolate positions if necessary
        self.cur_pos = new_pos  # Update the current position

        # Handle continuous left click hold
        if self.left_click_ctrl.get_current_button() == 1:
            State.toolbar.current_tool.left_click_hold(*new_pos)
        # Handle continuous right click hold
        elif self.right_click_ctrl.get_current_button() == 3:
            State.toolbar.current_tool.right_click_hold(*new_pos)
        else:
            self.drawing_area.queue_draw()  # Request a redraw of the drawing area

    def __on_pointer_leave(self, _) -> None:
        self.cur_pos = None  # Reset the current position when the pointer leaves
        self.drawing_area.queue_draw()  # Request a redraw of the drawing area

    def update_pixel(self, x: int, y: int):
        # Update the pixel data on the cached surface
        ctx = cairo.Context(self.cached_surface)
        color = self.pixel_data[y][x]
        ctx.set_source_rgba(*color)
        ctx.rectangle(
            x * self.grid_size,
            y * self.grid_size,
            self.grid_size,
            self.grid_size,
        )
        ctx.fill()
        self.drawing_area.queue_draw()

    def on_draw(
        self,
        _drawing_area: Gtk.DrawingArea,
        cr: cairo.Context,
        _width: int,
        _height: int,
    ) -> None:
        # Draw the cached surface with pixel data
        if self.cached_surface:
            cr.set_source_surface(self.cached_surface, 0, 0)
            cr.paint()

        # Draw tool overlay
        State.toolbar.current_tool.draw_overlay(cr)

        # Draw the cursor
        if self.cur_pos:
            cr.set_source_rgba(0, 0, 1, 1)
            cr.rectangle(
                self.cur_pos[0] * self.grid_size + 1,
                self.cur_pos[1] * self.grid_size + 1,
                self.grid_size - 2,
                self.grid_size - 2,
            )
            cr.stroke()
