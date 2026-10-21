import os
import sys

# Set as a repository secret (Actions and Dependabot) on tutorial-ci.
if not os.environ.get("FIXTURE_SECRET"):
    sys.exit("FIXTURE_SECRET was not exported from the caller's secrets")

if "github_token" in os.environ or "GITHUB_TOKEN" in os.environ:
    sys.exit("The workflow token must not be exported")

print("Live test fixture passed")
