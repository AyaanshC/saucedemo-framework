"""Local dashboard and allowlisted Selenium test runner."""
import json
import os
import tempfile
import subprocess
import sys
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from build_dashboard import ROOT, build

ADDRESS = ('127.0.0.1', 8766)
ORIGIN = 'http://127.0.0.1:8766'
MODULES = {'login': ['tests/test_login.py'], 'cart': ['tests/test_inventory_cart.py'],
           'checkout': ['tests/test_checkout.py'], 'all': ['tests']}
lock = threading.Lock()
state = {'running': False, 'revision': 0, 'message': 'Ready to test.'}


def set_control(command):
    # Replace the file atomically so pytest always reads a complete command.
    temporary = control.with_suffix('.new')
    temporary.write_text(command, encoding='ascii')
    temporary.replace(control)


control = None


def execute(module, directory):
    try:
        output = Path(directory.name)
        with (output / 'demo.log').open('w', encoding='utf-8') as log:
            result = subprocess.run([sys.executable, '-m', 'pytest', '-p', 'scripts.dashboard_control', *MODULES[module], '-m', 'case_study',
                                     '--headed', f'--html={output / "demo.html"}',
                                     f'--junitxml={output / "demo.xml"}', '-o', f'log_file={output / "pytest.log"}',
                                     '-o', f'cache_dir={output / "cache"}'],
                                    env=dict(os.environ, SAUCE_RUN_CONTROL=str(control), SAUCE_DEMO_OUTPUT=str(output)), cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        message = f'{module.title()} finished (pytest exit {result.returncode}).'
    except Exception as exc:
        message = f'Run error: {exc}'
    with lock:
        directory.cleanup()
        if state.get('mode') == 'terminate' and 'finished' in message:
            message = f'{module.title()} stopped. Demo terminated.'
        state.update(module=None, mode=None, running=False, revision=state['revision'] + 1, message=message)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def reply(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.headers.get('Host') != ORIGIN[7:] or self.headers.get('Origin') != ORIGIN:
            return self.send_error(403)
        parts = self.path.strip('/').split('/')
        if len(parts) != 2 or parts[1] not in MODULES or parts[0] not in ('run', 'pause', 'resume', 'terminate'):
            return self.send_error(404)
        action, module = parts
        global control
        with lock:
            if action == 'run':
                if state['running']:
                    return self.reply(409, state)
                directory = tempfile.TemporaryDirectory(prefix='sauce-run-')
                control = Path(directory.name) / 'command'
                set_control('run')
                state.update(running=True, module=module, mode='run', message=f'Running {module} in Chrome...')
                threading.Thread(target=execute, args=(module, directory), daemon=True).start()
            else:
                if not state['running'] or state['module'] != module or state['mode'] == 'terminate':
                    return self.reply(409, state)
                mode = 'run' if action == 'resume' else action
                set_control(mode)
                messages = {'run': 'Running', 'pause': 'Pause requested at the next case boundary',
                            'terminate': 'Stopping after the current case'}
                state.update(mode=mode, message=f'{module.title()}: {messages[mode]}.')
            self.reply(202, state)

    def do_GET(self):
        if self.headers.get('Host') != ORIGIN[7:]:
            return self.send_error(403)
        if self.path == '/status':
            with lock:
                return self.reply(200, state)
        path = Path(self.translate_path(urlsplit(self.path).path)).resolve()
        if not path.is_file() or not any(path.is_relative_to(ROOT / folder)
                for folder in ('reports', 'performance/html_report', 'dashboard/recording')):
            return self.send_error(404)
        super().do_GET()

    def do_HEAD(self):
        self.send_error(405)


if __name__ == '__main__':
    from urllib.request import urlopen
    url = ORIGIN + '/reports/dashboard.html'
    try:
        server = ThreadingHTTPServer(ADDRESS, Handler)
    except OSError:
        with urlopen(ORIGIN + '/status', timeout=2) as response:
            assert 'revision' in json.load(response)
        webbrowser.open(url)
    else:
        with server:
            build()
            print('Keep this window open while using the dashboard. Ctrl+C stops the server.', flush=True)
            webbrowser.open(url)
            server.serve_forever()
