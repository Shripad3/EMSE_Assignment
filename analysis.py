import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from scikit_posthocs import posthoc_dunn

# ------------------------------
# 1. Load Data
# ------------------------------
try:
    # Use generic "checkov_results.csv" if that's what you have
    df_violations = pd.read_csv("checkov_results.csv")
    # Ensure this matches your actual file name (RepoList.csv vs repo_list.csv)
    df_meta = pd.read_csv("RepoList.csv") 
except FileNotFoundError as e:
    print(f"Error: Could not find file. {e}")
    exit()

# ------------------------------
# 2. Pre-Processing (The Fix)
# ------------------------------
# We must count the raw violations to get "TotalViolations"
# Group by RepoId and count the number of rows
violation_counts = df_violations.groupby('RepoId').size().reset_index(name='TotalViolations')

# Merge metadata with the calculated counts
df_final = pd.merge(
    df_meta,
    violation_counts,
    left_on="RepoId",   # Column name in RepoList.csv
    right_on="RepoId",  # Column name in checkov_results.csv
    how="left"
)

# Fill NaNs with 0 (meaning the repo was clean/had 0 violations)
df_final["TotalViolations"] = df_final["TotalViolations"].fillna(0)

# ------------------------------
# 3. Compute Defect Density
# ------------------------------
# Avoid division by zero
df_final = df_final[df_final["TotalResources"] > 0]
df_final["DefectDensity"] = df_final["TotalViolations"] / df_final["TotalResources"]

# ------------------------------
# A. Descriptive Statistics
# ------------------------------
print("\n📊 Descriptive statistics (Defect Density):")
print(df_final.groupby("CloudProvider")["DefectDensity"].describe())

# ------------------------------
# B. Statistical Significance Test
# ------------------------------
groups = [
    df_final[df_final["CloudProvider"] == p]["DefectDensity"]
    for p in ["AWS", "GCP", "Azure"]
    if p in df_final["CloudProvider"].unique()
]

if len(groups) < 2:
    print("Not enough data groups to run statistics.")
else:
    stat, p_value = stats.kruskal(*groups)

    print(f"\n📈 Kruskal–Wallis Test:")
    print(f"Statistic = {stat:.4f}, p-value = {p_value:.6e}")

    if p_value < 0.05:
        print("✅ Statistically significant differences detected!")
        
        # Post-hoc Test
        posthoc = posthoc_dunn(
            df_final,
            val_col="DefectDensity",
            group_col="CloudProvider",
            p_adjust="bonferroni"
        )

        print("\n🔎 Post-hoc Dunn test (Bonferroni-corrected p-values):")
        print(posthoc)
    else:
        print("❌ No statistically significant difference detected.")

# ------------------------------
# C. Visualization
# ------------------------------
plt.figure(figsize=(10, 6))
sns.boxplot(
    x="CloudProvider",
    y="DefectDensity",
    data=df_final,
    showfliers=False # Hide extreme outliers to make the chart readable
)

plt.title("Security Violation Density by Cloud Provider")
plt.ylabel("Violations per Resource")
plt.xlabel("Cloud Provider")
plt.tight_layout()
plt.show()