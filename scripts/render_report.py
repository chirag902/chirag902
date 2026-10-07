name: Profile

on:
  push:
    branches: [main]
    paths: ["data/**", "scripts/**"]
  schedule:
    - cron: "0 */12 * * *"     # twice a day (UTC) for the releases table
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: profile
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Draw receipts card from data/evals.json
        run: python3 scripts/render_report.py

      - name: Refresh "Recently shipped" from real releases
        env:
          PROFILE_USER: ${{ github.repository_owner }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python3 scripts/sync_shipped.py

      - name: Commit only if something really changed
        run: |
          git add README.md assets
          if git diff --cached --quiet; then
            echo "Nothing to commit."
          else
            git config user.name  "profile-bot[bot]"
            git config user.email "profile-bot@users.noreply.github.com"
            git commit -m "chore(profile): sync card and shipped table"
            git push
          fi
