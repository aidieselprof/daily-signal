param([string]$RepoName = "daily-signal")
git init
 git add .
 git commit -m "Initial commit — Money Autopilot v2"
 gh repo create $RepoName --public --source . --remote origin --push
