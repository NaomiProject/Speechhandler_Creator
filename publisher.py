import csv
import tempfile
from github import Github
from pathlib import Path
import git

CSV_URL = "https://github.com/NaomiProject/naomi-plugins/blob/master/plugins.csv"

def publish_plugin(plugin_path, username, token):
    plugin_info_file = Path(plugin_path) / "plugin.info"
    if not plugin_info_file.exists():
        raise FileNotFoundError("plugin.info not found in the plugin folder.")

    # Load plugin.info into dict
    info = {}
    with open(plugin_info_file) as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                info[k] = v

    repo_name = info["name"]
    repo_url = f"https://github.com/{username}/{repo_name}"

    # Push plugin folder to GitHub
    local_repo = git.Repo.init(plugin_path)
    local_repo.git.add(A=True)
    local_repo.index.commit("Initial commit")
    origin = local_repo.create_remote('origin', repo_url)
    origin.push(refspec='master:master')

    # Authenticate to GitHub
    g = Github(token)
    repo = g.get_repo("NaomiProject/naomi-plugins")

    # Download CSV and add new entry
    csv_path = tempfile.mktemp(suffix=".csv")
    repo_csv = repo.get_contents("plugins.csv")
    with open(csv_path, "w", newline="") as f:
        f.write(repo_csv.decoded_content.decode())

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            info["name"],
            info["description"],
            info["license"],
            repo_url,
            "speechhandler",
            "0.0.1",
            local_repo.head.commit.hexsha
        ])

    # Create new branch and PR
    branch_name = f"add-{repo_name}-plugin"
    base = repo.get_branch("master")
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base.commit.sha)

    repo.update_file(
        path="plugins.csv",
        message=f"Add {repo_name} plugin",
        content=open(csv_path).read(),
        sha=repo_csv.sha,
        branch=branch_name
    )

    pr = repo.create_pull(
        title=f"Add {repo_name} plugin",
        body=f"Adding {repo_name} to plugins.csv",
        head=branch_name,
        base="master"
    )

    return pr.html_url
