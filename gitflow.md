

I'll guide you through creating a new feature using GitFlow workflow. Here are the steps:

1. First, make sure you have GitFlow initialized in your repository:
```bash
# If GitFlow is not installed
brew install git-flow  # For macOS
# or
apt-get install git-flow  # For Ubuntu

# Initialize GitFlow in your repository
git flow init
```

2. Create a new feature branch:
```bash
# Format: git flow feature start <feature-name>
git flow feature start circuit-breaker-implementation
```

3. Work on your feature. Make commits as needed:
```bash
# Add your changes
git add .

# Commit with meaningful message
git commit -m "feat: implement circuit breaker pattern
- Add circuit breaker handler
- Add failure simulator
- Add test routes for circuit breaker
- Update documentation"
```

4. If you need to pull the latest changes from develop:
```bash
git checkout develop
git pull
git checkout feature/circuit-breaker-implementation
git rebase develop
```

5. When feature is complete, finish the feature:
```bash
git flow feature finish circuit-breaker-implementation
```

This will:
- Merge feature/circuit-breaker-implementation into develop
- Delete the feature branch
- Switch back to develop branch

6. Push to remote:
```bash
git push origin develop
```

Optional: If you're working with pull requests:
```bash
# Instead of using git flow feature finish, you can:
git push origin feature/circuit-breaker-implementation

# Then create a pull request from feature/circuit-breaker-implementation to develop
```

Common GitFlow branch structure:
```plaintext
master (or main)
│
├── develop
│   │
│   ├── feature/circuit-breaker-implementation
│   ├── feature/another-feature
│   │
│   ├── release/1.0.0
│   │
│   └── hotfix/critical-bug
```

Useful GitFlow commands:
```bash
# Start a new feature
git flow feature start <feature-name>

# Finish a feature
git flow feature finish <feature-name>

# Start a release
git flow release start <version>

# Finish a release
git flow release finish <version>

# Start a hotfix
git flow hotfix start <hotfix-name>

# Finish a hotfix
git flow hotfix finish <hotfix-name>

# List all feature branches
git flow feature list
```

Best practices:
1. Use meaningful feature names
2. Keep features small and focused
3. Regularly sync with develop branch
4. Write clear commit messages
5. Document your changes
6. Add tests for new features

Example commit message format:
```bash
git commit -m "feat: implement circuit breaker pattern

- Add CircuitBreakerHandler class with state management
- Implement failure simulation for testing
- Add test routes for monitoring circuit state
- Update documentation with usage examples

Closes #123"
```

Would you like me to explain any part of the GitFlow process in more detail?