import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os


INPUT_CSV = "checkov_results_specific.csv"
OUT_DIR = "rq2_results"
TOP_N = 10

os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(INPUT_CSV)

print(f"Loaded {len(df)} Checkov violations")

def extract_resource_type(resource):
    if pd.isna(resource):
        return None
    parts = resource.split(".")
    return parts[-2] if len(parts) >= 2 else parts[0]

df["resource_type"] = df["resource"].apply(extract_resource_type)


df = df.dropna(subset=["resource_type"])


rq2_global = (
    df.groupby("resource_type")
      .size()
      .reset_index(name="ViolationCount")
      .sort_values("ViolationCount", ascending=False)
)

rq2_global.to_csv(
    os.path.join(OUT_DIR, "rq2_global_resource_violations.csv"),
    index=False
)

print("\nTop 10 resource types (global):")
print(rq2_global.head(TOP_N))


rq2_provider = (
    df.groupby(["CloudProvider", "resource_type"])
      .size()
      .reset_index(name="ViolationCount")
      .sort_values(["CloudProvider", "ViolationCount"], ascending=[True, False])
)

rq2_provider.to_csv(
    os.path.join(OUT_DIR, "rq2_resource_violations_by_provider.csv"),
    index=False
)

print("\nTop 10 resource types per provider:")
print(rq2_provider.groupby("CloudProvider").head(TOP_N))


plt.figure(figsize=(10, 6))
sns.barplot(
    data=rq2_global.head(TOP_N),
    x="ViolationCount",
    y="resource_type"
)
plt.title("Top 10 Terraform Resource Types by Security Violations (Global)")
plt.xlabel("Number of Violations")
plt.ylabel("Resource Type")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "rq2_top10_resources_global.png"))
plt.close()

for provider in df["CloudProvider"].unique():
    subset = rq2_provider[rq2_provider["CloudProvider"] == provider].head(TOP_N)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=subset,
        x="ViolationCount",
        y="resource_type"
    )
    plt.title(f"Top 10 Vulnerable Resource Types – {provider}")
    plt.xlabel("Number of Violations")
    plt.ylabel("Resource Type")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, f"rq2_top10_resources_{provider}.png"))
    plt.close()

print("\nRQ2 analysis complete.")
print(f"Results saved in folder: {OUT_DIR}")
