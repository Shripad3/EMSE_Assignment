import os
import subprocess
import json
import pandas as pd
import shutil
import time

# =====================================================
# CONFIGURATION
# =====================================================
REPO_CSV = "RepoList.csv"        # Your input CSV
CLONE_DIR = "./temp_repos"
OUTPUT_CSV = "checkov_results.csv"
CHECKOV_TIMEOUT = 300  # seconds

# =====================================================
# CHECKOV RUNNER
# =====================================================
def count_checkov_violations(repo_path):
    """
    Runs Checkov and returns the number of failed checks
    """
    try:
        cmd = [
            "checkov",
            "-d", repo_path,
            "--framework", "terraform",
            "-o", "json",
            "--quiet"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=CHECKOV_TIMEOUT
        )

        if not result.stdout:
            return 0

        output = json.loads(result.stdout)

        if isinstance(output, dict):
            output = [output]

        count = 0
        for scan in output:
            failed = scan.get("results", {}).get("failed_checks", [])
            count += len(failed)

        return count

    except subprocess.TimeoutExpired:
        print("⏱️ Checkov timeout")
        return 0
    except Exception as e:
        print(f"⚠️ Checkov error: {e}")
        return 0


# =====================================================
# MAIN
# =====================================================
def main():
    df_repos = pd.read_csv(REPO_CSV)

    # Create output file with header if it does not exist
    if not os.path.exists(OUTPUT_CSV):
        pd.DataFrame(
            columns=["RepoId", "CloudProvider", "TotalViolations"]
        ).to_csv(OUTPUT_CSV, index=False)

    os.makedirs(CLONE_DIR, exist_ok=True)

    for _, row in df_repos.iterrows():
        repo_id = row["RepoId"]
        clone_url = row["CloneUrl"]
        provider = row["CloudProvider"]

        print(f"\n📦 Processing Repo {repo_id} ({provider})")

        repo_path = os.path.join(CLONE_DIR, str(repo_id))

        # --- Clone ---
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, repo_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=120
            )
        except Exception as e:
            print(f"⚠️ Clone failed: {e}")
            continue

        # --- Scan ---
        violation_count = count_checkov_violations(repo_path)

        # --- Append result immediately ---
        result_row = pd.DataFrame([{
            "RepoId": repo_id,
            "CloudProvider": provider,
            "TotalViolations": violation_count
        }])

        result_row.to_csv(
            OUTPUT_CSV,
            mode="a",
            header=False,
            index=False
        )

        print(f"✅ Violations found: {violation_count}")

        # --- Cleanup ---
        shutil.rmtree(repo_path, ignore_errors=True)

        time.sleep(1)

    print("\n🎉 Mining complete")
    print(f"Results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
