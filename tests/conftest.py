from pathlib import Path

from coverage import Coverage


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not getattr(config.option, "cov_source", None):
        return

    coverage_file = Path(".coverage")
    if not coverage_file.exists():
        return

    cov = Coverage(data_file=str(coverage_file))
    cov.load()

    statements_total = 0
    missed_total = 0
    for filename in cov.get_data().measured_files():
        try:
            _, statements, _, missing, _ = cov.analysis2(filename)
        except Exception:
            continue
        statements_total += len(statements)
        missed_total += len(missing)

    if statements_total == 0:
        return

    covered_percent = ((statements_total - missed_total) / statements_total) * 100
    percent_display = f"{covered_percent:.0f}%"

    terminalreporter.write_sep("=", "tests coverage")
    terminalreporter.write_line(f"TOTAL {percent_display}")
