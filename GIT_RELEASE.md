# Git Release Checklist ✅

## Before Your First Commit

### 1. Verify Sensitive Files Are Protected

Run this command to check if any sensitive files would be committed:

```bash
# Check what files Git would track
git status

# These files should NOT appear (already in .gitignore):
# ❌ .env
# ❌ credentials.json
# ❌ token.pickle
# ❌ data/local_events.json
# ❌ *.log files
# ❌ .venv/ folder
```

### 2. Required Example Files (Safe to Commit)

✅ `.env.example` - Template for environment variables
✅ `credentials.example.json` - Template for Google OAuth
✅ `data/local_events.example.json` - Example events data

### 3. Initialize Git Repository

```bash
# Initialize git (if not already done)
git init

# Add all files (sensitive ones are already excluded by .gitignore)
git add .

# Check what will be committed
git status

# Create initial commit
git commit -m "Initial commit: Personal Dashboard application"
```

### 4. Create Repository on GitHub/GitLab

```bash
# Add remote repository
git remote add origin https://github.com/yourusername/your-repo-name.git

# Push to remote
git branch -M main
git push -u origin main
```

## Files That WILL Be Committed (Safe ✅)

```
✅ app/                          # Application code
✅ scripts/                      # Utility scripts  
✅ tests/                        # Test files
✅ .env.example                  # Environment template
✅ credentials.example.json      # OAuth template
✅ data/local_events.example.json # Example data
✅ .gitignore                    # Git ignore rules
✅ requirements.txt              # Dependencies
✅ run.py                        # Entry point
✅ dashboard.py                  # Legacy dashboard
✅ chat_completion.py            # CLI tool
✅ README.md                     # Documentation
✅ SETUP.md                      # Setup guide
✅ *.md files                    # Other documentation
```

## Files That WILL NOT Be Committed (Protected 🔒)

```
🔒 .env                          # YOUR credentials
🔒 credentials.json              # YOUR Google OAuth
🔒 token.pickle                  # YOUR access tokens
🔒 data/local_events.json        # YOUR personal events
🔒 .venv/                        # Virtual environment
🔒 __pycache__/                  # Python cache
🔒 *.log                         # Log files
🔒 *.db, *.sqlite               # Database files
🔒 .vscode/, .idea/             # IDE settings
```

## Pre-Release Security Checklist

- [ ] `.env` file is in `.gitignore` ✅
- [ ] `credentials.json` is in `.gitignore` ✅
- [ ] `token.pickle` is in `.gitignore` ✅
- [ ] Personal data files are in `.gitignore` ✅
- [ ] `.env.example` has placeholder values only ✅
- [ ] No API keys in source code ✅
- [ ] `SECRET_KEY` in `.env.example` is a placeholder ✅
- [ ] Database files are excluded ✅

## Quick Verification Commands

```bash
# Show what Git will track
git ls-files

# Show ignored files (should include .env, credentials.json, etc.)
git status --ignored

# Check if .env or credentials.json would be committed
git check-ignore .env credentials.json token.pickle data/local_events.json
# Should output all these files (meaning they're ignored)

# Double-check no secrets in tracked files
git grep -i "password\|secret\|api.*key" -- "*.py" | grep -v "getenv\|env\|example"
# Should return nothing or only example references
```

## Post-Commit Verification

After your first commit, verify no secrets were committed:

```bash
# Check the commit
git log -1 --name-only

# Verify .env is not in the repository
git ls-files | grep -E "^\.env$|credentials\.json$|token\.pickle$"
# Should return nothing

# If you accidentally committed secrets:
# DON'T PANIC - follow GitHub's guide to remove sensitive data:
# https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
```

## Repository README

Make sure your repository includes:

1. ✅ Clear setup instructions (SETUP.md)
2. ✅ API key requirements (documented in .env.example)
3. ✅ Google Calendar setup guide
4. ✅ Example configuration files
5. ✅ Installation steps
6. ✅ Troubleshooting section

## For Contributors

If others will contribute, add `CONTRIBUTING.md`:

```markdown
# Contributing

## Setup for Development

1. Fork the repository
2. Clone your fork
3. Copy `.env.example` to `.env`
4. Add your API keys to `.env`
5. Install dependencies: `pip install -r requirements.txt`
6. Run tests: `pytest`
7. Start development server: `python run.py`

## Never Commit

- Your `.env` file
- Your `credentials.json`
- Any personal data files
- Log files

All sensitive files are already in `.gitignore`.
```

## Emergency: If You Committed Secrets

If you accidentally committed sensitive data:

```bash
# Remove file from Git but keep local copy
git rm --cached .env
git rm --cached credentials.json
git commit -m "Remove sensitive files from repository"

# Push changes
git push

# IMPORTANT: Still need to:
# 1. Rotate all exposed API keys immediately
# 2. Generate new credentials.json from Google Console
# 3. Update your .env with new keys
# 4. For complete removal, use git-filter-branch or BFG Repo Cleaner
```

## Ready to Publish? ✅

If all checks pass:

1. ✅ All sensitive files are in `.gitignore`
2. ✅ Example files have placeholder values
3. ✅ Documentation is complete
4. ✅ Setup instructions are clear
5. ✅ No secrets in tracked files

**You're ready to push to GitHub/GitLab! 🚀**

```bash
git push origin main
```

## After Publishing

1. Test the setup process on a fresh clone
2. Verify others can set up using only `.env.example`
3. Update README with actual repository URL
4. Consider adding a LICENSE file
5. Add badges (optional): build status, license, etc.

---

**Remember**: Once something is committed to Git, assume it's public forever. Always verify before pushing! 🔒
