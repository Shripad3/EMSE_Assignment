import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from scikit_posthocs import posthoc_dunn


try:
    df_violations = pd.read_csv("checkov_results.csv")
    df_meta = pd.read_csv("RepoList.csv") 
except FileNotFoundError as e:
    print(f"Error: Could not find file. {e}")
    exit()
violation_counts = df_violations.groupby('RepoId').size().reset_index(name='TotalViolations')

df_final = pd.merge(
    df_meta,
    violation_counts,
    left_on="RepoId",   # Column name in RepoList.csv
    right_on="RepoId",  # Column name in checkov_results.csv
    how="left"
)


df_final["TotalViolations"] = df_final["TotalViolations"].fillna(0)


df_final = df_final[df_final["TotalResources"] > 0]
df_final["DefectDensity"] = df_final["TotalViolations"] / df_final["TotalResources"]


print("\nDescriptive statistics (Defect Density):")
print(df_final.groupby("CloudProvider")["DefectDensity"].describe())


groups = [
    df_final[df_final["CloudProvider"] == p]["DefectDensity"]
    for p in ["AWS", "GCP", "Azure"]
    if p in df_final["CloudProvider"].unique()
]

if len(groups) < 2:
    print("Not enough data groups to run statistics.")
else:
    stat, p_value = stats.kruskal(*groups)

    print(f"\nKruskal–Wallis Test:")
    print(f"Statistic = {stat:.4f}, p-value = {p_value:.6e}")

    if p_value < 0.05:
        print("Statistically significant differences detected!")
        
        # Post-hoc Test
        posthoc = posthoc_dunn(
            df_final,
            val_col="DefectDensity",
            group_col="CloudProvider",
            p_adjust="bonferroni"
        )

        print("\nPost-hoc Dunn test (Bonferroni-corrected p-values):")
        print(posthoc)
    else:
        print("No statistically significant difference detected.")

plt.figure(figsize=(10, 6))
sns.boxplot(
    x="CloudProvider",
    y="DefectDensity",
    data=df_final,
    showfliers=False
)

plt.title("Security Violation Density by Cloud Provider")
plt.ylabel("Violations per Resource")
plt.xlabel("Cloud Provider")
plt.tight_layout()
plt.show()