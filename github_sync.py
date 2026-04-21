import subprocess
import os
import sys

def run_command(command, env=None):
    process = subprocess.Popen(command, shell=True, env=env)
    process.wait()
    return process.returncode

def load_env():
    env_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val = parts[1].strip()
                        env_vars[key] = val
    return env_vars

def sync():
    print("[GitHub Sync]: Loading local credentials...")
    env = load_env()
    
    user = env.get("GITHUB_USERNAME")
    token = env.get("GITHUB_TOKEN")
    repo = env.get("GITHUB_REPO_NAME", "WikiHow-Project")
    email = env.get("GITHUB_EMAIL")

    if not all([user, token, email]):
        print("[Error]: Missing GITHUB_USERNAME, GITHUB_TOKEN, or GITHUB_EMAIL in .env")
        sys.exit(1)

    print(f"[GitHub Sync]: Authenticating as {user}...")
    
    # 1. Set local git identity (just in case they missed it)
    run_command(f'git config user.name "{user}"')
    run_command(f'git config user.email "{email}"')

    # 2. Construct Authenticated URL
    # Format: https://<user>:<token>@github.com/<user>/<repo>.git
    remote_url = f"https://{user}:{token}@github.com/{user}/{repo}.git"

    # 3. Handle Remote
    print("[GitHub Sync]: Setting up remote...")
    run_command("git remote remove origin")
    run_command(f"git remote add origin {remote_url}")

    # 4. Push
    print("[GitHub Sync]: Pushing to private repository...")
    # Get current branch
    branch_process = subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=True)
    branch = branch_process.decode().strip()
    
    res = run_command(f"git push -u origin {branch} --force")
    
    if res == 0:
        print("\n" + "="*40)
        print(" SUCCESS: Project synced to GitHub!")
        print(f" URL: https://github.com/{user}/{repo}")
        print("="*40)
    else:
        print("\n[Error]: Push failed. Check your token permissions or repository existence.")

if __name__ == "__main__":
    sync()
