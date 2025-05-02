##################################################################
##
## file: App.py
##
## description: gui for sorngen.py
##
## (c) 2024 Jochen Rust
##     DSI aerospace technology
##
##################################################################
import os
import sys
import pickle
from tkinter import filedialog

from stable.control import version
from stable.gui.aux_lib import std_handler, get_grid_dimensions, ProjectSave, Copy
from stable.gui.localisation.translator import Translator
from . import sorngen
from .gui.components import *
from stable.designflow.designflow_functions import run_elaboration, run_file_writer, run_arch_builder, run_sorn_builder, run_parsing
from .gui.supported_files import SORN_files, project_files

class SorngenApp(tk.Tk):
    def __init__(self, name: str) -> None:
        # important for controlflow
        super().__init__()
        self.std_handler = std_handler(self)
        self.step = 0
        self.button_configs = {}

        ### GUI setup
        # descriptions/ labels for buttons
        self.translator = Translator(self, 'en')

        # allocate namespaces for components
        self.main_frame = None
        self.prev_frame = None

        # initialize frames
        # meta frames
        self.windows_frame = get_frame(self, bg='#f0f0f0', row=1, col=0, rowspan=2, sticky='nsew')
        self.status_frame = get_frame(self, bg='#f0f0f0', row=0, col=2, rowspan=2, sticky='nsew')
        self.info_frame = get_frame(self, bg='#f0f0f0', row=2, col=2, rowspan=2, sticky='nsew')
        self.console_frame = get_frame(self, bg='#f0f0f0')
        self.project_frame = get_frame(self, bg='#C0C0C0', row=0, col=0, sticky='nsew')
        self.navigation_frame = get_frame(self, bg='#C0C0C0', row=3, rowspan=2, col=0, sticky='nsew')

        #main frames
        self.specification_frame = get_frame(self, render=False)
        self.parsing_frame = get_frame(self, 'aquamarine', render=False)
        self.elaboration_frame = get_frame(self, 'turquoise', render=False)
        self.architecture_frame = get_frame(self, 'azure', render=False)
        self.sorn_op_frame = get_frame(self, 'darkblue', render=False)

        # initialize components
        # meta components
        self.console_log = get_log_field(self.console_frame, padx=0, pady=0)
        self.info_log = get_log_field(self.info_frame)

        # status labels
        self.parse_status = get_status_label(self.status_frame, row=0, col=1, sticky='nsew', bg='lightgray')
        self.elaborate_status = get_status_label(self.status_frame, row=1, col=1, sticky='nsew', bg='lightgray')
        self.build_status = get_status_label(self.status_frame, row=2, col=1, sticky='nsew', bg='lightgray')
        self.sorn_status = get_status_label(self.status_frame, row=3, col=1, sticky='nsew', bg='lightgray')
        self.save_status = get_status_label(self.status_frame, row=4, col=1, sticky='nsew', bg='lightgray')

        # Buttons
        self.parse_button = get_button(self.windows_frame, self.translator.get('parse_desc'), self.show_parsing_frame, 1, 0, padx=10, pady=0)
        self.elaborate_button = get_button(self.windows_frame, self.translator.get('elaborate_desc'), self.show_elaboration_frame, 2, 0, padx=10, pady=0)
        self.arch_button = get_button(self.windows_frame, self.translator.get('architecture_desc'), self.show_arch_frame, 3, 0, padx=10, pady=0)
        self.sorn_button = get_button(self.windows_frame, self.translator.get('sornop_desc'), self.show_sornop_frame, 4, 0, padx=10, pady=0)

        # main components
        self.spec_text = get_text_field(self.specification_frame)
        self.parse_canvas = get_canvas(self.parsing_frame)
        self.elab_canvas = get_canvas(self.elaboration_frame)
        self.arch_canvas = get_canvas(self.architecture_frame)
        self.sorn_canvas = get_canvas(self.sorn_op_frame)

        # Default size
        self.default_width: int = self.winfo_screenwidth() // 2
        self.default_height: int = self.winfo_screenheight() // 2
        self.geometry(f'{self.default_width}x{self.default_height}')

        # Maximize window initially but keep borders
        # self.state('zoomed')

        # frozen SornEnv states
        self.parse_data = Copy()
        self.elab_data = Copy()
        self.arch_data = Copy()
        self.sorn_data = Copy()

        # further initializations
        self.init_grid()
        self.init_components()
        self.init()
        self.title(name)


    def init_components(self):
        # disallow weird resize
        self.windows_frame.grid_propagate(False)
        self.status_frame.grid_propagate(False)
        self.navigation_frame.grid_propagate(False)
        self.specification_frame.grid_propagate(False)
        self.parsing_frame.grid_propagate(False)
        self.elaboration_frame.grid_propagate(False)
        self.sorn_op_frame.grid_propagate(False)
        self.architecture_frame.grid_propagate(False)
        self.console_frame.grid_propagate(False)

        # initialize meta buttons
        get_button(self, self.translator.get('toggle_console_desc'), self.toggle_console, 4, 2)
        get_button(self.project_frame, self.translator.get('open_project_desc'), self.open_project, 0, 0, pady=(5, 0))
        get_button(self.project_frame, self.translator.get('save_project_desc'), self.save_project, 1, 0, pady=(0, 5))
        get_button(self.navigation_frame, self.translator.get('rerun_desc'), self.rerun, 0, 0, padx=(5, 0), pady=(5, 0))
        get_button(self.navigation_frame, self.translator.get('next_step_desc'), self.next_step, 0, 1, padx=(0, 5), pady=(5, 0))
        get_button(self.navigation_frame, self.translator.get('run_all_desc'), self.run_all, 1, 0, padx=(5, 5), columnspan=2, pady=(0, 5))

        #main buttons
        get_button(self.windows_frame, self.translator.get('spec_desc'), self.show_spec_frame, 0, 0, sticky='nsew', padx=10, pady=(10, 0))

        # Labels
        get_label(self.status_frame, self.translator.get('parsing_status_desc'), row=0, col=0, sticky='nsew', bg='lightgray')
        get_label(self.status_frame, self.translator.get('elaboration_status_desc'), row=1, col=0, sticky='nsew', bg='lightgray')
        get_label(self.status_frame, self.translator.get('architecture_status_desc'), row=2, col=0, sticky='nsew', bg='lightgray')
        get_label(self.status_frame, self.translator.get('sorn_status_desc'), row=3, col=0, sticky='nsew', bg='lightgray')
        get_label(self.status_frame, self.translator.get('save_vhdl_status_desc'), row=4, col=0, sticky='nsew', bg='lightgray')

        # Titles
        add_title_Frame(self.specification_frame, self.translator.get('spec_desc'),
                        buttons=[
                            (self.translator.get('open_spec_desc'), self.open_spec_file),
                            (self.translator.get('save_spec_desc'), self.save_spec_file)
                        ])

        add_title_Frame(self.parsing_frame, self.translator.get('parse_desc'))
        add_title_Frame(self.elaboration_frame, self.translator.get('elaborate_desc'))
        add_title_Frame(self.architecture_frame, self.translator.get('architecture_desc'))
        add_title_Frame(self.sorn_op_frame, self.translator.get('sornop_desc'))
        add_title_Frame(self.console_frame, self.translator.get('console_desc'))

        # initializing configs
        self.prev_frame = self.main_frame
        self.button_configs['parse'] = self.parse_button.grid_info()
        self.button_configs['elaborate'] = self.elaborate_button.grid_info()
        self.button_configs['arch'] = self.arch_button.grid_info()
        self.button_configs['sorn'] = self.sorn_button.grid_info()
        self.update_buttons()

    def init_grid(self):
        # root grid
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=50)
        self.grid_rowconfigure(3, weight=2)
        self.grid_rowconfigure(4, weight=2)

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=11)
        self.grid_columnconfigure(2, weight=3)

        # project frame
        self.project_frame.grid_rowconfigure(0, weight=1)
        self.project_frame.grid_rowconfigure(1, weight=1)
        self.project_frame.grid_columnconfigure(0, weight=1)

        # windows_frame grid
        self.windows_frame.grid_columnconfigure(0, weight=1)

        # status_frame grid
        rows, cols = get_grid_dimensions(self.status_frame)
        for row in range(rows):
            self.status_frame.grid_rowconfigure(row, weight=1)

        for col in range(cols):
            self.status_frame.grid_columnconfigure(col, weight=1)

        # console_frame grid
        self.console_frame.grid_rowconfigure(0, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)

        # navigation_frame grid
        self.navigation_frame.grid_rowconfigure(0, weight=1)
        self.navigation_frame.grid_rowconfigure(1, weight=1)
        self.navigation_frame.grid_columnconfigure(0, weight=1)
        self.navigation_frame.grid_columnconfigure(1, weight=1)

        # setup for main frame
        self.main_frame = self.specification_frame
        self.main_frame.grid(row=0, column=1, rowspan=5, sticky='nsew')

    # version infos
    def init(self):
        sorngen.info()
        self.std_handler.handle_stdout()

    def run(self):
        self.mainloop()

    # toggles the console and changes the description
    def toggle_console(self):
        if self.main_frame is self.console_frame:
            self.translator.set_to("toggle_console_desc", 'open')
            self.switch_to(self.prev_frame)
        else:
            self.translator.set_to("toggle_console_desc", 'close')
            self.switch_to(self.console_frame)

    def show_spec_frame(self):
        self.switch_to(self.specification_frame)

    def show_parsing_frame(self):
        self.switch_to(self.parsing_frame)

    def show_elaboration_frame(self):
        self.switch_to(self.elaboration_frame)

    def show_arch_frame(self):
        self.switch_to(self.architecture_frame)

    def show_sornop_frame(self):
        self.switch_to(self.sorn_op_frame)

    # switches the main frame to the specified frame
    def switch_to(self, other: tk.Frame):
        grid_config = self.main_frame.grid_info()

        self.main_frame.grid_forget()
        other.grid_propagate(False)
        other.grid(grid_config)
        self.prev_frame = self.main_frame
        self.main_frame = other

        if self.prev_frame is self.console_frame:
            self.translator.set_to("toggle_console_desc", 'open')

    # loads a specification file
    def open_spec_file(self):
        file = filedialog.askopenfile(mode='r', filetypes=[SORN_files])

        if not file is None:
            self.spec_text.delete(1.0, tk.END)
            self.spec_text.insert(1.0, file.read())
            file.close()

    # saves a specification file
    def save_spec_file(self):
        file = filedialog.asksaveasfile(defaultextension=SORN_files[1], filetypes=[SORN_files])
        if not file is None:
            file.write(self.spec_text.get(1.0, tk.END))
            file.close()

    # opens a project
    def open_project(self):
        file = filedialog.askopenfile(mode='rb', filetypes=[project_files])
        if not file is None:
            project_save = pickle.load(file)
            self.load_from_save(project_save)
            file.close()

    # saves the current project
    def save_project(self):
        file = filedialog.asksaveasfile(mode='wb', filetypes=[project_files], defaultextension=project_files[1])
        if not file is None:
            project_save = ProjectSave(
                self.step,
                self.console_log.get(1.0, tk.END),
                self.spec_text.get(1.0, tk.END),
                self.parse_canvas,
                self.elab_canvas,
                self.arch_canvas,
                self.sorn_canvas,
                self.parse_data,
                self.elab_data,
                self.arch_data,
                self.sorn_data,
                version.version
            )
            pickle.dump(project_save, file)

    # manifests the read project file
    def load_from_save(self, save: ProjectSave):
        self.step = save.step

        self.console_log.delete('1.0', tk.END)
        self.info_log.delete('1.0', tk.END)
        self.spec_text.delete('1.0', tk.END)
        self.console_log.log(save.console_log)
        for line in save.console_log.split("\n"):
            line += "\n"
            if line.lower().startswith('info'):
                self.info_log.log(line, 'info')
            elif line.lower().startswith('error'):
                self.info_log.log(line, 'error')
            elif line.lower().startswith('warning'):
                self.info_log.log(line, 'warning')
            elif line.lower().startswith('success'):
                self.info_log.log(line, 'success')

        self.spec_text.insert(tk.END, save.spec_text)
        # TODO Canvas Implementierung

        self.parse_data = save.parse_data
        self.elab_data = save.elab_data
        self.arch_data = save.arch_data
        self.sorn_data = save.sorn_data

        if self.step > 0:
            self.parse_status.positive()
        if self.step > 1:
            self.elaborate_status.positive()
        if self.step > 2:
            self.build_status.positive()
        if self.step > 3:
            self.sorn_status.positive()
        if self.step > 4:
            self.save_status.positive()

        if save.version != version.version:
            print(f"WARNING: current version ({version.version}) may be incompatible with version of save ({save.version})")
            self.std_handler.handle_stdout()

        self.update_buttons()

    # Parsing step
    def parse(self):
        self.parse_status.waiting()
        try:
            os.environ['specification'] = self.spec_text.get(1.0, tk.END)

            self.parse_data.save(run_parsing())
            self.show_parsing_frame()
            self.parse_status.positive()

            self.step = 1

        except Exception as e:
            self.step = 0
            self.parse_status.negative()
            sys.stderr.write(str(e) + "\n")

    # Elaboration step
    def elaborate(self):
        self.elaborate_status.waiting()
        try:
            # noinspection PyTypeChecker
            self.elab_data.save(run_elaboration(self.parse_data.load()))
            self.show_elaboration_frame()
            self.elaborate_status.positive()

            self.step = 2

        except Exception as e:
            self.step = 1
            self.elaborate_status.negative()
            sys.stderr.write(str(e) + "\n")

    # Architecture step
    def build_architecture(self):
        self.build_status.waiting()
        try:

            # noinspection PyTypeChecker
            self.arch_data.save(run_arch_builder(self.elab_data.load()))
            self.show_arch_frame()
            self.build_status.positive()

            self.step = 3

        except Exception as e:
            self.step = 2
            self.build_status.negative()
            sys.stderr.write(str(e) + "\n")

    # SORN step
    def build_sorn(self):
        self.sorn_status.waiting()
        try:
            # noinspection PyTypeChecker
            self.sorn_data.save(run_sorn_builder(self.arch_data.load()))

            self.show_sornop_frame()
            self.sorn_status.positive()

            self.step = 4

        except Exception as e:
            self.step = 3
            self.sorn_status.negative()
            sys.stderr.write(str(e) + "\n")

    # File writer step
    def generate_file(self):
        self.save_status.waiting()
        directory = filedialog.askdirectory()

        if directory != "":
            try:
                sorn_data = self.sorn_data.load()
                sorn_data.save_path = directory
                run_file_writer(sorn_data)
                self.save_status.positive()
                self.step = 5

            except Exception as e:
                self.step = 4
                self.save_status.negative()
                sys.stderr.write(str(e) + "\n")
        else:
            self.save_status.normal()

    # updates the visible buttons
    def update_buttons(self):
        confs = self.button_configs

        self.parse_button.grid_forget()
        self.elaborate_button.grid_forget()
        self.arch_button.grid_forget()
        self.sorn_button.grid_forget()

        if self.step >= 1:
            self.parse_button.grid(confs['parse'])
        else:
            self.parse_data.delete()
            self.parse_status.disable_if(['positive', 'waiting'])

        if self.step >= 2:
            self.elaborate_button.grid(confs['elaborate'])
        else:
            self.elab_data.delete()
            self.elaborate_status.disable_if(['positive', 'waiting'])

        if self.step >= 3:
            self.arch_button.grid(confs['arch'])
        else:
            self.arch_data.delete()
            self.build_status.disable_if(['positive', 'waiting'])

        if self.step >= 4:
            self.sorn_button.grid(confs['sorn'])
            self.translator.set_to("next_step_desc", 'last')
        else:
            self.sorn_data.delete()
            self.sorn_status.disable_if(['positive', 'waiting'])

        if self.step >= 5:
            pass
        else:
            self.save_status.disable_if(['positive', 'waiting'])

    # returns to the specified task
    def rerun(self):
        match self.main_frame:
            case self.specification_frame:
                self.step = 0
            case self.parsing_frame:
                self.parse()
            case self.elaboration_frame:
                self.elaborate()
            case self.architecture_frame:
                self.build_architecture()
            case self.sorn_op_frame:
                self.build_sorn()

        self.translator.set_to("next_step_desc", 'next')

        self.update_buttons()
        self.std_handler.handle_stdout()


    # executes the next sorngen step
    def next_step(self):
        match self.step:
            case 0:
                self.parse()
            case 1:
                self.elaborate()
            case 2:
                self.build_architecture()
            case 3:
                self.build_sorn()
            case 4 | 5:
                self.generate_file()

        self.update_buttons()
        self.std_handler.handle_stdout()

    # executes all sorngen steps
    def run_all(self):
        self.parse()
        self.elaborate()
        self.build_architecture()
        self.build_sorn()
        self.generate_file()

        self.update_buttons()
        self.std_handler.handle_stdout()


if __name__ == '__main__':
    app = SorngenApp(f"Sorngen {version.version} - (c) Jochen Rust")
    app.run()
