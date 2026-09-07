# Test Result Archive Standard

Status: REQUIRED for active/work repositories

## Purpose

Every automated or manual test run used to support a project conclusion must leave a reproducible evidence package. A green or red CI line without archived results is not sufficient evidence.

## Required archive contents

For every test run preserve, when applicable:

- repository and project name;
- commit SHA and branch/ref;
- UTC timestamp and run identifier;
- test suite / validator names;
- exact test command(s);
- environment/runtime versions;
- PASS / FAIL / ERROR / SKIPPED summary;
- passed, failed, error and skipped counts when the runner exposes them;
- duration when measured;
- raw stdout/stderr or equivalent runner log;
- machine-readable result (JUnit XML, JSON, SARIF or native report) when supported;
- coverage report when coverage is part of the run;
- hashes of generated evidence where practical;
- failure diagnostics and rerun/attempt identity.

## Storage layers

### CI artifact layer

Every CI run must upload a test-evidence artifact using `if: always()` (or platform equivalent) so failed runs are archived too.

Recommended artifact name:

`test-evidence-<project>-<workflow>-<run_id>-<attempt>-<short_sha>`

Recommended retention: 90 days unless project policy requires longer.

### Repository history layer

Do not commit every raw CI log to Git. Commit durable summaries only when they are part of a release, audit, investigation, benchmark, acceptance gate, regression baseline, red-team pass, or other decision record.

Recommended path:

`test-archive/YYYY/MM/<timestamp>-<short_sha>/`

Typical durable files:

- `summary.json`
- `summary.md`
- `manifest.json`
- selected JUnit/SARIF/report files

Large logs remain CI artifacts or external/local evidence storage and are referenced by run ID and hashes.

## Failure preservation

A failed test must not suppress archival. Test execution and evidence upload are separate concerns. The workflow must preserve the original test exit code while still running the archive step.

Acceptable patterns include:

1. run tests normally;
2. write results/logs to a known directory;
3. upload artifacts with `if: always()`;
4. allow the job to remain failed when the test command failed.

Do not use `continue-on-error: true` merely to make archival possible unless a later explicit gate restores the correct failure status.

## Minimum directory contract

Projects should write transient test evidence under:

`.test-results/`

Suggested layout:

```text
.test-results/
  manifest.json
  summary.json
  logs/
  junit/
  coverage/
  sarif/
  reports/
```

The directory is normally gitignored. CI uploads it as an artifact after every run.

## Manifest minimum fields

```json
{
  "schema_version": "1.0",
  "project": "<repo>",
  "repository": "<owner/repo>",
  "commit_sha": "<sha>",
  "ref": "<branch-or-tag>",
  "workflow": "<workflow>",
  "run_id": "<run-id>",
  "run_attempt": "<attempt>",
  "started_at_utc": "<timestamp>",
  "status": "PASS|FAIL|ERROR|CANCELLED|UNKNOWN",
  "commands": [],
  "result_files": [],
  "notes": []
}
```

## Project-specific runners

Use native machine-readable formats where available:

- Python / pytest: `--junitxml=.test-results/junit/pytest.xml` plus captured log;
- Go: `go test -json` plus human-readable log;
- Java/JUnit/Gradle/Maven: preserve XML reports;
- JavaScript/TypeScript: JUnit/JSON reporter where supported;
- C/C++: preserve CTest XML/JUnit or raw executable log;
- security scanners: SARIF/JSON/native report;
- KB validators: raw validator log + machine-readable summary/regression count.

## Active-project rule

This standard applies to all active/work projects maintained by the user, including knowledge-base, OSINT, security, AI, automation, site/application and engineering repositories. Old archived/training repositories need not be retrofitted unless work resumes in them.

When a project is next modified, its CI/test runner must be brought into compliance with this standard as part of that work.

## Reporting rule

Project status reports should cite archived test evidence rather than relying only on statements such as "tests passed". Where no artifact was produced, report that evidence is incomplete.
