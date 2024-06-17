import cairo
from gi.repository import Adw, Gtk, Gdk  # type:ignore

from state import State
import utils as Utils


class DrawingArea(Adw.Bin):
    cur_pos: list[int, int] = None  # Current position of the cursor on the grid
    prev_pos: list[int, int] = None  # Previous position of the cursor on the grid
    grid_size: int = 20  # Size of each grid cell in pixels
    canvas_size: int = 16  # Number of cells in the grid (width and height)
    pixel_data: list = []  # Stores the color data for each pixel in the grid

    def __init__(self) -> None:
        super().__init__()
        State.drawing_area = self  # Register this instance in the global state
        self.__setup_styles()  # Set up CSS styles for the drawing area
        self.__build_ui()  # Build the user interface

    def __build_ui(self) -> None:
        self.add_css_class("drawing-area-container")  # Add a CSS class to the container

        # Create the drawing area widget
        self.drawing_area: Gtk.DrawingArea = Gtk.DrawingArea(
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            css_classes=["drawing-area"],
            cursor=Gdk.Cursor(name="cell"),
        )
        # Set the size of the drawing area based on the grid size and canvas size
        self.drawing_area.set_content_width(self.canvas_size * self.grid_size)
        self.drawing_area.set_content_height(self.canvas_size * self.grid_size)
        self.drawing_area.set_draw_func(self.on_draw)

        # Initialize all pixels to transparent
        self.pixel_data = [
            [(255, 255, 255, 0)] * self.canvas_size for _ in range(self.canvas_size)
        ]

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

    def __setup_styles(self) -> None:
        self.styles: str = """
        .drawing-area {
            border-radius: 0px;
            border: solid 1px @borders;
        }
        """
        self.css_provider = Gtk.CssProvider()  # Create a CSS provider
        self.css_provider.load_from_string(self.styles)  # Load the CSS styles
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )  # Add the CSS provider to the display

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

    def on_draw(
        self,
        _drawing_area: Gtk.DrawingArea,
        cr: cairo.Context,
        _width: int,
        _height: int,
    ) -> None:
        # Draw the pixel data on the drawing area
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
                # Uncomment the following lines to draw grid lines
                # cr.set_source_rgba(0.8, 0.8, 0.8, 1)
                # cr.rectangle(
                #     x * self.grid_size,
                #     y * self.grid_size,
                #     self.grid_size,
                #     self.grid_size,
                # )
                # cr.stroke()

        # Draw overlay
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
