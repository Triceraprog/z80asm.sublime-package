""" Build Command for Sublime Text 3 launching assembly and running MAME.

Copyright 2018 Sylvain Glaize

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without
limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import subprocess
import threading
import os

import sublime
import sublime_plugin


class Panel:
    def __init__(self, window, set_settings):
        self.panel_lock = threading.Lock()
        with self.panel_lock:
            self.panel = window.create_output_panel('exec')

            settings = self.panel.settings()

            set_settings(settings)

            window.run_command('show_panel', {'panel': 'output.exec'})

    def do_write(self, text):
        with self.panel_lock:
            self.panel.run_command('append', {'characters': text})


class CommunicatingProcess:
    encoding = 'utf-8'

    def __init__(self, commands, working_dir, panel, proc_controller):
        assert commands

        self.panel = panel
        self.proc_controller = proc_controller

        args = commands[0]
        self.next_commands = commands[1:]
        self.working_dir = working_dir
        self.panel = panel

        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=working_dir
        )
        self.proc_controller.set(proc)

        threading.Thread(
            target=self.read_handle,
            args=(self.proc_controller.proc.stdout, )
        ).start()

    def read_handle(self, handle, ):
        chunk_size = 2 ** 13
        out = b''
        chain = False

        while True:
            try:
                data = os.read(handle.fileno(), chunk_size)
                out += data
                if len(data) == chunk_size:
                    continue
                if data == b'' and out == b'':
                    raise IOError('EOF')

                self.queue_write(out.decode(self.encoding))
                if data == b'':
                    raise IOError('EOF')
                out = b''

            except (UnicodeDecodeError) as ex:
                msg = 'Error decoding output using %s - %s'
                self.queue_write(msg % (self.encoding, str(ex)))
                break

            except IOError:
                returncode = self.proc_controller.returncode()

                if returncode == 0:
                    msg = 'Finished'
                    chain = True
                else:
                    msg = 'Finished with Error'

                self.proc_controller.stop()

                self.queue_write('\n[%s]\n' % msg)
                break

        if chain and self.next_commands:
            CommunicatingProcess(self.next_commands,
                                 self.working_dir,
                                 self.panel,
                                 self.proc_controller)

    def queue_write(self, text):
        sublime.set_timeout(lambda: self.panel.do_write(text), 1)


def fix_script_path(script_path, script_name):
    script_complete_path = os.path.join(script_path, script_name)

    if not os.path.exists(script_complete_path):
        script_complete_path = script_name

        if not os.path.exists(script_complete_path):
            return None

        else:
            # Mame needs complete path
            return os.path.realpath(script_complete_path)

    return script_complete_path


class ProcessController:
    def __init__(self):
        self.proc = None

    def is_running(self):
        return self.proc is not None and self.proc.poll() is None

    def set(self, proc):
        assert self.proc is None
        self.proc = proc

    def stop(self):
        if self.is_running():
            self.proc.terminate()
        self.proc = None

    def returncode(self):
        poll = self.proc.poll()
        if poll is None:
            return None

        return self.proc.returncode


class Z80AsmCommand(sublime_plugin.WindowCommand):
    proc_controller = ProcessController()

    def run(self, **kwargs):
        variables = self.window.extract_variables()
        working_dir = variables['file_path']
        filename = variables['file']

        def set_settings(settings):
            settings.set(
                'result_file_regex',
                r"^Error at file '([^']+)' line (\d+): ()(.+)"
            )
            settings.set('result_base_dir', working_dir)

        panel = Panel(self.window, set_settings)

        self.proc_controller.stop()

        script_path = os.path.dirname(os.path.realpath(__file__))
        script_name = kwargs.get('script', "mame")
        script_complete_path = fix_script_path(script_path, script_name)

        if not script_complete_path:
            panel. \
                do_write("Autoboot Script not found: {}\n".format(script_name))

        mame_path = kwargs.get('mame_path', "mame")

        asm = ['z80asm', '-v', '-o=input.bin', '-b', filename]
        mame = [mame_path, 'vg5k', '-ramsize', '48k', '-nomax', '-window',
                '-autoboot_delay', '0', '-autoboot_script',
                script_complete_path,
                '-debug', '-debugger', 'none']
        commands = [asm, mame]

        CommunicatingProcess(commands,
                             working_dir,
                             panel,
                             self.proc_controller)
