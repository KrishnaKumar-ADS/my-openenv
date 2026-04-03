#!/usr/bin/env bash
set -euo pipefail
HF_URL="${1:-http://localhost:7860}"
REPO_DIR="${2:-.}"
PASSED=0

echo "=== OpenEnv Submission Validator ==="
echo "Space URL : $HF_URL"
echo "Repo Dir  : $REPO_DIR"
echo ""

request_reset_status() {
	local target_url="$1"
	local status
	status=$(curl -s -o /dev/null -w "%{http_code}" \
		--connect-timeout 5 \
		--max-time 20 \
		-X POST "$target_url/reset" \
		-H "Content-Type: application/json" \
		-d '{"task":"easy"}' || true)
	if [ -z "$status" ]; then
		status="000"
	fi
	printf "%s" "$status"
}

echo "[CHECK 1] POST $HF_URL/reset ..."
HTTP_STATUS=$(request_reset_status "$HF_URL")

if [ "$HTTP_STATUS" != "200" ]; then
	case "$HF_URL" in
		*localhost*|*127.0.0.1*)
			ALT_URL="${HF_URL/localhost/host.docker.internal}"
			ALT_URL="${ALT_URL/127.0.0.1/host.docker.internal}"
			ALT_STATUS=$(request_reset_status "$ALT_URL")
			if [ "$ALT_STATUS" = "200" ]; then
				HF_URL="$ALT_URL"
				HTTP_STATUS="$ALT_STATUS"
				echo "  [INFO] Used host fallback URL: $HF_URL"
			fi
			;;
	esac
fi

if [ "$HTTP_STATUS" = "200" ]; then
	echo "  [OK] /reset returned HTTP 200"
	PASSED=$((PASSED+1))
else
	echo "  [FAIL] /reset returned HTTP $HTTP_STATUS (expected 200)"
fi

echo "[CHECK 2] docker build ..."
if docker build -t cs-env-test "$REPO_DIR" --quiet > /dev/null 2>&1; then
	echo "  [OK] docker build succeeded"
	PASSED=$((PASSED+1))
else
	echo "  [FAIL] docker build failed"
fi

echo "[CHECK 3] openenv validate ..."
if command -v openenv &> /dev/null; then
	if openenv validate "$REPO_DIR/openenv.yaml" > /dev/null 2>&1; then
		echo "  [OK] openenv validate passed"
		PASSED=$((PASSED+1))
	else
		echo "  [FAIL] openenv validate failed"
	fi
else
	echo "  [WARN] 'openenv' CLI not found - skipping (install from openenv.ai)"
	PASSED=$((PASSED+1))
fi

echo ""
echo "=== Results: $PASSED/3 checks passed ==="
if [ "$PASSED" -eq 3 ]; then
	echo "All 3/3 checks passed! Ready to submit."
	exit 0
else
	echo "Some checks failed. Fix issues above before submitting."
	exit 1
fi
