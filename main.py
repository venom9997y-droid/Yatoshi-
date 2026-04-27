import os
import sys
import threading
import subprocess

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock

Window.clearcolor = (0.04, 0.04, 0.04, 1)

BANNER = """
 ██╗   ██╗ █████╗ ████████╗ ██████╗ ███████╗██╗  ██╗██╗
 ╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗██╔════╝██║  ██║██║
  ╚████╔╝ ███████║   ██║   ██║   ██║███████╗███████║██║
   ╚██╔╝  ██╔══██║   ██║   ██║   ██║╚════██║██╔══██║██║
    ██║   ██║  ██║   ██║   ╚██████╔╝███████║██║  ██║██║
    ╚═╝   ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝

 Python Terminal v1.0 — type 'help' for commands
 ─────────────────────────────────────────────────\n
"""

HELP_TEXT = """
 Available commands:
   python <file.py>     — run a python script
   pip install <pkg>    — install a package
   pip list             — list installed packages
   pip uninstall <pkg>  — remove a package
   ls [path]            — list files
   cd <path>            — change directory
   pwd                  — current directory
   clear                — clear screen
   help                 — show this help
 ─────────────────────────────────────────────\n
"""


class YatoshiTerminal(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=4, spacing=2, **kwargs)
        self.history = []
        self.history_index = -1
        self.current_dir = os.path.expanduser('~')
        self.process = None

        self._build_ui()
        Clock.schedule_once(lambda dt: self.write(BANNER), 0.1)

    def _build_ui(self):
        # Top bar
        topbar = BoxLayout(size_hint_y=None, height=36, spacing=6)
        title = Label(
            text='[b][color=33ff66]Yatoshi[/color][/b]',
            markup=True, size_hint_x=0.4,
            font_size=16
        )
        kill_btn = Button(
            text='■ Kill', size_hint_x=None, width=70,
            background_color=(0.6, 0.1, 0.1, 1),
            font_size=13
        )
        kill_btn.bind(on_press=self.kill_process)
        clear_btn = Button(
            text='Clear', size_hint_x=None, width=70,
            background_color=(0.15, 0.15, 0.15, 1),
            font_size=13
        )
        clear_btn.bind(on_press=lambda x: self.clear())
        topbar.add_widget(title)
        topbar.add_widget(Label())  # spacer
        topbar.add_widget(kill_btn)
        topbar.add_widget(clear_btn)
        self.add_widget(topbar)

        # Output scroll
        self.scroll = ScrollView(do_scroll_x=False)
        self.output = TextInput(
            text='',
            readonly=True,
            background_color=(0.04, 0.04, 0.04, 1),
            foreground_color=(0.2, 1.0, 0.4, 1),
            cursor_color=(0.2, 1.0, 0.4, 1),
            font_size=13,
            size_hint_y=None,
            font_name='RobotoMono-Regular',
        )
        self.output.bind(minimum_height=self.output.setter('height'))
        self.scroll.add_widget(self.output)
        self.add_widget(self.scroll)

        # Quick buttons
        quick = BoxLayout(size_hint_y=None, height=40, spacing=4)
        quick_cmds = [
            ('python', 'python '),
            ('pip install', 'pip install '),
            ('pip list', 'pip list'),
            ('ls', 'ls'),
            ('pwd', 'pwd'),
        ]
        for label, cmd in quick_cmds:
            b = Button(
                text=label,
                background_color=(0.1, 0.25, 0.15, 1),
                font_size=12
            )
            b.bind(on_press=lambda x, c=cmd: self._set_input(c))
            quick.add_widget(b)
        self.add_widget(quick)

        # Input row
        input_row = BoxLayout(size_hint_y=None, height=44, spacing=4)
        self.prompt_label = Label(
            text='[color=33ff66]$[/color]',
            markup=True,
            size_hint_x=None, width=22,
            font_size=16
        )
        self.cmd_input = TextInput(
            multiline=False,
            background_color=(0.08, 0.08, 0.08, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.2, 1.0, 0.4, 1),
            font_size=14,
            hint_text='Enter command...',
            hint_text_color=(0.4, 0.4, 0.4, 1),
        )
        self.cmd_input.bind(on_text_validate=self._on_enter)
        run_btn = Button(
            text='▶ Run',
            size_hint_x=None, width=80,
            background_color=(0.1, 0.5, 0.2, 1),
            font_size=14
        )
        run_btn.bind(on_press=self._on_enter)
        input_row.add_widget(self.prompt_label)
        input_row.add_widget(self.cmd_input)
        input_row.add_widget(run_btn)
        self.add_widget(input_row)

    def _set_input(self, text):
        self.cmd_input.text = text
        self.cmd_input.focus = True
        self.cmd_input.cursor = (len(text), 0)

    def write(self, text):
        def _write(dt):
            self.output.text += text
            Clock.schedule_once(lambda dt2: setattr(
                self.scroll, 'scroll_y', 0), 0.05)
        Clock.schedule_once(_write)

    def clear(self):
        self.output.text = BANNER

    def kill_process(self, *args):
        if self.process:
            try:
                self.process.kill()
                self.write('\n[Process killed]\n')
            except Exception:
                pass
            self.process = None

    def _on_enter(self, *args):
        cmd = self.cmd_input.text.strip()
        if not cmd:
            return
        self.cmd_input.text = ''
        self.history.append(cmd)
        self.history_index = len(self.history)
        self.write(f'\n[color=33ff66]$[/color] {cmd}\n' if False else f'\n$ {cmd}\n')
        self._execute(cmd)

    def _execute(self, cmd):
        # Built-in commands
        parts = cmd.split()
        if not parts:
            return

        if parts[0] == 'help':
            self.write(HELP_TEXT)
            return

        if parts[0] == 'clear':
            self.clear()
            return

        if parts[0] == 'cd':
            path = parts[1] if len(parts) > 1 else os.path.expanduser('~')
            try:
                os.chdir(path)
                self.current_dir = os.getcwd()
                self.write(f'→ {self.current_dir}\n')
            except Exception as e:
                self.write(f'cd: {e}\n')
            return

        # Run as shell command
        threading.Thread(target=self._run_shell, args=(cmd,), daemon=True).start()

    def _run_shell(self, cmd):
        try:
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            env['HOME'] = os.path.expanduser('~')

            self.process = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.current_dir,
                env=env
            )

            for line in iter(self.process.stdout.readline, ''):
                self.write(line)

            self.process.wait()
            code = self.process.returncode
            if code != 0:
                self.write(f'\n[Exit code: {code}]\n')
            self.process = None

        except Exception as e:
            self.write(f'Error: {e}\n')
            self.process = None

    def run_file(self, path):
        """Called when .py file opened from file manager"""
        self.write(f'\n→ Running: {path}\n')
        self._execute(f'python "{path}"')


class YatoshiApp(App):
    def build(self):
        self.title = 'Yatoshi'
        self.icon = 'icon.png'
        self.terminal = YatoshiTerminal()
        return self.terminal

    def on_start(self):
        """Handle .py file opened via intent"""
        try:
            from android import activity
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            intent = PythonActivity.mActivity.getIntent()
            action = intent.getAction()
            uri = intent.getData()
            if uri:
                path = uri.getPath()
                if path and path.endswith('.py'):
                    Clock.schedule_once(
                        lambda dt: self.terminal.run_file(path), 1)
        except Exception:
            pass


if __name__ == '__main__':
    YatoshiApp().run()
