from gi.repository import Gtk, Adw, Gdk  # type:ignore

from shared import Box
from state import State
from palettes import default_palettes
import utils as Utils


class PaletteItem(Adw.Bin):
    def __init__(self, color: str) -> None:
        super().__init__()
        self.color = color
        self.css_class = State.palette_bar.add_palette_item(self.color)
        self.__build_ui()

    def __build_ui(self) -> None:
        self.add_css_class("palette-item")
        self.set_tooltip_text(self.color)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.add_css_class(self.css_class)

        left_click_ctrl = Gtk.GestureClick(button=1)
        left_click_ctrl.connect("released", self.__on_left_click)
        self.add_controller(left_click_ctrl)

        right_click_ctrl = Gtk.GestureClick(button=3)
        right_click_ctrl.connect("released", self.__on_right_click)
        self.add_controller(right_click_ctrl)

    def __on_left_click(self, *_):
        State.palette_bar.primary_color = self.color

    def __on_right_click(self, *_):
        State.palette_bar.secondary_color = self.color


class PaletteBar(Gtk.Box):
    __primary_color: str = "#000000ff"
    __secondary_color: str = "#00000000"

    @property
    def primary_color(self) -> str:
        return self.__primary_color

    @primary_color.setter
    def primary_color(self, new_color: str):
        self.__primary_color = new_color
        self.primary_color_btn.set_tooltip_text(new_color + " (Left Click)")
        self.primary_color_btn.set_css_classes(
            ["palette-item", self.__get_css_class_for_color(new_color)]
        )

    @property
    def secondary_color(self) -> str:
        return self.__secondary_color

    @secondary_color.setter
    def secondary_color(self, new_color: str):
        self.__secondary_color = new_color
        self.secondary_color_btn.set_tooltip_text(new_color + " (Right Click)")
        self.secondary_color_btn.set_css_classes(
            ["palette-item", self.__get_css_class_for_color(new_color)]
        )

    def __init__(self) -> None:
        super().__init__()
        State.palette_bar = self
        self.__setup_styles()
        self.__build_ui()
        colors: list[str] = default_palettes["cc-29"]
        for color in colors:
            self.__add_item(color)

    def __add_item(self, color: str) -> None:
        self.palette.append(PaletteItem(color))

    def __get_css_class_for_color(self, color: str) -> str:
        for css_class in self.styles.split("\n\n"):
            if color in css_class:
                return css_class.split("{")[0].strip(". \t")

        return self.add_palette_item(color)

    def __setup_styles(self):
        self.styles: str = """
        flowboxchild {
            all:unset;
            padding:0px;
            margin:0px;
        }

        .palette-item {
            border-radius: 9999px;
            border: solid 2px @borders;
            min-width: 30px;
            min-height: 30px;
        }

        .palette-current-color-btn {
            border: solid 2px @borders;
        }

        .default-primary-color {
            background-color: #000000ff;
        }

        .default-secondary-color {
            background-color: #00000000;
        }
        """

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_string(self.styles)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def __build_ui(self) -> None:
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.props.width_request = 100

        self.palette = Gtk.FlowBox(
            max_children_per_line=2,
            margin_top=6,
            margin_bottom=6,
            margin_end=6,
            margin_start=6,
            row_spacing=6,
            valign=Gtk.Align.START,
        )
        self.append(
            Gtk.ScrolledWindow(
                child=self.palette,
                vexpand=True,
                window_placement=Gtk.CornerType.TOP_RIGHT,
            )
        )

        self.append(Gtk.Separator())

        self.primary_color_btn = Adw.Bin()
        self.primary_color = "#000000ff"
        self.secondary_color_btn = Adw.Bin()
        self.secondary_color = "#00000000"

        self.append(
            Box(
                children=[self.primary_color_btn, self.secondary_color_btn],
                halign=Gtk.Align.CENTER,
                spacing=8,
                margin_top=6,
                margin_bottom=6,
            )
        )

    def add_palette_item(self, color: str) -> str:
        """Add new css class for color if not exists. Else return existing css class"""

        if color in self.styles:
            return self.__get_css_class_for_color(color)
        style_class = Utils.generate_random_ascii_string(30)
        self.styles += f".{style_class}{{background-color:{color};border: solid 2px @borders;}}\n\n"
        self.css_provider.load_from_string(self.styles)
        return style_class
