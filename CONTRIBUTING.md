# Contributing to Qubee AI

Thank you for your interest in contributing to Qubee AI! This document provides guidelines for contributing to the project.

## Ways to Contribute

### 1. Report Bugs
- Use GitHub Issues to report bugs
- Include steps to reproduce
- Provide expected vs actual behavior
- Include your environment details (OS, Python version)

### 2. Suggest Features
- Open a GitHub Issue with the "enhancement" label
- Describe the feature and its benefits
- Explain use cases

### 3. Improve Documentation
- Fix typos or unclear explanations
- Add examples
- Translate documentation

### 4. Expand the Corpus
- Add more Afaan Oromo text sources
- Verify existing vocabulary
- Add domain-specific terms

### 5. Fix Bugs or Add Features
- Fork the repository
- Create a feature branch
- Make your changes
- Submit a pull request

## Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/qubee-ai.git
cd qubee-ai

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/test_spell_checker.py
```

## Code Style

- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic
- Keep functions focused and small

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Test edge cases
- Include both positive and negative test cases

```bash
# Run all tests
python tests/test_spell_checker.py

# Run specific test
python -m unittest tests.test_spell_checker.TestSpellCheckerAccuracy
```

## Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** with clear, descriptive commits
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Run tests** to ensure nothing breaks
6. **Submit pull request** with clear description

### PR Title Format
```
[Type] Brief description

Types: Fix, Feature, Docs, Test, Refactor, Perf
Example: [Feature] Add real-time spell checking
```

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## Corpus Contribution Guidelines

### Adding New Words
1. Ensure words are authentic Afaan Oromo
2. Use standard Qubee orthography
3. Include context (sentence examples)
4. Verify spelling with native speakers

### Text Sources
- Must be publicly available or properly licensed
- Prefer authoritative sources (news, books, academic)
- Include source attribution
- Remove personal information

## Grammar Rules

When adding new grammar rules:
1. Document the linguistic rule
2. Provide examples (correct and incorrect)
3. Add test cases
4. Consider edge cases
5. Avoid false positives

## Community Guidelines

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn

## Questions?

- Open a GitHub Discussion
- Check existing issues
- Read the documentation
- Contact maintainers

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in academic papers (if applicable)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make Afaan Oromo NLP tools better!** 🙏
