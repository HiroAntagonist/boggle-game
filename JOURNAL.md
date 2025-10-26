Lots of initialization today
I didnt realize that gh repo create created a commit so the commits collided. I think the right flow is to do a pull after a repo create

# Claude & Amritansh Learning Journal

## 2025-01-15: Week 1, Day 1 - Project Setup

### What we did
- Set up development environment from scratch
- Authenticated GitHub CLI and created private repo
- Configured Python with uv (modern package manager)
- Installed pytest, pytest-watch, and mypy for testing and type checking
- Set up mypy.ini for type safety (Python 3.12)
- Configured VSCode with Pylance, testing, and Python extensions
- Made 3 commits and pushed to GitHub
- Learned about git email privacy and fixed it

### What I learned
- `gh repo create` can create and connect a repo in one command
- uv is much faster than pip for package management
- Git can diverge when remote and local have different histories
- `git pull --rebase` replays local commits on top of remote
- `git commit --amend --reset-author` can fix commit metadata
- GitHub protects private email addresses automatically
- VSCode can auto-discover pytest tests

### Challenges/Issues
- Hit a git divergence issue when pushing (fixed with rebase)
- GitHub rejected push due to email privacy (fixed with no-reply email)

### Key Commands Learned
```bash
gh auth login                    # Authenticate GitHub CLI
gh repo create --private         # Create private repo and connect it
uv init                         # Initialize Python project
uv venv                         # Create virtual environment  
uv add --dev pytest mypy        # Add development dependencies
git pull --rebase origin main   # Rebase local commits on remote
git commit --amend --reset-author  # Fix commit author
```

### Blockers/Questions
- None - Day 1 complete!

### Next session
- Day 2: First TDD cycle - Board generation
- Write failing test for Board class
- Implement minimal code to pass
- Learn pytest basics and Python type hints

### Time spent
~45 minutes

### Reflection
Setting up the environment took some troubleshooting (git divergence, email privacy), but these were great learning moments. The tools (uv, gh CLI, VSCode) are much more modern than what I used in the early 2000s. Excited to start writing actual code tomorrow!

---
