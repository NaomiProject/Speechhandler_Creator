# publisher.py
import os
import time
import subprocess
from github import Github
from storage import read_plugin_info, write_plugin_info


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stderr}")
    return p.stdout.strip()


def _safe_branch(s: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in s).strip("-") or "add-plugin"


def _ensure_remote(cwd, name, url):
    try:
        run(["git", "remote", "get-url", name], cwd=cwd)
        run(["git", "remote", "set-url", name, url], cwd=cwd)
    except RuntimeError:
        run(["git", "remote", "add", name, url], cwd=cwd)


def _ensure_fork(token, username):
    """Ensure user has a fork of NaomiProject/naomi-plugins. Returns clone SSH URL."""
    g = Github(token)
    upstream = g.get_repo("NaomiProject/naomi-plugins")
    try:
        fork = g.get_user().get_repo("naomi-plugins")
    except Exception:
        fork = None
    if not fork:
        upstream.create_fork()
        # wait until fork becomes available
        for _ in range(30):
            try:
                fork = g.get_user().get_repo("naomi-plugins")
                break
            except Exception:
                time.sleep(2)
        if not fork:
            raise RuntimeError("Timed out waiting for fork creation.")
    return fork.ssh_url


def _ensure_plugin_repo(plugin_folder, token, username):
    """
    Make sure the plugin folder is a git repo, remote points to user's GitHub,
    push to main; update plugin.info's repo_url if we had to create a new repo,
    and COMMIT that change immediately.
    Returns (plugin_name, repo_ssh_url, license, latest_commit_sha)
    """
    cfg, info_path = read_plugin_info(plugin_folder)
    name = cfg["plugin"].get("Name", "").strip()
    license_text = cfg["plugin"].get("License", "MIT").strip()
    repo_url = cfg["plugin"].get("URL", "").strip()

    if not name:
        raise RuntimeError("plugin.info missing 'Name'.")

    g = Github(token)
    user = g.get_user()

    # Ensure .git
    if not os.path.exists(os.path.join(plugin_folder, ".git")):
        run(["git", "init"], cwd=plugin_folder)

    repo = None
    if repo_url:
        # derive repo name from URL
        base = os.path.basename(repo_url)
        reponame = base[:-4] if base.endswith(".git") else base
        try:
            repo = user.get_repo(reponame)
        except Exception:
            repo = None
    else:
        # create new repo if missing
        reponame = "".join(ch for ch in name if ch.isalnum() or ch in "-_").strip() or "naomi-plugin"
        try:
            repo = user.get_repo(reponame)
        except Exception:
            repo = None
        if not repo:
            repo = user.create_repo(reponame, private=False, auto_init=False)
        repo_url = repo.ssh_url
        # write repo_url into plugin.info and COMMIT it immediately
        cfg["plugin"]["repo_url"] = repo_url
        write_plugin_info(cfg, info_path)
        run(["git", "add", "plugin.info"], cwd=plugin_folder)
        try:
            run(["git", "commit", "-m", "Set repo_url in plugin.info"], cwd=plugin_folder)
        except RuntimeError:
            # if file already committed unchanged, ignore
            pass

    # Ensure origin remote is correct
    _ensure_remote(plugin_folder, "origin", repo_url)

    # Commit all current work and push main
    run(["git", "add", "-A"], cwd=plugin_folder)
    try:
        run(["git", "commit", "-m", "Update plugin source"], cwd=plugin_folder)
    except RuntimeError:
        pass
    run(["git", "branch", "-M", "main"], cwd=plugin_folder)
    run(["git", "push", "-u", "origin", "main"], cwd=plugin_folder)

    # Latest commit SHA
    branch = repo.get_branch("main")
    sha = branch.commit.sha
    return name, repo_url, license_text, sha


def _ensure_local_plugins_index(username, token):
    """Clone or update user's fork of naomi-plugins into ./naomi-plugins and sync upstream."""
    target_dir = "naomi-plugins"
    if not os.path.exists(target_dir):
        fork_ssh = _ensure_fork(token, username)
        run(["git", "clone", fork_ssh, target_dir])

    cwd = os.path.abspath(target_dir)
    # Make sure upstream is set
    _ensure_remote(cwd, "upstream", "git@github.com:NaomiProject/naomi-plugins.git")

    run(["git", "fetch", "origin"], cwd=cwd)
    run(["git", "fetch", "upstream"], cwd=cwd)
    # default branch name can be master or main; check both
    default_branch = "master"
    try:
        run(["git", "rev-parse", "--verify", "upstream/master"], cwd=cwd)
    except RuntimeError:
        default_branch = "main"
        run(["git", "rev-parse", "--verify", "upstream/main"], cwd=cwd)

    run(["git", "checkout", "-B", default_branch, f"origin/{default_branch}"], cwd=cwd)
    run(["git", "merge", f"upstream/{default_branch}"], cwd=cwd)

    return cwd, default_branch


def publish_plugin_folder(plugin_folder, github_token, github_username):
    """
    1) Ensure plugin repo is up-to-date on user's GitHub (SSH), updating plugin.info repo_url & committing immediately if needed.
    2) Ensure local clone of user's fork of naomi-plugins is present and in sync with upstream.
    3) Create a branch, append line to plugins.csv with: name, repo_url, commit_sha, license.
    4) Push branch to user's fork and open PR (PyGithub) against NaomiProject/naomi-plugins.
    Returns PR URL.
    """
    name, repo_url, license_text, sha = _ensure_plugin_repo(plugin_folder, github_token, github_username)
    idx_dir, base_branch = _ensure_local_plugins_index(github_username, github_token)

    branch_name = _safe_branch(f"add-{name}")
    run(["git", "checkout", "-B", branch_name], cwd=idx_dir)

    csv_path = os.path.join(idx_dir, "plugins.csv")
    line = f"{name},{repo_url},{sha},{license_text}\n"
    with open(csv_path, "a", encoding="utf-8") as f:
        f.write(line)

    run(["git", "add", "plugins.csv"], cwd=idx_dir)
    run(["git", "commit", "-m", f"Add {name} plugin"], cwd=idx_dir)
    run(["git", "push", "origin", branch_name], cwd=idx_dir)

    g = Github(github_token)
    upstream = g.get_repo("NaomiProject/naomi-plugins")
    pr = upstream.create_pull(
        title=f"Add {name} plugin",
        body=f"Registering plugin **{name}**\n\n- Repo: {repo_url}\n- Commit: `{sha}`\n- License: {license_text}",
        head=f"{github_username}:{branch_name}",
        base=base_branch
    )
    return pr.html_url


def _read_plugin_info(folder):
    cfg, _ = read_plugin_info(folder)
    return {
        "name": cfg["plugin"].get("name", ""),
        "repo_url": cfg["plugin"].get("repo_url", ""),
        "license": cfg["plugin"].get("license", ""),
    }
