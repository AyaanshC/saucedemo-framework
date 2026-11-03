"""Export actual collected node IDs, requirement IDs and scope markers without executing tests."""
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MARKERS = ['smoke', 'regression', 'case_study', 'extended', 'proposed_contract', 'coverage_limited']


class Coverage:
    def __init__(self):
        self.cases = []

    def pytest_collection_finish(self, session):
        self.cases = [dict(test=item.nodeid,
                           requirements=sorted({mark.args[0] for mark in item.iter_markers('requirement')}),
                           **{name: item.get_closest_marker(name) is not None for name in MARKERS})
                      for item in session.items]


def collect():
    plugin = Coverage()
    status = pytest.main([str(ROOT / 'tests'), '--collect-only', '-q', '-o', 'addopts=', '-o', 'log_file=NUL'],
                         plugins=[plugin])
    if status:
        return int(status)
    data = {'total': len(plugin.cases),
            'counts': {name: sum(case[name] for case in plugin.cases) for name in MARKERS},
            'cases': plugin.cases}
    output = ROOT / 'reports/coverage-map.json'
    output.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(json.dumps({'total': data['total'], **data['counts']}, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(collect())
