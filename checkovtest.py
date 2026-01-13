# import glob
# import os
# import json
# import pandas as pd

# checkov_dir = "/Users/shripad/terraform_repos/checkov_outputs"  # update to your path
# checkov_files = glob.glob(os.path.join(checkov_dir, "*.json"))

# print("Checkov files found:", checkov_files)

# all_findings = []

# for f in checkov_files:
#     print("Loading:", f)
#     repo_name = os.path.basename(f).replace('.json','').strip().lower()
#     with open(f) as file:
#         data = json.load(file)
#         failed_checks = data.get('results', {}).get('failed_checks', [])
#         for result in failed_checks:
#             resource_type = result.get('resource','').strip().lower()
#             all_findings.append({
#                 'repository_name': repo_name,
#                 'resource_type': resource_type,
#                 'check_id': result.get('check_id',''),
#                 'category': result.get('check_class','')
#             })

# checkov_df = pd.DataFrame(all_findings)
# print("Checkov columns:", checkov_df.columns.tolist())
# print("Number of findings loaded:", len(checkov_df))
# print(checkov_df.head())


import glob
checkov_dir = "/Users/shripad/Documents/Developer/Projects/Empirical_assignment/repos/checkov_outputs"
checkov_files = glob.glob(f"{checkov_dir}/*.json")
print("Checkov files found:", checkov_files)