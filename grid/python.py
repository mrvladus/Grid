import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
import cairo


class DrawingApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.DrawingApp")
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = DrawingWindow(self)
        self.window.present()


class DrawingWindow(Gtk.ApplicationWindow):
    PIXEL_SIZE = 1  # Size of each pixel

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Pixel Art App")
        self.set_default_size(800, 600)

        self.drawing_area = Gtk.DrawingArea()
        self.set_child(self.drawing_area)
        self.drawing_area.set_draw_func(self.on_draw)

        self.width_in_pixels = self.get_default_size().width // self.PIXEL_SIZE
        self.height_in_pixels = self.get_default_size().height // self.PIXEL_SIZE

        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32,
            self.width_in_pixels * self.PIXEL_SIZE,
            self.height_in_pixels * self.PIXEL_SIZE,
        )
        self.cr = cairo.Context(self.surface)
        self.cr.set_source_rgba(1, 1, 1, 0)  # Initial color is white
        self.cr.paint()

        self.previous_x = None
        self.previous_y = None

        self.init_gestures()

    def init_gestures(self):
        # Gesture for left button drag
        self.drag_left = Gtk.GestureDrag.new()
        self.drag_left.set_button(Gdk.BUTTON_PRIMARY)
        self.drag_left.connect("drag-begin", self.on_drag_begin)
        self.drag_left.connect("drag-update", self.on_drag_update)
        self.add_controller(self.drag_left)

        # Gesture for right button drag
        self.drag_right = Gtk.GestureDrag.new()
        self.drag_right.set_button(Gdk.BUTTON_SECONDARY)
        self.drag_right.connect("drag-begin", self.on_drag_begin)
        self.drag_right.connect("drag-update", self.on_drag_update)
        self.add_controller(self.drag_right)

    def on_drag_begin(self, gesture, start_x, start_y):
        self.previous_x = start_x
        self.previous_y = start_y
        self.update_pixel(gesture, start_x, start_y)

    def on_drag_update(self, gesture, offset_x, offset_y):
        _, current_x, current_y = gesture.get_point()
        self.update_pixel(gesture, current_x, current_y)

    def update_pixel(self, gesture, x, y):
        pixel_x = int(x // self.PIXEL_SIZE)
        pixel_y = int(y // self.PIXEL_SIZE)

        if 0 <= pixel_x < self.width_in_pixels and 0 <= pixel_y < self.height_in_pixels:
            if gesture.get_button() == Gdk.BUTTON_PRIMARY:
                self.cr.set_source_rgb(0, 0, 0)  # Black for left button
            elif gesture.get_button() == Gdk.BUTTON_SECONDARY:
                self.cr.set_source_rgb(1, 0, 0)  # Red for right button

            if self.previous_x is not None and self.previous_y is not None:
                prev_pixel_x = int(self.previous_x // self.PIXEL_SIZE)
                prev_pixel_y = int(self.previous_y // self.PIXEL_SIZE)
                self.draw_line(prev_pixel_x, prev_pixel_y, pixel_x, pixel_y)

            self.previous_x = x
            self.previous_y = y

        self.drawing_area.queue_draw()

    def draw_line(self, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        distance = max(abs(dx), abs(dy))
        if distance == 0:
            distance = 1  # To avoid division by zero
        x_step = dx / distance
        y_step = dy / distance
        for i in range(distance + 1):
            pixel_x = int(x0 + i * x_step)
            pixel_y = int(y0 + i * y_step)
            if (
                0 <= pixel_x < self.width_in_pixels
                and 0 <= pixel_y < self.height_in_pixels
            ):
                self.cr.rectangle(
                    pixel_x * self.PIXEL_SIZE,
                    pixel_y * self.PIXEL_SIZE,
                    self.PIXEL_SIZE,
                    self.PIXEL_SIZE,
                )
                self.cr.fill()

    def on_draw(self, area, cr, width, height):
        cr.set_source_surface(self.surface, 0, 0)
        cr.paint()


app = DrawingApp()
app.run(None)
