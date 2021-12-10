from tkinter import *
from tkinter.ttk import *
import GUI_FrameDataOverlay as fdo
import GUI_Overlay as ovr
#import GUI_TimelineOverlay as tlo
#import GUI_CommandInputOverlay as cio
#import GUI_MatchStatOverlay as mso
#import GUI_DebugInfoOverlay as dio
#import GUI_PunishCoachOverlay as pco
import ConfigReader
from _GameStateManager import GameStateManager
import time
from enum import Enum
import VersionChecker
import webbrowser
import GUI_MoveViewer
import GUI_MoveIdMeter
import sys

class GUI_Main(Tk):
    def __init__(self):
        self.overlay = None

        Tk.__init__(self)
        self.wm_title("SCUFFLE")
        self.iconbitmap('Data/icon.ico')

        self.color_scheme_config = ConfigReader.ConfigReader("color_scheme")
        self.color_scheme_config.add_comment("colors with names -> http://www.science.smith.edu/dftwiki/images/3/3d/TkInterColorCharts.png")
        self.changed_color_scheme("Current", False)

        self.menu = Menu(self)
        self.configure(menu=self.menu)

        self.text = Text(self, wrap="word")
        self.stdout = sys.stdout
        self.var_print_frame_data_to_file = BooleanVar(value=False)
        sys.stdout = TextRedirector(self.text, sys.stdout, self.write_to_overlay, self.var_print_frame_data_to_file, "stdout")
        self.stderr = sys.stderr
        sys.stderr = TextRedirector(self.text, sys.stderr, self.write_to_error, "stderr")
        self.text.tag_configure("stderr", foreground="#b22222")



        try:
            with open("Data/SCUFFLE_readme.txt") as fr:
                lines = fr.readlines()
            for line in lines: print(line)
        except:
            print("Error reading readme file.")

        #Disables version checker
        updates = False
        #updates = VersionChecker.check_version()
        if updates:
            self.wm_title("SCUFFLE (Updates Available)")

        print("SCUFFLE Starting...")
        self.launcher = GameStateManager()

        self.overlay = fdo.GUI_FrameDataOverlay(self, self.launcher)
        #self.graph = tlo.GUI_TimelineOverlay(self, self.launcher)

        self.tekken_bot_menu = Menu(self.menu)
        self.tekken_bot_menu.add_command(label="Restart", command=self.restart)

        self.menu.add_cascade(label="SCUFFLE", menu=self.tekken_bot_menu)

        self.tools_menu = Menu(self.menu)
        self.move_viewer = None
        self.tools_menu.add_command(label="Launch Move Viewer", command=self.launch_move_viewer)

        self.move_id_ometer = None
        self.tools_menu.add_command(label="Launch Move-Id-Ometer", command=self.launch_move_id_ometer)

        self.do_show_all_hitbox_data = BooleanVar()
        self.do_show_all_hitbox_data.set(False)
        self.tools_menu.add_checkbutton(label='Show frame data for all hitboxes (useful for moves with \'tip\' properties)', onvalue=True, offvalue=False, variable=self.do_show_all_hitbox_data)

        self.tools_menu.add_command(label="Dump all frame data to console", command=self.dump_frame_data)

        self.do_print_debug_values = BooleanVar()
        self.do_print_debug_values.set(False)
        #self.tools_menu.add_checkbutton(label='DEBUG: Print Every Frame (WARNING: CPU USAGE HIGH)', onvalue=True, offvalue=False, variable=self.do_print_debug_values)

        self.menu.add_cascade(label="Advanced Tools", menu=self.tools_menu)





        self.checkbox_dict = {}
        self.column_menu = Menu(self.menu)
        for i, enum in enumerate(fdo.DataColumns):
            bool = self.overlay.redirector.columns_to_print[i]
            self.add_checkbox(self.column_menu, enum, "{} ({})".format(enum.name.replace('X', ' ').strip(), fdo.DataColumnsToMenuNames[enum]), bool, self.changed_columns)
        self.menu.add_cascade(label='Columns', menu=self.column_menu)

        self.display_menu = Menu(self.menu)
        for enum in ovr.DisplaySettings:
            default = self.overlay.tekken_config.get_property(ovr.DisplaySettings.config_name(), enum.name, False)
            self.add_checkbox(self.display_menu, enum, enum.name, default, self.changed_display)
        self.menu.add_cascade(label="Display", menu=self.display_menu)

        self.color_scheme_menu = Menu(self.menu)
        self.scheme_var = StringVar()
        for section in self.color_scheme_config.parser.sections():
            if section not in ("Comments", "Current"):
                self.color_scheme_menu.add_radiobutton(label=section, variable=self.scheme_var, value=section, command=lambda : self.changed_color_scheme(self.scheme_var.get()))
        self.menu.add_cascade(label="Color Scheme", menu=self.color_scheme_menu)

        self.tekken_bot_menu = Menu(self.menu)
        self.tekken_bot_menu.add_command(label=VersionChecker.CURRENT_VERSION)
        self.tekken_bot_menu.add_command(label="Check for new version", command=self.print_release_notes)
        self.tekken_bot_menu.add_command(label="Download Latest Release", command=self.download_latest_release)
        self.menu.add_cascade(label="Version", menu=self.tekken_bot_menu)


        self.text.grid(row = 2, column = 0, columnspan=2, sticky=N+S+E+W)
        #self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        #self.grid_columnconfigure(1, weight=1)

        self.geometry(str(920) + 'x' + str(720))


        self.previous_working_pid = 0
        self.update_launcher()
        #self.overlay.hide()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def print_release_notes(self):
        VersionChecker.check_version(force_print=True)


    def download_latest_release(self):
        webbrowser.open('https://github.com/rougelite/SCUFFLE/releases/')

    def restart(self):
        self.launcher = GameStateManager()
        self.stop_overlay()
        self.start_overlay()

    def write_to_overlay(self, string):
        if self.var_print_frame_data_to_file.get() and 'NOW:' in string:
            with open("Data/out.txt", 'a') as fa:
                fa.write(string +'\n')
        if self.overlay != None:
            self.overlay.redirector.write(string)
        #if 'HIT' in string:
            #self.graph.redirector.write(string)

    def write_to_error(self, string):
        self.stderr.write(string)

    def launch_move_viewer(self):
        try:
            self.old_move_id = 0
            if self.move_viewer != None:
                self.move_viewer.master.destroy()
                self.move_viewer = None
            self.move_viewer = GUI_MoveViewer.GUI_MoveViewer(Toplevel(self))
            self.move_viewer.set_movelist(self.launcher.game_reader.p1_movelist)
        except Exception as e:
            print(e)

    def dump_frame_data(self):
        try:
            self.launcher.game_reader.p1_movelist.print_all_frame_data()
        except Exception as e:
            print(e)

    def launch_move_id_ometer(self):
        if self.move_id_ometer != None:
            self.move_id_ometer.master.destroy()
            self.move_id_ometer = None
        self.move_id_ometer = GUI_MoveIdMeter.GUI_MoveIdMeter(Toplevel(self))

    def add_checkbox(self, menu, lookup_key, display_string, default_value, button_command):
        var = BooleanVar()
        var.set(default_value)
        self.checkbox_dict[lookup_key] = var
        menu.add_checkbutton(label=display_string, onvalue=True, offvalue=False, variable=var, command = button_command)

    def changed_color_scheme(self, section, do_reboot=True):
        for enum in fdo.ColorSchemeEnum:
            fdo.CurrentColorScheme.dict[enum] = self.color_scheme_config.get_property(section, enum.name, fdo.CurrentColorScheme.dict[enum])
            self.color_scheme_config.set_property("Current", enum.name, fdo.CurrentColorScheme.dict[enum])
        self.color_scheme_config.write()
        if do_reboot:
            self.reboot_overlay()

    def changed_mode(self, mode):

        self.stop_overlay()

        self.mode = OverlayMode[mode]

        if self.mode != OverlayMode.Off:
            self.start_overlay()



    def changed_columns(self):
        generated_columns = []
        for enum in fdo.DataColumns:
            var = self.checkbox_dict[enum]
            generated_columns.append(var.get())
        self.overlay.set_columns_to_print(generated_columns)

    def changed_display(self):
        for enum in ovr.DisplaySettings:
            var = self.checkbox_dict[enum]
            if self.overlay != None:
                self.overlay.tekken_config.set_property(ovr.DisplaySettings.config_name(), enum.name, var.get())
        if self.overlay != None:
            self.overlay.tekken_config.write()
        self.reboot_overlay()

    def stop_overlay(self):
        if self.overlay != None:
            self.overlay.toplevel.destroy()
        self.overlay = None

    def start_overlay(self):
        self.overlay = fdo.GUI_FrameDataOverlay(self, self.launcher)
        self.overlay.hide()

    def reboot_overlay(self):
        self.stop_overlay()
        self.start_overlay()

    def update_launcher(self):
        time1 = time.time()
        successful_update = self.launcher.Update(self.do_print_debug_values.get(), self.do_show_all_hitbox_data.get())

        if self.move_viewer != None:
            if self.launcher.p1_move_id != self.old_move_id and self.launcher.p1_move_id != 0x59: #0x59 is the hex for 'coming to a stop' move_id
                self.old_move_id = self.launcher.p1_move_id
                try:
                    self.move_viewer.load_moveid(self.launcher.p1_move_id)
                except:
                    self.move_viewer = None

            try:
                if self.move_viewer.do_inject_movelist:
                    self.launcher.game_reader.do_write_movelist = True
                    self.launcher.game_reader.p1_movelist = self.move_viewer.movelist
                    self.move_viewer.do_inject_movelist = False
            except:
                self.move_viewer = None


        if self.overlay != None:
            self.overlay.update_location()
            if successful_update:
                self.overlay.update_state()

        if self.move_id_ometer != None:
            try:
                self.move_id_ometer.update_meter(self.launcher)
            except Exception as e: #grabs window close errors (and everything else too oh god)
                self.move_id_ometer = None
                print('Move-Id-Ometer update loop : {}'.format(e))



        #self.graph.update_state()
        time2 = time.time()
        elapsed_time = 1000 * (time2 - time1)

        if self.launcher.game_reader.HasWorkingPID():
            if self.launcher.game_reader.HasNewMovelist():
                if self.move_viewer != None:
                    movelist = self.launcher.game_reader.p1_movelist
                    if movelist != None:
                        try:
                            self.move_viewer.set_movelist(movelist)
                            self.launcher.game_reader.MarkMovelistAsOld()
                        except:
                            self.move_viewer = None
                        self.previous_working_pid += 1
            else:
                self.previous_working_pid += 1

            self.after(max(2, 8 - int(round(elapsed_time))), self.update_launcher)
        else:
            self.previous_working_pid = 0
            self.after(1000, self.update_launcher)

    def on_closing(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        self.destroy()



class TextRedirector(object):
    def __init__(self, widget, stdout, callback_function, var_print_frame_data_to_file,tag="stdout"):
        self.widget = widget
        self.stdout = stdout
        self.tag = tag
        self.callback_function = callback_function
        self.var_print_frame_data_to_file = var_print_frame_data_to_file

    def write(self, str):

        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see('end')
        self.callback_function(str)

    def flush(self):
        pass

class OverlayMode(Enum):
    Off = 0
    FrameData = 1
    #Timeline = 2
    CommandInput = 3
    PunishCoach = 4
    MatchupRecord = 5
    DebugInfo = 6

OverlayModeToDisplayName = {
    OverlayMode.Off : 'Off',
    OverlayMode.FrameData: 'Frame Data',
    OverlayMode.CommandInput: 'Command Inputs (and cancel window)',
    OverlayMode.PunishCoach: 'Punish Alarm (loud!)',
    OverlayMode.MatchupRecord: 'Matchup Stats',
    OverlayMode.DebugInfo: 'Debugging Variables',
}

if __name__ == '__main__':
    app = GUI_Main()
    #app.update_launcher()
    app.mainloop()