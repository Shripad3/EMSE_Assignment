import os
import subprocess
import json
import pandas as pd
import shutil
import time

# =====================================================
# CONFIGURATION
# =====================================================
REPO_CSV = "RepoList.csv"          # Input repo list
CLONE_DIR = "./temp_repos"              # Temp clone dir
OUTPUT_CSV = "checkov_results_specific.csv"      # Incremental output
CHECKOV_TIMEOUT = 300                   # 5 minutes per repo

# =====================================================
# HELPERS
# =====================================================
def run_checkov(repo_path):
    """Run Checkov and return failed checks"""
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
            return []

        output = json.loads(result.stdout)
        if isinstance(output, dict):
            output = [output]

        violations = []
        for scan in output:
            failed = scan.get("results", {}).get("failed_checks", [])
            for check in failed:
                violations.append({
                    "check_id": check.get("check_id"),
                    "check_name": check.get("check_name"),
                    "resource": check.get("resource"),
                    "file_path": check.get("file_path"),
                })

        return violations

    except subprocess.TimeoutExpired:
        print("⏱️ Checkov timeout")
        return []
    except Exception as e:
        print(f"⚠️ Checkov error: {e}")
        return []


# =====================================================
# MAIN
# =====================================================
def main():
    df_repos = pd.read_csv(REPO_CSV)
    os.makedirs(CLONE_DIR, exist_ok=True)

    # Write CSV header once
    if not os.path.exists(OUTPUT_CSV):
        pd.DataFrame(columns=[
            "RepoId",
            "CloudProvider",
            "check_id",
            "check_name",
            "resource",
            "file_path"
        ]).to_csv(OUTPUT_CSV, index=False)

    for idx, row in df_repos.iterrows():
        repo_id = row["RepoId"]
        clone_url = row["CloneUrl"]
        provider = row["CloudProvider"]

        print(f"\n📦 [{idx+1}/{len(df_repos)}] Processing Repo {repo_id} ({provider})")

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
        violations = run_checkov(repo_path)

        # --- Prepare rows ---
        rows = []

        if violations:
            for v in violations:
                rows.append({
                    "RepoId": repo_id,
                    "CloudProvider": provider,
                    **v
                })
        else:
            # Optional: keep repos with zero violations
            rows.append({
                "RepoId": repo_id,
                "CloudProvider": provider,
                "check_id": None,
                "check_name": None,
                "resource": None,
                "file_path": None
            })

        # --- Append incrementally ---
        pd.DataFrame(rows).to_csv(
            OUTPUT_CSV,
            mode="a",
            header=False,
            index=False
        )

        print(f"✅ Written {len(violations)} violations to CSV")

        # --- Cleanup ---
        shutil.rmtree(repo_path, ignore_errors=True)
        time.sleep(1)

    print("\n🎉 Mining finished!")
    print(f"Results saved incrementally in {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
