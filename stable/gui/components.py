##################################################################
##
## file: components.py
##
## description: provides functions and classes to create GUI components
##
## (c) 2024 Jochen Rust
##     DSI aerospace technology
##
##################################################################
import tkinter as tk

class LogField(tk.Text):
    def __init__(self, root, width, height):
        super().__init__(root, width=width, height=height, wrap='word')
        self.config(state='disabled')

    def log(self, chars, severity=None):
        self.config(state='normal')
        self.insert('end', chars, severity)
        self.config(state='disabled')

    def delete(self, index1, index2 = None):
        self.config(state='normal')
        super().delete(index1, index2)
        self.config(state='disabled')

class StatusLabel(tk.Label):
    def __init__(self, root, bg, font=None):
        super().__init__(root, bg=bg, font=font)

        self.tick = "\u2713"
        self.cross = "\u2715"
        self.bubble = "\u25ef"
        self.state = None
        self.normal()

    def negative(self):
        self.config(text=self.cross, fg='red')
        self.state = 'negative'

    def positive(self):
        self.config(text=self.tick, fg='green')
        self.state = 'positive'

    def waiting(self):
        self.config(text=self.bubble, fg='blue')
        self.state = 'waiting'

    def normal(self):
        self.config(text='-', fg='black')
        self.state = 'normal'

    def disable_if(self, states: list[str] | str):
        if isinstance(states, str):
            states = [states]

        if isinstance(states, list):
            if self.state in states:
                self.normal()

def get_frame(root: tk.Tk|tk.Frame, bg: str=None, row: int=0, rowspan: int=1, col: int=0, colspan: int=1, sticky: str=None, padx: int=0, pady: int=0, render=True, border=True):
    frame = tk.Frame(root, bg=bg)
    if render:
        frame.grid(row=row, rowspan=rowspan, column=col, columnspan=colspan, sticky=sticky, padx=padx, pady=pady)

    if border:
        frame['borderwidth'] = 3
        frame['relief'] = 'ridge'


    return frame

def get_label(root: tk.Tk|tk.Frame, text: tk.StringVar, bg: str=None, row: int=0, rowspan: int=1, col: int=0, colspan: int=1, sticky: str=None, padx: int=0, pady: int=0):
    label = tk.Label(root, bg=bg, textvariable=text)
    label.grid(row=row, rowspan=rowspan, column=col, columnspan=colspan, sticky=sticky, padx=padx, pady=pady)
    return label

def get_status_label(root: tk.Tk, bg: str=None, row: int=0, rowspan: int=1, col: int=0, colspan: int=1, sticky: str=None, padx: int=0, pady: int=0):
    label = StatusLabel(root, bg=bg)
    label.grid(row=row, rowspan=rowspan, column=col, columnspan=colspan, sticky=sticky, padx=padx, pady=pady)
    return label

#type of root should be SorngenApp, causes circular import
def get_button(root: tk.Tk | tk.Frame, text: tk.StringVar, command: callable, row: int, col: int, sticky: str = 'nsew',
               rowspan: int = 1,
               columnspan: int = 1,
               padx: int | tuple[int, int] = 5,
               pady: int | tuple[int, int] = 5) -> tk.Button:
    button = tk.Button(root, textvariable=text, command=command)
    button.grid(row=row, rowspan=rowspan, column=col, columnspan=columnspan, sticky=sticky, padx=padx, pady=pady)
    return button

def get_log_field(root: tk.Tk|tk.Frame, padx: tuple[int, int]|int = 5, pady: tuple[int, int]|int = 5) -> LogField:
    log_field = LogField(root, width=1, height=1)
    log_field.grid(row=0, rowspan=1, column=0, columnspan=1, sticky='nsew', pady=pady, padx=padx)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    log_field.tag_configure('error', foreground='red')
    log_field.tag_configure('warning', foreground='#DD7D40')
    log_field.tag_configure('success', foreground='green')
    log_field.tag_configure('info')
    return log_field

def get_text_field(root: tk.Tk|tk.Frame, bg=None, padx=(0, 0), pady=(0, 0)) -> tk.Text:
    text_field = tk.Text(root, width=1, height=1, bg=bg, wrap='word')
    text_field.grid(row=0, rowspan=1, column=0, columnspan=1, sticky='nsew', pady=pady, padx=padx)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    return text_field

def get_canvas(root: tk.Tk|tk.Frame, bg=None, padx=(0, 0), pady=(0, 0)) -> tk.Canvas:
    canvas = tk.Canvas(root, bg=bg)
    canvas.grid(row=0, rowspan=1, column=0, columnspan=1, sticky='nsew', padx=padx, pady=pady)
    canvas.create_text(100, 100, text="Not implemented", font='TkMenuFont', fill='red')

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    return canvas

# Adds a title bar with buttons to the top of the specified frame.
# Existing widgets in the frame are pushed down by one row.
def add_title_Frame(root: tk.Tk|tk.Frame, title: tk.StringVar, bg=None, buttons=None) -> tk.Frame:
    if buttons is None:
        buttons = []

    # Create a frame for the title bar
    title_bar = tk.Frame(root, height=30, bg=bg)

    # Add the title bar frame to the top row (row=0)
    title_bar.grid(row=0, column=0, sticky='ew')

    # Adjust existing widgets to move them down by one row
    for widget in root.winfo_children():
        if widget != title_bar:
            # Shift each widget down by changing its row index
            current_row = widget.grid_info().get('row', None)
            if current_row is not None:
                widget.grid(row=current_row + 1, column=widget.grid_info().get('column', 0),
                            sticky=widget.grid_info().get('sticky', 'nsew'),
                            padx=widget.grid_info().get('padx', 0),
                            pady=widget.grid_info().get('pady', 0))

    for button in buttons:
        b = tk.Button(title_bar, textvariable=button[0], command=button[1])
        b.pack(side=tk.RIGHT, padx=5, pady=5)

    label = tk.Label(title_bar, textvariable=title)
    label.pack(side=tk.LEFT, padx=(5, 0))
    root.grid_rowconfigure(0, weight=0)  # Title bar row does not expand
    root.grid_rowconfigure(1, weight=1)  # Existing widgets row expands
    return title_bar