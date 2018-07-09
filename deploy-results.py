import os

from cico import TravisCI, GitHub
from cico.results import Directory, File, Badge


class TestStatusBadge(Badge):
    def __init__(self, tap_file):
        results = self.get_test_counts(tap_file)
        value = ', '.join('{} {}'.format(name, count)
                          for name, count in results.items() if count)
        color = 'green'
        if results['failed']:
            color = 'red'
        elif results['skipped']:
            color = 'orange'
        super().__init__('tests', png=True, label='tests', value=value,
                         default_color=color)

    @staticmethod
    def get_test_counts(tap_file):
        result = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
        }
        with open(tap_file, 'r') as result_file:
            for line in result_file.readlines():
                if '# SKIP' in line:
                    result['skipped'] += 1
                elif line.startswith('ok'):
                    result['passed'] += 1
                elif line.startswith('not ok'):
                    result['failed'] += 1
        return result


TravisCI(
    repo=GitHub('stefanhoelzl', 'ci-results', os.environ.get('GITHUB_TOKEN')),
    branch='fancy-dict',
    results=[
        File('testresults.tap'),
        Directory('covhtml'),
        TestStatusBadge('testresults.tap'),
    ]
).commit()
