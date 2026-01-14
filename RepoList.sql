WITH RepoStats AS (
    -- Count resources per provider for each repository
    -- We assume 'aws', 'google', 'azurerm' are the standard Terraform provider names
    SELECT 
        m.RepositoryId,
        CASE 
            WHEN r.Provider LIKE '%aws%' THEN 'AWS'
            WHEN r.Provider LIKE '%google%' THEN 'GCP'
            WHEN r.Provider LIKE '%azure%' THEN 'Azure'
            ELSE 'Other'
        END AS CloudProvider,
        COUNT(*) as ResourceCount
    FROM Modules m
    JOIN Resources r ON m.Id = r.ModuleId
    GROUP BY m.RepositoryId, CloudProvider
),
DominantProvider AS (
    -- Determine the dominant provider for each repo
    SELECT 
        RepositoryId,
        CloudProvider,
        ResourceCount,
        ROW_NUMBER() OVER (PARTITION BY RepositoryId ORDER BY ResourceCount DESC) as rn
    FROM RepoStats
    WHERE CloudProvider IN ('AWS', 'GCP', 'Azure') -- Filter out random providers
)
-- Final Selection: Get Repositories and their Clone URLs
SELECT 
    r.Id as RepoId,
    r.Name,
    r.CloneUrl,
    dp.CloudProvider,
    dp.ResourceCount as TotalResources
FROM Repositories r
JOIN DominantProvider dp ON r.Id = dp.RepositoryId
WHERE dp.rn = 1 -- Select only the top provider for that repo
AND dp.ResourceCount > 5 -- Optional: Filter out trivial "hello world" projects
ORDER BY dp.CloudProvider, dp.ResourceCount DESC;
