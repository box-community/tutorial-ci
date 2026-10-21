# Tutorial CI

Shared GitHub Actions workflows that keep the sample repositories behind the
[Box developer tutorials](https://developer.box.com/tutorials) working as their
dependencies change.

Each sample repository calls these workflows from a short caller file, so a fix
or improvement lands here once instead of in every repository.

## Workflows

### `python-ci.yml`

For Python samples that install from `requirements.txt`. For each Python
version in the matrix (3.11 and 3.14 by default), it:

1. Installs the newest versions `requirements.txt` allows. There is no
   lockfile, so this matches what a reader following the tutorial installs.
2. Runs `pip check` to catch conflicting packages.
3. Imports every top-level `.py` file, with a placeholder value for each
   variable in `.env.example`.
4. Calls `GET /health` on any Flask app named `app` and expects `200`.

It needs no secrets and never calls Box.

| Input | Default | Description |
| --- | --- | --- |
| `python-versions` | `'["3.11", "3.14"]'` | JSON list of Python versions to test. |
| `working-directory` | `.` | Directory that contains `requirements.txt` and the sample's modules. |

### `python-live.yml`

Runs a sample's live test against a test Box enterprise. It installs
`requirements.txt`, exports every secret the caller passes as an environment
variable with the same name, and runs the test command. Name the secrets after
the variables in the sample's `.env.example`, so the test reads them the same
way the sample does.

The job skips pull requests from forks, which never receive secrets, and runs
one live test at a time per repository.

| Input | Default | Description |
| --- | --- | --- |
| `python-version` | `'3.14'` | Python version to run the live test on. |
| `test-command` | `python tests/live_test.py` | Command that runs the sample's live test. |
| `working-directory` | `.` | Directory that contains `requirements.txt` and the sample's modules. |

## Use it in a sample repository

Add `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    # Weekly, to catch new releases of unpinned dependencies.
    - cron: '0 6 * * 1'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  ci:
    uses: box-community/tutorial-ci/.github/workflows/python-ci.yml@v1
```

To run a live test, add `tests/live_test.py` and `.github/workflows/live.yml`:

```yaml
name: Live test (Box)

on:
  pull_request:
  schedule:
    - cron: '0 6 * * 1'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  live:
    uses: box-community/tutorial-ci/.github/workflows/python-live.yml@v1
    secrets: inherit
```

Add the secrets under **Settings > Secrets and variables** in both the
**Actions** and **Dependabot** sections. Workflows triggered by Dependabot pull
requests only receive Dependabot secrets.

Add `.github/dependabot.yml` so Dependabot proposes updates to `requirements.txt`
and to the `@v1` reference above:

```yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    # Only propose a change when a release falls outside the allowed range,
    # such as a new boxsdk major. Newer releases within range already install.
    versioning-strategy: increase-if-necessary
    schedule:
      interval: weekly
      day: sunday
    cooldown:
      default-days: 5
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
      day: sunday
    cooldown:
      default-days: 5
```

## Versioning

Sample repositories pin a major version tag such as `@v1`. Backward-compatible
changes move the `v1` tag forward. Breaking changes, such as a new required
input, get a new major tag so existing callers keep working until they opt in.

Changes here are tested by `self-test.yml`, which runs both workflows against
the fixture in `tests/fixtures/flask-app`. The live fixture expects a
`FIXTURE_SECRET` repository secret (any value) in both the Actions and
Dependabot sections.

## License

[MIT](./LICENSE)
