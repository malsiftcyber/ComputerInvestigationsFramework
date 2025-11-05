# Contributing to Computer Investigations Framework

Thank you for your interest in contributing to CIF! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and considerate
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Be patient with questions and suggestions

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include:
   - Clear description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or error messages

### Suggesting Features

1. Check existing feature requests
2. Use the feature request template
3. Describe:
   - Use case and motivation
   - Proposed solution
   - Alternatives considered
   - Impact on existing functionality

### Code Contributions

#### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/ComputerInvestigationsFramework.git
cd ComputerInvestigationsFramework

# Create a branch
git checkout -b feature/your-feature-name

# Setup development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
```

#### Coding Standards

- **Python**: Follow PEP 8 style guide
- **JavaScript**: Follow ESLint configuration
- **Documentation**: Update README and docstrings
- **Testing**: Add tests for new features

#### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add domain name detection to agents
fix: Fix WebSocket connection handling
docs: Update installation instructions
refactor: Improve file metadata collection
```

#### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests if applicable
5. Update documentation
6. Ensure all tests pass
7. Submit a pull request

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests pass

## Areas for Contribution

### High Priority

- Authentication and authorization
- HTTPS/TLS support
- Test coverage
- Documentation improvements
- Performance optimizations

### Feature Ideas

- File carving capabilities
- Timeline analysis
- Registry viewer (Windows)
- Event log viewer
- Reporting features
- Multi-user support

## Development Guidelines

### Backend Development

- Use Flask best practices
- Handle errors gracefully
- Add logging for debugging
- Document API endpoints

### Frontend Development

- Follow React best practices
- Use Material-UI components
- Ensure responsive design
- Add loading states

### Agent Development

- Cross-platform compatibility
- Error handling and logging
- Efficient file operations
- Security considerations

## Questions?

Feel free to open an issue for questions or reach out to maintainers.

Thank you for contributing! 🎉

