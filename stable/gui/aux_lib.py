##################################################################
##
## file: aux_lib.py
##
## description: provides useful helper functions
##
## (c) 2024 Jochen Rust
##     DSI aerospace technology
##
##################################################################
import io
import pickle
import sys

def get_grid_dimensions(frame):
    rows = []
    columns = []

    for widget in frame.grid_slaves():
        rows.append(widget.grid_info()['row'])
        columns.append(widget.grid_info()['column'])

    # Determine the maximum row and column
    max_row = max(rows) if rows else -1
    max_column = max(columns) if columns else -1

    return max_row + 1, max_column + 1

def save_grid_config(element):
    return element.grid_info()


def set_grid_config(element, config):
    element.grid(config)



class std_handler:
    def __init__(self, gui):
        self.app = gui
        self.old_stdout = sys.stdout
        self.new_stdout = io.StringIO()

        self.current_cursor = 0
        self.capture()

    def prepare(self):
        self.new_stdout.seek(self.current_cursor)

    def stop(self):
        sys.stdout = self.old_stdout

    def capture(self):
        sys.stdout = self.new_stdout

    def handle_stdout(self):
        self.prepare()
        for line in self.new_stdout.readlines():
            self.app.console_log.log(line)
            if line.lower().startswith('info'):
                self.app.info_log.log(line, 'info')
            elif line.lower().startswith('error'):
                self.app.info_log.log(line, 'error')
            elif line.lower().startswith('warning'):
                self.app.info_log.log(line, 'warning')
            elif line.lower().startswith('success'):
                self.app.info_log.log(line, 'success')

        self.current_cursor = len(self.new_stdout.getvalue())

class ProjectSave:
    def __init__(self, step, console_log, spec_text, parse_canvas, elab_canvas, arch_canvas, sorn_canvas, parse_data, elab_data, arch_data, sorn_data, version):
        self.step = step
        self.console_log = console_log
        self.spec_text = spec_text
        #self.parse_canvas = parse_canvas
        #self.elab_canvas = elab_canvas
        #self.arch_canvas = arch_canvas
        #self.sorn_canvas = sorn_canvas
        self.parse_data = parse_data
        self.elab_data = elab_data
        self.arch_data = arch_data
        self.sorn_data = sorn_data
        self.version = version


class Copy(io.BytesIO):
    def __init__(self, obj=None):
        super().__init__()
        if obj is not None:
            self.save(obj)

    def save(self, obj):
        # noinspection PyTypeChecker
        pickle.dump(obj, self)

    def load(self):
        self.seek(0)
        return pickle.load(self)

    def delete(self):
        self.flush()
