# hcl-dataset-tools

This toolkit is designed for analyzing and processing the `terrads` database of Terraform repositories.

## Folder Structure

* **`data/dataset.sqlite`**
* The main SQLite database containing repository data.

* **`RepoList.sql`**
* A SQL script used to identify the dominant cloud provider (**AWS**, **GCP**, or **Azure**) for each repository.
* Exports a list of `CloneUrl` and `RepositoryId`, categorized by provider.

* **`mining.py`**
* A script designed to run **Checkov** analysis on the repositories.

* **`just`**
* Modified for Windows PowerShell compatibility.
* Includes improved environment variable handling and better integration with `dotnet`, `just`, `go`, and `gcc`.
* Updates included for database path handling.

* **`finalize_db.py`**
* A script to vacuum the database, drop unnecessary views or tables, and optimize the overall file size.

* **`Screenshots`**
* A directory containing raw screenshots and basic analysis of the `terrads` data.

---

## Usage

1. **Generate Categories:**
Run `RepoList.sql` against `dataset.sqlite` to generate a categorized list of repositories by their dominant cloud provider.
2. **Run Analysis:**
Redundant file `mining.py` to perform the Checkov analysis.
3. **Cleanup:**
Run `finalize_db.py` to clean, compress, and optimize the database after processing is complete.
