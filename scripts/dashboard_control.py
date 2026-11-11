"""Apply dashboard controls at testcase boundaries so Chrome teardown and reports finish."""
import os
from pathlib import Path
import time

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    control = Path(os.environ["SAUCE_RUN_CONTROL"])
    while True:
        command = control.read_text(encoding="ascii")
        if command == "terminate":
            pytest.exit("Terminated from the dashboard", returncode=2)
        if command == "run":
            return
        # Poll only while a presenter has explicitly paused the run.
        time.sleep(0.2)
