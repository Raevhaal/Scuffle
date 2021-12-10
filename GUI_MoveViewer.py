import os
from tkinter import *
from tkinter.ttk import *
import tkinter.font as tkf
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import MovelistParser

class GUI_MoveViewer:

    DISTINCT_COLORS = [
        '#e6194b',
        '#3cb44b',
        '#ffe119',
        '#4363d8',
        '#f58231',
        '#911eb4',
        '#46f0f0',
        '#f032e6',
        '#bcf60c',
        '#fabebe',
        '#008080',
        '#e6beff',
        '#9a6324',
        '#fffac8',
        '#800000',
        '#aaffc3',
        '#808000',
        '#ffd8b1',
        '#000075',
        '#808080',
        '#ffffff',
        '#000000'
    ]

    def __init__(self, master):
        self.master = master
        #self.master.geometry(str(1850) + 'x' + str(990))
        master.title("SCUFFLE Move Viewer")
        master.iconbitmap('Data/icon.ico')
        s = Style()
        bold_label_font = 'Consolas 10 bold'

        self.do_inject_movelist = False

        self.movelist_name_var = StringVar()
        self.movelist_name_var.set('???')

        self.main_window = Frame(master)
        self.main_window.pack()

        s.configure('Loader.TFrame', background='#D1D1D1')
        s.configure('TNotebook.Tab', font='Consolas 14')

        loader_frame = Frame(self.main_window, style='Loader.TFrame')
        loader_frame.grid(sticky=N+W, row = 0, column=0)

        loader_frame_top = Frame(loader_frame)
        loader_frame_bot = Frame(loader_frame)
        loader_frame_hit = Frame(loader_frame)
        loader_frame_clip = Frame(loader_frame)
        loader_frame_tools = Frame(loader_frame)

        loader_frame_top.grid(sticky=N + E + W, row=0, column=0, padx=5, pady=5)
        loader_frame_bot.grid(sticky=N + E + W, row=1, column=0, padx=5, pady=5)
        loader_frame_hit.grid(sticky=N + E + W, row=2, column=0, padx=5, pady=5)
        loader_frame_clip.grid(sticky=N + E + W, row=3, column=0, padx=5, pady=5)
        loader_frame_tools.grid(sticky=N + E + W, row=4, column=0, padx=5, pady=5)

        self.movelist_menu_label = Label(loader_frame_top, text="Movelist", font=bold_label_font)
        self.movelist_menu_label.pack()


        self.label = Label(loader_frame_top, textvariable=self.movelist_name_var)
        self.label.pack()

        self.load_movelist_button = Button(loader_frame_top, text="Load Movelist", command=lambda: self.load_movelist_dialog())
        self.load_movelist_button.pack()

        self.save_movelist_button = Button(loader_frame_top, text="Save Movelist", command=lambda: self.save_movelist_dialog())
        self.save_movelist_button.pack()

        self.save_movelist_button = Button(loader_frame_top, text="Inject Movelist", command=lambda: self.inject_movelist_dialog())
        self.save_movelist_button.pack()

        #display_frame = Frame(self.main_window)
        display_frame = Notebook(self.main_window)
        display_frame.grid(sticky=S + E + W, row = 0, column = 1)

        move_frame = Frame(display_frame)
        hitbox_frame = Frame(display_frame)
        cancel_frame = Frame(self.main_window)

        display_frame.add(move_frame, text='Move')
        display_frame.add(hitbox_frame, text='Attack')
        display_frame.add(cancel_frame, text = 'Scripting')

        move_id_entry_container = Frame(loader_frame_bot)
        move_id_entry_container.grid(row=0, column=0)

        move_id_frame_label = Label(move_id_entry_container, text="Move Id", font=bold_label_font)
        move_id_frame_label.pack()

        self.move_id_textvar = StringVar()
        self.move_id_textvar.set('-')
        self.move_id_label = Label(move_id_entry_container, textvariable=self.move_id_textvar, font = bold_label_font)
        self.move_id_label.pack()

        move_id_label_container = Frame(move_id_entry_container)
        move_id_label_container.pack()

        move_id_entry = Entry(move_id_label_container)
        move_id_entry.bind('<Return>', lambda x: self.load_moveid(move_id_entry.get()))

        self.load_button = Button(move_id_entry_container, text="Load", command=lambda: self.load_moveid(move_id_entry.get()))
        self.load_button.pack()

        next_move_id_button = Button(move_id_label_container, text=">", width = 1, command=lambda: self.next_move_id_command())
        prev_move_id_button = Button(move_id_label_container, text="<", width = 1, command=lambda: self.prev_move_id_command())

        next_move_id_button.grid(row=0, column=2)
        move_id_entry.grid(row=0, column=1)
        prev_move_id_button.grid(row=0, column=0)

        s.configure('Save.TButton', font='Consolas 14 bold')
        save_move = Button(move_id_entry_container, text="Save Changes", style='Save.TButton', command=lambda: self.save_move_bytes_command())
        save_move.pack()

        self.move_pair= ScrolledTextPair(move_frame, (12, 32), 24, True)
        self.move_pair.grid(sticky=W, row=0, column=1)
        self.move_raw = self.move_pair.left
        self.move_intr = self.move_pair.right

        hitbox_frame_header = Frame(loader_frame_hit)
        hitbox_frame_header.pack()

        hitbox_frame_label = Label(hitbox_frame_header, text="Attacks", font=bold_label_font)
        hitbox_frame_label.pack()

        self.hitbox_index = 0
        self.hitboxes_data = []

        self.hitbox_index_var = StringVar()
        self.hitbox_index_var.set('0/0')

        self.hitbox_id_var = StringVar()
        self.hitbox_id_var.set('-')

        hitbox_iterator_frame = Frame(hitbox_frame_header)
        next_hitbox_button = Button(hitbox_iterator_frame, text=">", width=1, command=lambda: self.next_hitbox_command())
        prev_hitbox_button = Button(hitbox_iterator_frame, text="<", width=1, command=lambda: self.prev_hitbox_command())
        hitbox_label = Label(hitbox_iterator_frame, textvariable = self.hitbox_index_var)
        hitbox_id_label = Label(hitbox_frame_header, textvariable=self.hitbox_id_var, font=bold_label_font)

        #hitbox_iterator_frame.grid_columnconfigure(1, weight=1)
        prev_hitbox_button.grid(sticky=N, row=0, column=0)
        hitbox_label.grid(sticky=N+E+W, row=0, column=1)
        next_hitbox_button.grid(sticky=N, row = 0, column=2)

        hitbox_id_label.pack()
        hitbox_iterator_frame.pack()

        self.hitbox_pair = ScrolledTextPair(hitbox_frame, (18, 32), 36, True)
        self.hitbox_pair.grid(sticky=W, row=0, column=1)
        self.hitbox_raw = self.hitbox_pair.left
        self.hitbox_intr = self.hitbox_pair.right

        self.cancel_pair = ScrolledTextPair(cancel_frame, (70, 50), 40, add_canvas=True)
        self.cancel_pair.grid(sticky=N + W, row = 0, column = 1)

        self.cancel_raw = self.cancel_pair.left

        self.cancel_intr = self.cancel_pair.right
        self.cancel_intr.tag_configure("bold", font="Helvetica 9 bold")
        self.cancel_intr.tag_configure("soulcharge", font="Helvetica 9 bold", foreground='#2C75FF')

        clipboard_label = Label(loader_frame_clip, text="Cheat Engine", font = bold_label_font)
        clipboard_label.grid(sticky=N+W+E, row=0, column=0)

        clipboard_move_button = Button(loader_frame_clip, text="Copy Move to Clipboard", command=lambda: GUI_MoveViewer.copy_to_clipboard_and_strip(self.move_raw.get('1.0', END)))
        clipboard_move_button.grid(sticky=N + W + E, row=1, column=0)

        clipboard_hitbox_button = Button(loader_frame_clip, text="Copy Hitbox to Clipboard", command=lambda: GUI_MoveViewer.copy_to_clipboard_and_strip(self.hitbox_raw.get('1.0', END)))
        clipboard_hitbox_button.grid(sticky=N + W + E, row=2, column=0)

        clipboard_cancel_button = Button(loader_frame_clip, text="Copy Scripting to Clipboard", command=lambda: GUI_MoveViewer.copy_to_clipboard_and_strip(self.cancel_raw.get('1.0', END)))
        clipboard_cancel_button.grid(sticky=N + W + E, row=3, column=0)

        tool_label = Label(loader_frame_tools, text="Tools", font=bold_label_font)
        tool_label.pack()

        hex_to_dec = Frame(loader_frame_tools)
        hex_to_dec.pack()
        self.tool_hex_string = StringVar()
        self.tool_dec_string = StringVar()
        self.tool_hex_string.set('0xff')
        self.tool_dec_string.set('255')
        self.tool_hex_string.trace('w', self.hex_to_dec)
        self.tool_dec_string.trace('w', self.dec_to_hex)

        tool_hex = Entry(hex_to_dec, textvariable=self.tool_hex_string, width=10)
        tool_dec = Entry(hex_to_dec, textvariable=self.tool_dec_string, width=10)
        tool_hex.grid(row=0, column=0)
        tool_dec.grid(row=0, column=1)

        tool_hex_label = Label(hex_to_dec, text='HEX')
        tool_dec_label = Label(hex_to_dec, text='DEC')
        tool_hex_label.grid(row=1, column=0)
        tool_dec_label.grid(row=1, column=1)

        encode_to_decode = Frame(loader_frame_tools)
        encode_to_decode.pack()
        self.tool_decode_string = StringVar()
        self.tool_encode_string= StringVar()
        self.tool_decode_string.trace('w', self.encode)
        self.tool_encode_string.trace('w', self.decode)
        self.tool_decode = Entry(encode_to_decode, textvariable=self.tool_decode_string, width=10)
        self.tool_encode = Entry(encode_to_decode, textvariable=self.tool_encode_string, width=10)
        self.tool_encode.grid(row=0, column=0)
        self.tool_decode.grid(row=0, column=1)

        tool_encode_label = Label(encode_to_decode, text='Encoded')
        tool_decode_label = Label(encode_to_decode, text='Decoded')
        tool_encode_label.grid(row=1, column=0)
        tool_decode_label.grid(row=1, column=1)



    def hex_to_dec(self, *args):
        try:
            i = int(self.tool_hex_string.get(), 16)
            self.tool_dec_string.set(i)
        except:
            pass

    def dec_to_hex(self, *args):
        try:
            i = int(self.tool_dec_string.get(), 10)
            self.tool_hex_string.set(hex(i))
        except:
            pass

    def decode(self, *args):
        try:
            if self.master.focus_get() != self.tool_decode:
                i = int(self.tool_encode_string.get(), 16)
                i = MovelistParser.decode_move_id(i, self.movelist)
                self.tool_decode_string.set(hex(i))
        except:
            pass

    def encode(self, *args):
        try:
            if self.master.focus_get() != self.tool_encode:
                i = int(self.tool_decode_string.get(), 16)
                i = MovelistParser.encode_move_id(i, self.movelist)
                self.tool_encode_string.set(hex(i))
        except:
            pass


    def load_movelist(self, path):
        try:
            self.movelist = MovelistParser.Movelist.from_file(path)
            self.movelist_name_var.set(self.movelist.name)
        except Exception as e:
            print(e)

    def set_movelist(self, movelist):
        self.movelist = movelist
        self.movelist_name_var.set(self.movelist.name)


    def save_move_bytes_command(self):

        move = self.movelist.all_moves[int(self.move_id_textvar.get())]
        move_successful = self.text_entry_to_bytes(self.move_raw, move, MovelistParser.Move.LENGTH)

        hitbox_successful = True
        if self.hitbox_index >= 0:
            if len(move.attacks) > 0:
                attack = move.attacks[self.hitbox_index]
                hitbox_successful = self.text_entry_to_bytes(self.hitbox_raw, attack, MovelistParser.Attack.LENGTH)
                if hitbox_successful:
                    self.hitbox_pair.highlight_blue()
                else:
                    self.hitbox_pair.highlight_red()


        cancel = move.cancel
        cancel_successful = self.text_entry_to_bytes(self.cancel_raw, cancel, 0)

        if move_successful:
            self.move_pair.highlight_blue()
        else:
            self.move_pair.highlight_red()

        if cancel_successful:
            self.cancel_pair.highlight_blue()
        else:
            self.cancel_pair.highlight_red()

        if move_successful and hitbox_successful and cancel_successful:
            self.inject_movelist_dialog()

    def text_entry_to_bytes(self, text_widget, modified, bytes_length):
        raw = text_widget.get(1.0, END)
        raw = raw.replace('\n', '').replace(' ', '')
        move_length = bytes_length * 2
        try:
            _ = int(raw, 16)
            if move_length > 0:
                if len(raw) != move_length:
                    raise AssertionError()

            b = []
            for i in range(0, len(raw), 2):
                b.append(int(raw[i:i + 2], 16))
            modified_bytes = bytes(b)
            modified.modified_bytes = modified_bytes
            return True
        except Exception as e:
            print(e)
            return False

    def next_hitbox_command(self):
        self.hitbox_index += 1
        if self.hitbox_index >= len(self.hitboxes_data):
            self.hitbox_index = 0
        self.load_hitbox()

    def prev_hitbox_command(self):
        self.hitbox_index -= 1
        if self.hitbox_index < 0:
            self.hitbox_index = 0
        self.load_hitbox()

    def next_move_id_command(self):
        self.load_moveid(int(self.move_id_textvar.get()) + 1)

    def prev_move_id_command(self):
        self.load_moveid(int(self.move_id_textvar.get()) - 1)

    def load_moveid(self, move_id, is_encoded=False):
        try:
            id = int(move_id)
        except:
            print('unrecognized move_id: {}'.format(move_id))
            return

        if is_encoded:
            id = MovelistParser.decode_move_id(id, self.movelist)

        if id < len(self.movelist.all_moves) and id >= 0:
            self.move_id_textvar.set('{}'.format(id))
            move = self.movelist.all_moves[id]

            bytes, guide = move.get_gui_guide()

            raw, intr = self.apply_guide(bytes, guide)

            self.move_raw.delete(1.0, END)
            self.move_raw.insert(END, raw)

            self.move_intr.delete(1.0, END)
            self.move_intr.insert(END, intr)

            self.hitbox_index = 0
            self.hitboxes_data = []

            for i, attack in enumerate(move.attacks):
                bytes, guide = attack.get_gui_guide()
                raw, intr = self.apply_guide(bytes, guide)
                self.hitboxes_data.append((raw, intr, move.attack_indexes[i]))
            self.load_hitbox()

            cancel_guide, goto_line_to_line = move.cancel.get_gui_guide()
            #for bytes in cancel_guide:

            raw = ''
            intr = ''
            for bytes, desc in cancel_guide:
                raw = '{}{}\n'.format(raw, bytes)
                intr = '{}{}\n'.format(intr, desc)


            self.cancel_raw.delete(1.0, END)
            self.cancel_raw.insert(END, raw)
            self.cancel_intr.delete(1.0, END)
            self.cancel_intr.insert(END, intr)

            highlight_tag_and_remove(self.cancel_intr, '<sc>', 'soulcharge')
            highlight_tag_and_remove(self.cancel_intr, '<b>', 'bold')


            self.move_pair.highlight_gray()
            self.hitbox_pair.highlight_gray()
            self.cancel_pair.highlight_gray()

            if self.cancel_pair.canvas != None:
                canvas = self.cancel_pair.canvas
                canvas.delete(ALL)
                h = self.cancel_pair.font_height
                #canvas.config(width = (len(goto_line_to_line) + 2) * 4)
                #canvas.config(width=60)
                canvas.configure(scrollregion=(0, 0, 0, h * len(cancel_guide)))
                i = 0
                lanes = [-1] * len(GUI_MoveViewer.DISTINCT_COLORS)
                for x, y in goto_line_to_line:
                    my_lane = 0 #if we don't find a lane (unlikely) it all just kinda breaks
                    for j, lane in enumerate(lanes):
                        if x > lane:
                            my_lane = j
                            break
                    lanes[my_lane] = y #reserving lane until we're done

                    canvas.create_rectangle(2 + my_lane*4, (h * x) - (h/2), 2 + (my_lane*4) + 2, (h * (y + 1)) - (h/2), fill=GUI_MoveViewer.DISTINCT_COLORS[my_lane], outline='black')
                    i += 1


    def load_hitbox(self):
        i = self.hitbox_index
        if len(self.hitboxes_data) == 0:
            self.hitbox_raw.delete(1.0, END)
            self.hitbox_intr.delete(1.0, END)
        elif i < len(self.hitboxes_data):
            self.hitbox_raw.delete(1.0, END)
            self.hitbox_raw.insert(END, self.hitboxes_data[i][0])

            self.hitbox_intr.delete(1.0, END)
            self.hitbox_intr.insert(END, self.hitboxes_data[i][1])
        self.update_hitbox_var()

    def update_hitbox_var(self):
        self.hitbox_index_var.set('{}/{}'.format(self.hitbox_index + 1, len(self.hitboxes_data)))
        if len(self.hitboxes_data) > 0:
            self.hitbox_id_var.set('{}'.format(self.hitboxes_data[self.hitbox_index][2]))
        else:
            self.hitbox_id_var.set('-')

    def load_movelist_dialog(self):
        #Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing

        filename = askopenfilename(initialdir = '{}/{}'.format(os.getcwd(), '/movelists'))  # show an "Open" dialog box and return the path to the selected file
        self.load_movelist(filename)

    def save_movelist_dialog(self):
        filename = asksaveasfilename(defaultextension=".sc6_movelist")
        if filename == '':
            return
        else:
            with open(filename, 'wb') as fw:
                fw.write(self.movelist.generate_modified_movelist_bytes())

    def inject_movelist_dialog(self):
        self.do_inject_movelist = True

    def apply_guide(self, bytes, guide):
        raw = ''
        intr = ''
        for start, stop, func, info in guide:
            slice = bytes[start:stop]
            raw += ('{}\n'.format(MovelistParser.Movelist.bytes_as_string(slice)))
            try:
                intr += ('{} : {}\n'.format(func(slice, 0), info))
            except:
                intr += 'ERROR\n'
        return raw, intr



    def copy_to_clipboard_and_strip(text):
            clip = Tk()
            clip.withdraw()
            clip.clipboard_clear()
            clip.clipboard_append(text.replace('\n', ''))
            clip.destroy()


#https://stackoverflow.com/questions/32038701/python-tkinter-making-two-text-widgets-scrolling-synchronize
class ScrolledTextPair(Frame):
    '''Two Text widgets and a Scrollbar in a Frame'''

    def __init__(self, master, width_lr, h, hide_scrollbar=False, add_canvas=False):
        Frame.__init__(self, master, width=800, height=640)


        # Creating the widgets
        self.left = Text(self, width = width_lr[0], wrap='none', height=h,  undo=True, autoseparators=True, maxundo=-1)
        self.font_height = tkf.Font(font=self.left['font']).metrics('linespace')
        self.right = Text(self, width = width_lr[1], wrap='none', height=h,  undo=True, autoseparators=True, maxundo=-1)
        self.scrollbar = Scrollbar(self)
        if not hide_scrollbar:
            self.scrollbar.pack(side=RIGHT, fill=Y)
        if add_canvas:
            #self.canvas_frame = Frame(self, width=40, height=640)
            #self.canvas_frame.pack_propagate(0)
            #self.canvas_frame.pack(side=LEFT, fill=BOTH, expand=True)
            self.canvas = Canvas(self, width=60, height = 640)
            self.canvas.configure(background='white')

            self.canvas.yview('moveto', '1.0')
            self.pack_propagate(0)
            self.canvas.pack(side=LEFT, fill=None, expand=False)
            self.pack_propagate(1)
            #self.canvas.create_rectangle(0,0, 20, 300, fill='red')

            #self.canvas.create_window((0, 0), window=self.canvas_frame, anchor='nw')

            # self.canvas.configure(scrollregion=(0,0, 40, 2000))
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        else:
            self.canvas = None

        self.left.pack(side=LEFT, fill=BOTH, expand=True)
        self.right.pack(side=LEFT, fill=BOTH, expand=True)

        #Styling
        self.left.tag_configure("odd", background="#f0f0f0")
        self.left.tag_configure("even", background="#ffffff")
        self.left.tag_configure("red", background="#ffdddd")
        self.left.tag_configure("blue", background="#ddddff")
        self.left.tag_raise('sel')

        self.right.tag_configure("odd", background="#f0f0f0")
        self.right.tag_configure("even", background="#ffffff")
        self.right.tag_raise('sel')

        # Changing the settings to make the scrolling work
        self.scrollbar['command'] = self.on_scrollbar
        self.left['yscrollcommand'] = self.on_textscroll
        self.right['yscrollcommand'] = self.on_textscroll
        if add_canvas:
            self.canvas['yscrollcommand'] = self.on_textscroll

    def on_scrollbar(self, *args):
        '''Scrolls both text widgets when the scrollbar is moved'''
        self.left.yview(*args)
        self.right.yview(*args)
        if self.canvas != None:
            self.canvas.yview(*args)


    def on_textscroll(self, *args):
        '''Moves the scrollbar and scrolls text widgets when the mousewheel
        is moved on a text widget'''
        self.scrollbar.set(*args)
        self.on_scrollbar('moveto', args[0])

    def highlight_gray(self):
        ScrolledTextPair.alternating_tags(self.left, 'odd', 'even')

    def highlight_blue(self):
        ScrolledTextPair.alternating_tags(self.left, 'blue', 'even')

    def highlight_red(self):
        ScrolledTextPair.alternating_tags(self.left, 'red', 'even')

    # https://stackoverflow.com/questions/26348989/changing-background-color-for-every-other-line-of-text-in-a-tkinter-text-box-wid
    def alternating_tags(text, even, odd):
        lastline = text.index("end-1c").split(".")[0]
        tag = odd
        for i in range(1, int(lastline)):
            for t in ('red', 'blue', 'odd', 'even'):
                text.tag_remove(t, "%s.0" % i, "%s.0" % (i + 1))
            text.tag_add(tag, "%s.0" % i, "%s.0" % (i + 1))
            tag = even if tag == odd else odd


def highlight_tag_and_remove(tw, marker, highlight):
    regex = '{}.*?{}'.format(marker, marker).replace('>', '\>').replace('<', '\<')
    highlight_pattern_in_text_widget(tw, regex, marker, highlight, regexp=True)


def highlight_pattern_in_text_widget(tw, pattern, marker, tag, start="1.0", end="end",
                      regexp=False):
    '''Apply the given tag to all text that matches the given pattern

    If 'regexp' is set to True, pattern will be treated as a regular
    expression according to Tcl's regular expression syntax.
    '''

    start = tw.index(start)
    end = tw.index(end)
    tw.mark_set("matchStart", start)
    tw.mark_set("matchEnd", start)
    tw.mark_set("searchLimit", end)

    count = IntVar()
    while True:
        index = tw.search(pattern, "matchEnd", "searchLimit",
                            count=count, regexp=regexp)
        if index == "": break
        if count.get() == 0: break  # degenerate pattern which matches zero-length strings
        tw.mark_set("matchStart", index)
        tw.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
        tw.tag_add(tag, "matchStart", "matchEnd")

        size = len(marker)

        tw.delete('{}-{}c'.format('matchEnd', size), "matchEnd")
        tw.delete("matchStart", '{}+{}c'.format('matchStart', size))


if __name__ == '__main__':
    root = Tk()
    my_gui = GUI_MoveViewer(root)
    root.mainloop()