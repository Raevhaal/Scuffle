from tkinter import *
from tkinter.ttk import *

import time

import GameplayEnums
import _GameStateManager

class GUI_MoveIdMeter:
    FRAMES = 100

    p1_symbols = {
        0: '+',
        1: '*',
        2: '.',
        3: '#',
        4: '^',
        5: '&',
        6: '@',
        7: '~',

    }

    '''tag_colors = {
        0: '#555555',
        1: '#777777',
        2: '#999999',
        3: '#bbbbbb',
        4: '#dddddd',
        5: '#666666',
        6: '#888888',
    }'''

    tag_colors = {
        0: '#FFAAAA',
        1: '#FFFFAA',
        2: '#90EE90',
        3: '#ADD8E6',
        4: '#CCCCCC',
        5: '#FF89D2',
        6: '#E5AC67',
        7: '#9BFFFF',
    }


    p2_symbols = {
        0: 'A',
        1: 'B',
        2: 'C',
        3: 'D',
        4: 'E',
        5: 'F',
        6: 'G',
        7: 'F',

    }


    def __init__(self, master):
        self.master = master
        #self.master.geometry(str(1550) + 'x' + str(250))
        master.title("SCUFFLE Move-Id-Ometer")
        master.attributes("-topmost", True)
        master.iconbitmap('Data/icon.ico')

        guide_font = ("Consolas", 12)
        label_font = ("Consolas", 8)

        self.style = Style()
        self.style.configure('MoveIdOmeter.TFrame', background='black')

        self.ometer_frame = Frame(self.master)
        self.ometer_frame.pack()

        self.p1_text = Text(self.ometer_frame, font=guide_font, width=GUI_MoveIdMeter.FRAMES, height = 1)
        self.p2_text = Text(self.ometer_frame, font=guide_font, width=GUI_MoveIdMeter.FRAMES, height=1)

        self.frames_guide = Text(self.ometer_frame, font=guide_font, width=GUI_MoveIdMeter.FRAMES, height=1)

        self.p1_key = Text(self.ometer_frame, font=guide_font, width=10, height=len(GUI_MoveIdMeter.p1_symbols))
        self.p2_key = Text(self.ometer_frame, font=guide_font, width=10, height=len(GUI_MoveIdMeter.p2_symbols))

        self.p1_buttons = Text(self.ometer_frame, font=guide_font, width=GUI_MoveIdMeter.FRAMES, height=1)
        self.p2_buttons = Text(self.ometer_frame, font=guide_font, width=GUI_MoveIdMeter.FRAMES, height=1)
        self.p1_directions = Text(self.ometer_frame, font=guide_font, width=GUI_MoveIdMeter.FRAMES, height=1)
        self.p2_directions = Text(self.ometer_frame, font=guide_font, width=GUI_MoveIdMeter.FRAMES, height=1)

        self.selection_var = StringVar()
        self.selection_var.set('000 Frames Selected')
        self.selection_label = Label(self.ometer_frame, font=guide_font, textvariable=self.selection_var)


        self.p1_dir_label = Label(self.ometer_frame, font=label_font, text="Dir")
        self.p1_but_label = Label(self.ometer_frame, font=label_font, text="But")
        self.p1_id_label = Label(self.ometer_frame, font=label_font, text="Id")

        self.p2_dir_label = Label(self.ometer_frame, font=label_font, text="Dir")
        self.p2_but_label = Label(self.ometer_frame, font=label_font, text="But")
        self.p2_id_label = Label(self.ometer_frame, font=label_font, text="Id")


        self.p1_directions.grid(sticky=S, row=0, column=2)
        self.p1_buttons.grid(sticky = S, row = 1, column = 2)
        self.p1_text.grid(sticky = S, row = 2, column = 2)

        self.frames_guide.grid(row=3, column=2)

        self.p2_text.grid(sticky = N,row = 4, column = 2)
        self.p2_buttons.grid(sticky=N, row=5, column=2)
        self.p2_directions.grid(sticky=N, row=6, column=2)

        self.selection_label.grid(row=7, column=2)

        self.p1_key.grid(row=0, column = 0, rowspan=8)
        self.p2_key.grid(row=0, column=3, rowspan=8)

        self.p1_dir_label.grid(row=0, column = 1)
        self.p1_but_label.grid(row=1, column=1)
        self.p1_id_label.grid(row=2, column=1)

        self.p2_id_label.grid(row=4, column=1)
        self.p2_but_label.grid(row=5, column=1)
        self.p2_dir_label.grid(row=6, column=1)



        self.current_frame = -1

        self.p1_counter = 1
        self.p2_counter = 1

        self.p1_keymap = {}
        self.p2_keymap = {}
        for i in range(len(GUI_MoveIdMeter.p1_symbols)):
            self.p1_keymap[i] = -1
            self.p2_keymap[i] = -1

        guide_text = ''
        for i in range(GUI_MoveIdMeter.FRAMES):
            if i % 5 == 0:
                guide_text += '|'
            elif i == 96:
                guide_text += 'N'
            elif i == 97:
                guide_text += 'O'
            elif i == 98:
                guide_text += 'W'
            elif (i + 3) % 5 == 0:
                if (i + 3) == 5:
                    guide_text += '0'
                else:
                    guide_text += str(i + 3)[0]
            elif (i + 2) % 5 == 0:
                if (i + 2) == 5:
                    guide_text += '5'
                else:
                    guide_text += str(i + 2)[1]
            else:
                guide_text += '.'

        self.frames_guide.insert(END, guide_text)

        for i, tag_color in GUI_MoveIdMeter.tag_colors.items():
            self.p1_text.tag_config(str(i), background=tag_color)
            self.p2_text.tag_config(str(i), background=tag_color)
            self.p1_key.tag_config(str(i), background=tag_color)
            self.p2_key.tag_config(str(i), background=tag_color)

        self.p1_current_move_ids = {}
        self.p2_current_move_ids = {}


    def update_meter(self, game_state:_GameStateManager.GameStateManager):

        try:
            highest_selection = max(len(self.p1_text.selection_get()), len(self.p2_text.selection_get()))
            self.selection_var.set('{:03} Frames Selected'.format(highest_selection))
        except:
            pass

        if self.current_frame != game_state.game_reader.timer:
            missing_frames = min(GUI_MoveIdMeter.FRAMES, game_state.game_reader.timer - self.current_frame)
            old_frame = self.current_frame
            self.current_frame = game_state.game_reader.timer

            #print(game_state.game_reader.timer)
            last_x_frames = missing_frames
            if len(game_state.game_reader.snapshots) > last_x_frames:

                prev_p1_move_id = -1
                prev_p2_move_id = -1
                size = len(self.p1_text.get('1.0', END))
                if size > GUI_MoveIdMeter.FRAMES:
                    delete_index = size - GUI_MoveIdMeter.FRAMES + missing_frames

                    self.p1_text.delete(1.0, '1.{}'.format(missing_frames))
                    self.p2_text.delete(1.0, '1.{}'.format(missing_frames))
                    self.p1_directions.delete(1.0, '1.{}'.format(missing_frames))
                    self.p1_buttons.delete(1.0, '1.{}'.format(missing_frames))
                    self.p2_directions.delete(1.0, '1.{}'.format(missing_frames))
                    self.p2_buttons.delete(1.0, '1.{}'.format(missing_frames))

                if self.current_frame < old_frame:
                    self.p1_text.delete(1.0, END)
                    self.p2_text.delete(1.0, END)
                    self.p1_directions.delete(1.0, END)
                    self.p1_buttons.delete(1.0, END)
                    self.p2_directions.delete(1.0, END)
                    self.p2_buttons.delete(1.0, END)



                i = -1

                for target_frame in range(self.current_frame, self.current_frame - last_x_frames, -1):
                    snapshot = game_state.game_reader.snapshots[i]
                    if (target_frame != snapshot.timer):
                        #print('missing {}'.format(target_frame))
                        self.p1_text.insert(END, ' ')
                        self.p2_text.insert(END, ' ')

                        self.p1_buttons.insert(END, ' ')
                        self.p2_buttons.insert(END, ' ')

                        self.p1_directions.insert(END, ' ')
                        self.p2_directions.insert(END, ' ')

                    else:
                        i -= 1
                        p1_move_id = snapshot.p1.movement_block.movelist_id
                        p2_move_id = snapshot.p2.movement_block.movelist_id
                        if p1_move_id != prev_p1_move_id:
                            prev_p1_move_id = p1_move_id
                            found_key = False
                            for key, value in self.p1_keymap.items():
                                if value == p1_move_id:
                                    self.p1_counter = key
                                    found_key = True
                                    break
                            if not found_key:
                                self.p1_counter += 1
                                self.p1_counter = self.p1_counter % len(GUI_MoveIdMeter.p1_symbols)
                                self.p1_keymap[self.p1_counter] = p1_move_id
                                self.p1_key.delete(1.0, END)
                                for x, y in self.p1_keymap.items():
                                    self.p1_key.insert(END, '{}: {}\n'.format(GUI_MoveIdMeter.p1_symbols[x], y), str(x))

                        if p2_move_id != prev_p2_move_id:
                            prev_p2_move_id = p2_move_id
                            found_key = False
                            for key, value in self.p2_keymap.items():
                                if value == p2_move_id:
                                    self.p2_counter = key
                                    found_key = True
                                    break
                            if not found_key:
                                self.p2_counter += 1
                                self.p2_counter = self.p2_counter % len(GUI_MoveIdMeter.p2_symbols)
                                self.p2_keymap[self.p2_counter] = p2_move_id
                                self.p2_key.delete(1.0, END)
                                for x, y in self.p2_keymap.items():
                                    self.p2_key.insert(END, '{}: {}\n'.format(GUI_MoveIdMeter.p2_symbols[x], y), str(x))


                        p1_move_id_string = GUI_MoveIdMeter.p1_symbols[self.p1_counter]
                        p2_move_id_string = GUI_MoveIdMeter.p2_symbols[self.p2_counter]

                        self.p1_text.insert(END, p1_move_id_string, str(self.p1_counter))
                        self.p2_text.insert(END, p2_move_id_string, str(self.p2_counter))


                        p1_button = snapshot.p1.global_block.input_code_button
                        p1_direction = snapshot.p1.global_block.input_code_direction

                        p2_button = snapshot.p2.global_block.input_code_button
                        p2_direction = snapshot.p2.global_block.input_code_direction

                        self.p1_buttons.insert(END, GameplayEnums.ReadInputButtonCode(p1_button))
                        self.p2_buttons.insert(END, GameplayEnums.ReadInputButtonCode(p2_button))

                        self.p1_directions.insert(END, GameplayEnums.ReadInputDirectionCode(p1_direction))
                        self.p2_directions.insert(END, GameplayEnums.ReadInputDirectionCode(p2_direction))


















if __name__ == '__main__':
    root = Tk()
    my_gui = GUI_MoveIdMeter(root)
    #root.mainloop()
    #launcher = SoulCaliburGameState.SC6GameReader()
    launcher = _GameStateManager.GameStateManager()
    counter = 0
    while (True):
        counter += 1
        launcher.Update(False, False)

        root.update_idletasks()
        root.update()

        #if counter % 10 == 0:
        my_gui.update_meter(launcher)

        time.sleep(.005)