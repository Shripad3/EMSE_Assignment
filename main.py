import sqlite3
import pandas as pd
import json
import glob
import os

# ======================================================
# 1️⃣ Load TerraDS (for contextual description only)
# ======================================================
db_path = r"/Users/shripad/Downloads/Empirical SWE Project Dataset.sqlite"
conn = sqlite3.connect(db_path)

repositories = pd.read_sql("SELECT * FROM Repositories", conn)
modules = pd.read_sql("SELECT * FROM Modules", conn)
resources = pd.read_sql("SELECT * FROM Resources", conn)

conn.close()

print("✅ TerraDS loaded:")
print(f"Repositories: {len(repositories)}")
print(f"Modules: {len(modules)}")
print(f"Resources: {len(resources)}")

# ======================================================
# 2️⃣ Load Checkov JSON outputs
# ======================================================
checkov_dir = r"repos/checkov_outputs"
checkov_files = glob.glob(os.path.join(checkov_dir, "*.json"))

print(f"Checkov files found: {checkov_files}")

all_findings = []

for f in checkov_files:
    repo_name = os.path.basename(f).replace(".json", "").strip().lower()

    with open(f, "r") as file:
        data = json.load(file)

        failed_checks = data.get("results", {}).get("failed_checks", [])

        for result in failed_checks:
            all_findings.append({
                "repository_name": repo_name,
                "resource_type": result.get("resource", "").strip().lower(),
                "check_id": result.get("check_id", ""),
                "category": result.get("check_class", "")
            })

checkov_df = pd.DataFrame(all_findings)

print("\n✅ Checkov parsing complete")
print("Columns:", checkov_df.columns.tolist())
print("Total violations:", len(checkov_df))
print(checkov_df.head())

# ======================================================
# 3️⃣ RQ1 – Repository-level security violations
# ======================================================
rq1_repo_metrics = (
    checkov_df
    .groupby("repository_name")
    .agg(
        total_violations=("check_id", "count"),
        affected_resources=("resource_type", "nunique")
    )
    .reset_index()
)

rq1_repo_metrics.to_csv("rq1_repo_metrics.csv", index=False)

print("\n✅ RQ1 complete: rq1_repo_metrics.csv generated")

# ======================================================
# 4️⃣ RQ2 – Resource-type security violations
# ======================================================
rq2_resource_metrics = (
    checkov_df
    .groupby("resource_type")
    .agg(
        total_violations=("check_id", "count"),
        repo_count=("repository_name", "nunique")
    )
    .reset_index()
    .sort_values(by="total_violations", ascending=False)
)

rq2_resource_metrics.to_csv("rq2_resource_metrics_global.csv", index=False)

print("✅ RQ2 complete: rq2_resource_metrics_global.csv generated")

# ======================================================
# 5️⃣ Top-10 resource types (for reporting)
# ======================================================
top10_resources = rq2_resource_metrics.head(10)
top10_resources.to_csv("top10_resources.csv", index=False)

print("\n🏁 Pipeline finished successfully")
