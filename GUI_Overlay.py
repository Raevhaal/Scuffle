"""
Our abstract overlay class provides shared tools for our overlays
"""

from ConfigReader import ConfigReader
from enum import Enum
import platform
from tkinter import *
from tkinter.ttk import *

class DisplaySettings(Enum):
    overlay_on_bottom = -1
    overlay_as_draggable_window = 0
    only_appears_when_SC6_has_focus = 1
    transparent_background = 2

    def config_name():
        return "DisplaySettings"

class ColorSchemeEnum(Enum):
    background = 0
    transparent = 1
    p1_text = 2
    p2_text = 3
    system_text = 4
    mid = 11
    high = 12
    low = 13
    throw = 14

class CurrentColorScheme:
    dict = {
        ColorSchemeEnum.background : 'gray10',
        ColorSchemeEnum.transparent: 'white',
        ColorSchemeEnum.p1_text: 'ivory2',
        ColorSchemeEnum.p2_text: 'LightSkyBlue1',
        ColorSchemeEnum.system_text: 'lawn green',
        ColorSchemeEnum.mid: '#FFEB44',
        ColorSchemeEnum.high: '#FF789A',
        ColorSchemeEnum.low: '#84C1FF',
        ColorSchemeEnum.throw: '#F29FFF',
    }

class Overlay:
    def __init__(self, master, xy_size, window_name):
        print("Launching {}".format(window_name))
        config_filename = "frame_data_overlay"
        self.tekken_config = ConfigReader(config_filename)
        is_windows_7 = 'Windows-7' in platform.platform()
        self.is_draggable_window = self.tekken_config.get_property(DisplaySettings.config_name(), DisplaySettings.overlay_as_draggable_window.name, False)
        self.is_minimize_on_lost_focus = self.tekken_config.get_property(DisplaySettings.config_name(), DisplaySettings.only_appears_when_SC6_has_focus.name, True)
        #self.is_transparency = self.tekken_config.get_property(DisplaySettings.config_name(), DisplaySettings.transparent_background.name, not is_windows_7)
        self.is_transparency = self.tekken_config.get_property(DisplaySettings.config_name(), DisplaySettings.transparent_background.name, False)
        self.is_overlay_on_top = not self.tekken_config.get_property(DisplaySettings.config_name(), DisplaySettings.overlay_on_bottom.name, False)



        self.overlay_visible = False
        if master == None:
            self.toplevel = Tk()
        else:
            self.toplevel = Toplevel()

        self.toplevel.wm_title(window_name)

        self.toplevel.attributes("-topmost", True)

        self.background_color = CurrentColorScheme.dict[ColorSchemeEnum.background]

        if self.is_transparency:
            self.tranparency_color = CurrentColorScheme.dict[ColorSchemeEnum.transparent]
            self.toplevel.wm_attributes("-transparentcolor", self.tranparency_color)
            self.toplevel.attributes("-alpha", "0.75")
        else:
            if is_windows_7:
                print("Windows 7 detected. Disabling transparency.")
            self.tranparency_color = self.background_color
        self.toplevel.configure(background=self.tranparency_color)

        self.toplevel.iconbitmap('Data/icon.ico')
        if not self.is_draggable_window:
            self.toplevel.overrideredirect(True)

        self.w = xy_size[0]
        self.h = xy_size[1]

        self.toplevel.geometry(str(self.w) + 'x' + str(self.h))


    def update_location(self):
        if not self.is_draggable_window:
            game_rect = self.launcher.game_reader.GetWindowRect()
            if game_rect != None:
                x = (game_rect.right + game_rect.left) / 2 - self.w / 2
                if self.is_overlay_on_top:
                    y = game_rect.top
                else:
                    y = game_rect.bottom - self.h - 10
                self.toplevel.geometry('%dx%d+%d+%d' % (self.w, self.h, x, y))
                if not self.overlay_visible:
                    self.show()
            else:
                if self.overlay_visible:
                    self.hide()

    def update_state(self):
        pass

    def hide(self):
        if self.is_minimize_on_lost_focus and not self.is_draggable_window:
            self.toplevel.withdraw()
            self.overlay_visible = False

    def show(self):
        self.toplevel.deiconify()
        self.overlay_visible = True

    def write_config_file(self):
        self.tekken_config.write()