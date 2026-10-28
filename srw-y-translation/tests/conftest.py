"""Fail the session if any test is skipped.

Owner decision (2026-10-27): tests may only depend on files committed in this
repository. A skip usually means somebody reintroduced a dependency on a
private `local/`, `build/` or Drive artifact. Rather than silently hiding such
a test, the whole run fails so it gets fixed or deleted.
"""


def pytest_sessionfinish(session, exitstatus):
    reporter = session.config.pluginmanager.get_plugin('terminalreporter')
    skipped = reporter.stats.get('skipped', []) if reporter else []
    if skipped:
        reporter.write_line(
            f'ERROR: {len(skipped)} skipped test(s); all test inputs must be in the repo',
            red=True)
        session.exitstatus = 1
