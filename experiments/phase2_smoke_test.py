import os
import sys
import subprocess
import time


def run_presmoke():
    print("=" * 60)
    print("Phase-2 Pre-Smoke Test")
    print("=" * 60)
    print()

    out_dir = "results/phase2_presmoke"
    os.makedirs(out_dir, exist_ok=True)

    start = time.time()

    cmd = [
        sys.executable, "-m", "experiments.phase2_runner",
        "presmoke",
    ]
    env = {**os.environ, "MAX_WORKERS": "4"}

    result = subprocess.run(cmd, env=env, cwd=os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))

    elapsed = time.time() - start

    print()
    print(f"Pre-smoke completed in {elapsed:.1f}s, exit code {result.returncode}")

    return result.returncode


def run_smoke():
    print("=" * 60)
    print("Phase-2 Smoke Test (full baseline + optimizer)")
    print("=" * 60)
    print()

    out_dir = "results/phase2_smoke"
    os.makedirs(out_dir, exist_ok=True)

    start = time.time()

    cmd = [
        sys.executable, "-m", "experiments.phase2_runner",
        "smoke",
    ]
    env = {**os.environ, "MAX_WORKERS": "4"}

    result = subprocess.run(cmd, env=env, cwd=os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))

    elapsed = time.time() - start

    print()
    print(f"Smoke completed in {elapsed:.1f}s, exit code {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    test_type = sys.argv[1] if len(sys.argv) > 1 else "presmoke"

    if test_type == "presmoke":
        sys.exit(run_presmoke())
    elif test_type == "smoke":
        sys.exit(run_smoke())
    else:
        print(f"Unknown test type: {test_type}")
        print("Usage: python -m experiments.phase2_smoke_test [presmoke|smoke]")
        sys.exit(1)
