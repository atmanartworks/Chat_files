# Git Setup and Push Guide

## Step 1: Git Repository Initialize Pannunga

Project root folder la (chat-with-files) terminal open pannunga:

```bash
cd "C:\atman projects\chat-with-files"
git init
```

## Step 2: Files Add Pannunga

```bash
# All files add pannunga
git add .

# Or specific files add pannunga
git add backend/
git add frontend/
git add .gitignore
```

## Step 3: First Commit

```bash
git commit -m "Initial commit: FounderGPT backend and frontend"
```

## Step 4: GitHub Repository Create

1. GitHub.com la login pannunga
2. "New Repository" click pannunga
3. Repository name: `foundergpt` (or your preferred name)
4. Public or Private select pannunga
5. "Create repository" click pannunga
6. **Important**: README, .gitignore, license add pannadhinga (already irukku)

## Step 5: Remote Add Pannunga

GitHub la repository create aagumbodhu, intha commands run pannunga:

```bash
# Your GitHub username and repository name use pannunga
git remote add origin https://github.com/YOUR_USERNAME/foundergpt.git

# Or SSH use pannalam
git remote add origin git@github.com:YOUR_USERNAME/foundergpt.git
```

## Step 6: Push Pannunga

```bash
# Main branch ku push pannunga
git branch -M main
git push -u origin main
```

## Important Notes

### Files Git la Add Pannadha:
- `.env` files (sensitive data)
- `venv/` folder (virtual environment)
- `node_modules/` (frontend dependencies)
- `*.db` files (database files)
- `uploads/` folder (user uploaded files)
- `generated_pdfs/` folder (generated PDFs)
- `__pycache__/` folders

### Files Git la Add Pannanum:
- All source code files (`.py`, `.jsx`, `.css`, etc.)
- `requirements.txt`
- `package.json`
- `render.yaml`
- `Procfile`
- Documentation files (`.md`)
- Configuration files

## Quick Commands Summary

```bash
# 1. Initialize
git init

# 2. Add files
git add .

# 3. Commit
git commit -m "Initial commit"

# 4. Add remote (GitHub repository URL)
git remote add origin https://github.com/YOUR_USERNAME/foundergpt.git

# 5. Push
git branch -M main
git push -u origin main
```

## Troubleshooting

### "fatal: not a git repository"
- `git init` run pannunga project root folder la

### "remote origin already exists"
- `git remote remove origin` run pannunga
- Then again `git remote add origin` run pannunga

### "Permission denied"
- GitHub credentials check pannunga
- Personal Access Token use pannunga

## Next Steps After Push

1. Render dashboard la repository connect pannunga
2. Deployment start pannunga
3. Environment variables set pannunga
