"""
A transparent frame data display that sits on top of Tekken.exe in windowed or borderless mode.
"""


from tkinter import *
from tkinter.ttk import *
import sys
from enum import Enum
import GUI_Overlay
from GUI_Overlay import CurrentColorScheme, ColorSchemeEnum


class DataColumns(Enum):
    idX = 0
    XXCOMXX = 1
    impX = 2
    AT = 3
    BLOCK = 4
    XXHITXX = 5
    COUNTER = 6
    DM = 7
    GD = 8
    A = 9
    WHF = 10
    REC = 11
    GAP = 12
    #BSTN = 7
    #HSTN = 8
    #CSTN = 9
    NOTE = 13

    def config_name():
        return "DataColumns"

DataColumnsToMenuNames = {
    DataColumns.idX : 'internal move id number',
    DataColumns.XXCOMXX : 'best guess for input command',
    DataColumns.impX : 'the startup frames before the move becomes active',
    DataColumns.AT : 'the type of attack (low/mid/high/throw/special)',
    DataColumns.BLOCK : 'frame advantage when the move is blocked',
    DataColumns.XXHITXX : 'frame advantage when the move hits',
    DataColumns.COUNTER : 'frame advantage when the move counter hits',
    DataColumns.DM : 'the amount of damage listed for the move',
    DataColumns.GD : 'amount of guard damage inflicted on block, all characters have a starting guard health of 240 points',
    DataColumns.A : 'The number of active frames, hitting an opponent with a later active frame is not reflected in the displayed frame data',
    DataColumns.WHF: 'total number of frames in the animation',
    DataColumns.REC: 'number of frames after impact but before returning to neutral',
    DataColumns.GAP: 'number of frames between the impact of previous move and impact of this move',
    #DataColumns.BSTN : 'amount of frames before defender recovers from blocking',
    #DataColumns.HSTN : 'amount of frames before defender recovers from being hit',
    #DataColumns.CSTN : 'amount of frames before defender recovers from being counter hit',
    DataColumns.NOTE  : '???'
}

class TextRedirector(object):
    def __init__(self, stdout, widget, style, fa_p1_var, fa_p2_var):
        self.KEY = 'FDO:'
        self.NOTE = 'NOTE:'
        self.p1_note = ''
        self.p2_note = ''

        self.stdout = stdout
        self.widget = widget
        #self.fa_p1_var = fa_p1_var
        #self.fa_p2_var = fa_p2_var
        self.style = style
        self.widget.tag_config("p1", foreground=CurrentColorScheme.dict[ColorSchemeEnum.p1_text])
        self.widget.tag_config("p2", foreground=CurrentColorScheme.dict[ColorSchemeEnum.p2_text])
        self.widget.tag_config("MID", foreground=CurrentColorScheme.dict[ColorSchemeEnum.mid])
        self.widget.tag_config("HIGH", foreground=CurrentColorScheme.dict[ColorSchemeEnum.high])
        self.widget.tag_config("LOW", foreground=CurrentColorScheme.dict[ColorSchemeEnum.low])
        self.widget.tag_config("THROW", foreground=CurrentColorScheme.dict[ColorSchemeEnum.throw])
        self.columns_to_print = [True] * len(DataColumns)

        #self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_slight_minus])

    def set_columns_to_print(self, booleans_for_columns):
        self.columns_to_print = booleans_for_columns
        self.populate_column_names(booleans_for_columns)

    def populate_column_names(self, booleans_for_columns):
        column_names = ""
        for i, enum in enumerate(DataColumns):
            if booleans_for_columns[i]:
                column_names += "|{}".format(enum.name.replace('X', ' '))
        self.set_first_column(column_names)

    def set_first_column(self, first_column_string):
        self.widget.configure(state="normal")
        self.widget.delete("1.0", "2.0")
        self.widget.insert("1.0", first_column_string + '\n')
        self.widget.configure(state="disabled")


    def write(self, output_str):
        #self.stdout.write(output_str)

        lines = int(self.widget.index('end-1c').split('.')[0])
        max_lines = 5
        if lines > max_lines:
            r = lines - max_lines
            for _ in range(r):
                self.widget.configure(state="normal")
                self.widget.delete('2.0', '3.0')
                self.widget.configure(state="disabled")

        if self.KEY in output_str:

            data = output_str.split(self.KEY)[1]
            fa = output_str.split(self.KEY)[1][:3]

            '''if '?' not in fa:
                if int(fa) <= -14:
                    self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_very_punishible])
                elif int(fa) <= -10:
                    self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_punishible])
                elif int(fa) <= -5:
                    self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_safe_minus])
                elif int(fa) < 0:
                    self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_slight_minus])
                else:
                    self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_plus])'''

            text_tag = None
            if "p1:" in output_str:
                #self.fa_p1_var.set(fa)
                data = data.replace('p1:', '')
                player_text_tag = 'p1'
                note_placeholder = self.p1_note
            else:
                #self.fa_p2_var.set(fa)
                data = data.replace('p2:', '')
                player_text_tag = 'p2'
                note_placeholder = self.p2_note

            if '|' in output_str:
                out = ""

                self.widget.configure(state="normal")
                for i, col in enumerate(data.split('|')):
                    if self.columns_to_print[i]:
                        text_tag = player_text_tag
                        self.widget.insert("end", '|', text_tag)
                        if 'throw_mid' in col:
                            text_tag = 'THROW'
                            out = 'M TH'
                        elif 'mid' in col:
                            text_tag = 'MID'
                            out = 'M '
                        elif 'high' in col:
                            text_tag = 'HIGH'
                            out = 'H '
                        elif 'low' in col:
                            text_tag = 'LOW'
                            out = 'L '
                        elif 'throw' in col:
                            text_tag = 'THROW'
                            out = 'TH'
                        elif 'sl' in col:
                            text_tag = 'LOW'
                            out = 'SL'
                        elif 'sm' in col:
                            text_tag = 'MID'
                            out = 'SM'
                        else:
                            text_tag = player_text_tag
                            out = col
                        self.widget.insert("end", out, text_tag)

                out = note_placeholder + "\n"

                self.widget.insert("end", out, text_tag)

                self.widget.configure(state="disabled")
                self.widget.see('0.0')
                self.widget.yview('moveto', '.02')

        if self.NOTE in output_str:
            out = output_str.replace(self.NOTE, '')


            self.widget.configure(state="normal")
            if 'p1:' in out:
                pos = self.widget.search(self.p1_note, END, stopindex=1.0, backwards=True)
                out = out.replace('p1:', '')
            elif 'p2:' in out:
                pos = self.widget.search(self.p2_note, END, stopindex=1.0, backwards=True)
                out = out.replace('p2:', '')
            else:
                pos = None
            if pos:
                out = out.lstrip()
                self.widget.mark_set('note', pos)
                self.widget.insert('note', out)
            self.widget.configure(state="disabled")





class GUI_FrameDataOverlay(GUI_Overlay.Overlay):
    def __init__(self, master, launcher):

        GUI_Overlay.Overlay.__init__(self, master, (1000, 86), "SCUFFLE: Frame Data Overlay")


        self.launcher = launcher


        self.s = Style()
        self.s.theme_use('alt')
        self.s.configure('Overlay.TFrame', background=self.background_color)
        #self.s.configure('.', foreground=CurrentColorScheme.dict[ColorSchemeEnum.advantage_text])

        Grid.columnconfigure(self.toplevel, 0, weight=0)
        Grid.columnconfigure(self.toplevel, 1, weight=0)
        Grid.columnconfigure(self.toplevel, 2, weight=0)
        Grid.columnconfigure(self.toplevel, 3, weight=1)
        Grid.columnconfigure(self.toplevel, 4, weight=0)
        Grid.columnconfigure(self.toplevel, 5, weight=0)
        Grid.columnconfigure(self.toplevel, 6, weight=0)
        Grid.rowconfigure(self.toplevel, 0, weight=1)
        Grid.rowconfigure(self.toplevel, 1, weight=0)

        self.s.configure('Overlay.TFrame', background=self.tranparency_color)
        #self.fa_p1_var, fa_p1_label = self.create_frame_advantage_label(1)
        #self.fa_p2_var, fa_p2_label = self.create_frame_advantage_label(5)

        self.l_margin = self.create_padding_frame(0)
        self.r_margin = self.create_padding_frame(6)
        self.l_seperator = self.create_padding_frame(2)
        self.r_seperator = self.create_padding_frame(4)

        self.text = self.create_textbox(3)

        self.stdout = sys.stdout
        self.redirector = TextRedirector(self.stdout, self.text, self.s, None, None)
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")

        #self.redirector.populate_column_names(self.get_data_columns())
        self.redirector.set_columns_to_print(self.get_data_columns())

        self.text.configure(state="disabled")

    def get_data_columns(self):
        booleans_for_columns = []
        for enum in DataColumns:
            bool = self.tekken_config.get_property(DataColumns.config_name(), enum.name, True)
            booleans_for_columns.append(bool)
        return booleans_for_columns

    def create_padding_frame(self, col):
        padding = Frame(self.toplevel, width=10, style='Overlay.TFrame')
        padding.grid(row=0, column=col, rowspan=2, sticky=N + S + W + E)
        return padding

    def create_live_recovery(self, parent, col):
        live_recovery_var = StringVar()
        live_recovery_var.set('??')
        live_recovery_label = Label(parent, textvariable=live_recovery_var, font=("Segoe UI", 12), width=5, anchor='c')
        #live_recovery_label.grid(row=0, column=col, sticky =S+W)
        live_recovery_label.place(rely=0.0, relx=0.0, x=4, y=4, anchor=NW)
        return live_recovery_var

    def create_frame_advantage_label(self, col):
        frame_advantage_var = StringVar()
        frame_advantage_var.set('?')
        frame_advantage_label = Label(self.toplevel, textvariable=frame_advantage_var, font=("Consolas", 44), width=4, anchor='c',
                                        borderwidth=4, relief='ridge')
        frame_advantage_label.grid(row=0, column=col)
        return frame_advantage_var, frame_advantage_label

    def create_attack_type_label(self, col):
        attack_type_var = StringVar()
        attack_type_var.set('?')
        attack_type_label = Label(self.toplevel, textvariable=attack_type_var, font=("Verdana", 12), width=10, anchor='c',
                                    borderwidth=4, relief='ridge')
        attack_type_label.grid(row=1, column=col)
        return attack_type_var

    def create_textbox(self, col):
        textbox = Text(self.toplevel, font=("Consolas", 14), wrap=NONE, highlightthickness=0, pady=0, relief='flat')
        textbox.grid(row=0, column=col, rowspan=2, sticky=N + S + W + E)
        textbox.configure(background=self.background_color)
        textbox.configure(foreground=CurrentColorScheme.dict[ColorSchemeEnum.system_text])
        return textbox


    def update_state(self):
        pass
        #GUI_Overlay.Overlay.update_state(self)
        '''if self.show_live_framedata:
            if len(self.launcher.gameState.stateLog) > 1:
                l_recovery = str(self.launcher.gameState.GetOppFramesTillNextMove() - self.launcher.gameState.GetBotFramesTillNextMove())
                r_recovery = str(self.launcher.gameState.GetBotFramesTillNextMove() - self.launcher.gameState.GetOppFramesTillNextMove())
                if not '-' in l_recovery:
                    l_recovery = '+' + l_recovery
                if not '-' in r_recovery:
                    r_recovery = '+' + r_recovery
                self.l_live_recovery.set(l_recovery)
                self.r_live_recovery.set(r_recovery)'''


    def set_columns_to_print(self, columns_to_print):
        self.redirector.set_columns_to_print(columns_to_print)

    def update_column_to_print(self, enum, value):
        self.tekken_config.set_property(DataColumns.config_name(), enum.name, value)
        self.write_config_file()