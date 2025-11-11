# Auto-commit and push changes

Automatically commits and pushes all staged changes to the current branch.

## Usage

```
/auto-commit "commit message here"
```

## What it does

1. Stages all changes (`git add -A`)
2. Creates a commit with your message
3. Pushes to origin (current branch)
4. Shows git log of last 5 commits

## Examples

```
/auto-commit "Fix: Resolve scheduler crash"
/auto-commit "docs: Add deployment guide"
/auto-commit "refactor: Simplify code"
```

## Notes

- Message is required
- All uncommitted changes will be staged and committed
- Pushes to the current branch (usually main)
- No confirmation needed
