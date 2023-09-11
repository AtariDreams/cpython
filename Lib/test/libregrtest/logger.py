import os
import time

from test.libregrtest.runtests import RunTests
from test.libregrtest.utils import print_warning, MS_WINDOWS

if MS_WINDOWS:
    from test.libregrtest.win_utils import WindowsLoadTracker


class Logger:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.test_count_text = ''
        self.test_count_width = 3
        self.win_load_tracker = None

    def log(self, line: str = '') -> None:
        empty = not line

        # add the system load prefix: "load avg: 1.80 "
        load_avg = self.get_load_avg()
        if load_avg is not None:
            line = f"load avg: {load_avg:.2f} {line}"

        # add the timestamp prefix:  "0:01:05 "
        test_time = time.perf_counter() - self.start_time

        mins, secs = divmod(int(test_time), 60)
        hours, mins = divmod(mins, 60)
        test_time = "%d:%02d:%02d" % (hours, mins, secs)

        line = f"{test_time} {line}"
        if empty:
            line = line[:-1]

        print(line, flush=True)

    def get_load_avg(self) -> float | None:
        if hasattr(os, 'getloadavg'):
            return os.getloadavg()[0]
        if self.win_load_tracker is not None:
            return self.win_load_tracker.getloadavg()
        return None

    def set_tests(self, runtests: RunTests) -> None:
        if runtests.forever:
            self.test_count_text = ''
            self.test_count_width = 3
        else:
            self.test_count_text = '/{}'.format(len(runtests.tests))
            self.test_count_width = len(self.test_count_text) - 1

    def start_load_tracker(self) -> None:
        if not MS_WINDOWS:
            return

        try:
            self.win_load_tracker = WindowsLoadTracker()
        except PermissionError as error:
            # Standard accounts may not have access to the performance
            # counters.
            print_warning(f'Failed to create WindowsLoadTracker: {error}')

    def stop_load_tracker(self) -> None:
        if self.win_load_tracker is None:
            return
        self.win_load_tracker.close()
        self.win_load_tracker = None
