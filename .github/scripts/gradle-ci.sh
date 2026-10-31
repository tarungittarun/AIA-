#!/usr/bin/env bash
set -uo pipefail
label="$1"
shift
log="gradle-${label}.log"
set +e
gradle "$@" --stacktrace --console=plain >"$log" 2>&1
result=$?
set -e
if [[ $result -ne 0 ]]; then
  detail=$(grep -A18 -B2 -E 'What went wrong|FAILURE:|Could not resolve|Script compilation error|FAILED|error:' "$log" | head -n 24 | tr '\n' ' ' | cut -c1-12000)
  echo "::error title=Gradle ${label} failed::${detail:-See ${log}}"
  echo "## Gradle ${label} failed" >> "$GITHUB_STEP_SUMMARY"
  echo '```text' >> "$GITHUB_STEP_SUMMARY"
  tail -n 80 "$log" >> "$GITHUB_STEP_SUMMARY"
  echo '```' >> "$GITHUB_STEP_SUMMARY"
  exit "$result"
fi
cat "$log"
