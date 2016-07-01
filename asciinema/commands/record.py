import sys
import os
import subprocess
import tempfile

from asciinema.commands.command import Command
from asciinema.recorder import Recorder
from asciinema.api import APIError


class RecordCommand(Command):

    def __init__(self, api, filename, command, title, assume_yes, recorder=None):
        Command.__init__(self)
        self.api = api
        self.filename = filename
        self.command = command
        self.title = title
        self.assume_yes = assume_yes
        self.recorder = recorder if recorder is not None else Recorder()

    def execute(self):
        if self.filename == "":
            self.filename = self._tmp_path()
            upload = True
        else:
            upload = False

        self.print_info("Asciicast recording started.")
        self.print_info("""Hit Ctrl-D or type "exit" to finish.""")

        self.recorder.record(self.filename, self.command, self.title)

        self.print_info("Asciicast recording finished.")

        if upload:
            if not self.assume_yes:
                self.print_info("Press <Enter> to upload, <Ctrl-C> to cancel.")
                try:
                    sys.stdin.readline()
                except KeyboardInterrupt:
                    return 0

            try:
                url, warn = self.api.upload_asciicast(self.filename)
                if warn:
                    self.print_warning(warn)
                os.remove(self.filename)
                self.print(url)
            except APIError as e:
                self.print_warning("Upload failed: %s" % str(e))
                self.print_warning("Retry later by running: asciinema upload %s" % self.filename)
                return 1

        return 0

    def _tmp_path(self):
        fd, path = tempfile.mkstemp(suffix='-asciinema.json')
        os.close(fd)
        return path