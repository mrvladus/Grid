from gi.repository import Gtk, Adw, Xdp, Gdk  # type:ignore

from state import State
from palettes import default_palettes
from utils import Utils


class PaletteItem(Gtk.Button):
    def __init__(self, color: str) -> None:
        super().__init__()
        self.color = color
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_tooltip_text(self.color)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.add_css_class("circular")
        self.css_class = State.add_palette_item(self.color)
        self.add_css_class(self.css_class)

    def do_clicked(self):
        State.current_color = self.color
        State.palette_bar.update_color(self.css_class, self.color)


class PaletteBar(Adw.Bin):
    portal = Xdp.Portal()

    def __init__(self) -> None:
        super().__init__()
        State.palette_bar = self
        self.__build_ui()
        colors: list[str] = default_palettes["cc-29"]
        for color in colors:
            self.__add_item(color)

    def __build_ui(self) -> None:
        self.palette = Gtk.FlowBox(
            max_children_per_line=2,
            margin_top=6,
            margin_bottom=6,
            margin_end=6,
            margin_start=6,
            row_spacing=6,
        )
        color_picker_btn: Gtk.Button = Gtk.Button(
            icon_name="grid-color-picker-symbolic"
        )
        color_picker_btn.connect("clicked", self.__on_color_picker_btn_clicked)

        open_palette_btn = Gtk.Button(icon_name="grid-palette-symbolic")

        top_bar = Gtk.Box(
            css_classes=["toolbar"],
            halign=Gtk.Align.CENTER,
            hexpand=True,
        )
        top_bar.append(color_picker_btn)
        top_bar.append(open_palette_btn)

        bottom_bar = Gtk.Box(
            css_classes=["toolbar"],
            halign=Gtk.Align.CENTER,
            hexpand=True,
        )

        self.current_color = Gtk.Button(css_classes=["default-color", "pill"])
        bottom_bar.append(self.current_color)

        toolbar_view: Adw.ToolbarView = Adw.ToolbarView(
            content=Gtk.ScrolledWindow(child=self.palette, vexpand=True),
        )
        toolbar_view.add_top_bar(top_bar)
        toolbar_view.add_bottom_bar(bottom_bar)
        self.set_child(toolbar_view)

    def update_color(self, css_class: str, hex_color: str):
        self.current_color.set_css_classes(["pill", css_class])
        self.current_color.set_tooltip_text(hex_color)

    def __add_item(self, color: str) -> None:
        self.palette.append(PaletteItem(color))

    def __on_color_picker_btn_clicked(self, _):
        def __on_selected(portal: Xdp.Portal, task):
            color: Gdk.RGBA = Gdk.RGBA()
            color.red, color.green, color.blue = portal.pick_color_finish(task)
            color.alpha = 1
            color_rgba = color.to_string().strip("rgba()").split(",")
            State.set_current_solor(
                Utils.rgba_to_hex([int(c) for c in color_rgba] + [255])
            )

        self.portal.pick_color(None, None, __on_selected)
