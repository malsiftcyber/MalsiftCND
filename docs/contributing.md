# Contributing to MalsiftCND

Thank you for your interest in contributing to MalsiftCND! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git
- PostgreSQL 15+
- Redis 7+

### Development Setup

1. **Fork the repository:**
   ```bash
   git clone https://github.com/your-username/MalsiftCND.git
   cd MalsiftCND
   ```

2. **Set up development environment:**
   ```bash
   # Run setup script
   ./scripts/setup.sh
   
   # Or manually
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure development settings:**
   ```bash
   cp env.example .env
   # Edit .env with development settings
   ```

4. **Initialize database:**
   ```bash
   python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

5. **Start development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Development Guidelines

### Code Style

**Python Code Style:**
- Follow PEP 8
- Use Black for formatting
- Use flake8 for linting
- Use mypy for type checking

**Formatting:**
```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy .
```

**Code Organization:**
- Keep functions small and focused
- Use descriptive variable names
- Add docstrings to all functions and classes
- Follow the existing project structure

### Testing

**Running Tests:**
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_scanners.py

# Run with coverage
pytest --cov=app tests/
```

**Writing Tests:**
- Write tests for all new functionality
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

**Test Structure:**
```python
import pytest
from unittest.mock import Mock, patch

class TestScanner:
    def test_scan_success(self):
        """Test successful scan execution."""
        # Arrange
        scanner = NmapScanner()
        target = ScanTarget(ip="127.0.0.1")
        
        # Act
        result = await scanner.scan(target)
        
        # Assert
        assert result.success is True
        assert result.data is not None
```

### Documentation

**Code Documentation:**
- Add docstrings to all functions and classes
- Include parameter and return type information
- Provide usage examples for complex functions

**API Documentation:**
- Update API documentation for new endpoints
- Include request/response examples
- Document error conditions

**User Documentation:**
- Update user manual for new features
- Add troubleshooting information
- Include configuration examples

## Contribution Process

### Submitting Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
   ```bash
   # Run tests
   pytest
   
   # Check code style
   black .
   flake8 .
   mypy .
   
   # Test manually
   uvicorn app.main:app --reload
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

5. **Push and create pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Guidelines

**Before submitting:**
- Ensure all tests pass
- Update documentation
- Add changelog entry
- Request review from maintainers

**Pull request template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] Manual testing completed
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changelog updated
```

### Code Review Process

**Review Criteria:**
- Code quality and style
- Test coverage
- Documentation completeness
- Security considerations
- Performance impact

**Review Process:**
1. Automated checks (CI/CD)
2. Maintainer review
3. Address feedback
4. Approval and merge

## Project Structure

### Directory Layout

```
MalsiftCND/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   ├── auth/              # Authentication
│   ├── core/              # Core functionality
│   ├── models/            # Database models
│   ├── scanners/          # Scanner implementations
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── tests/                  # Test files
├── docker-compose.yml      # Docker configuration
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
└── README.md             # Project overview
```

### Key Components

**Core Modules:**
- `app/core/config.py`: Configuration management
- `app/core/database.py`: Database setup
- `app/core/logging.py`: Logging configuration

**Scanner Modules:**
- `app/scanners/base.py`: Base scanner interface
- `app/scanners/nmap_scanner.py`: Nmap implementation
- `app/scanners/masscan_scanner.py`: Masscan implementation

**API Modules:**
- `app/api/v1/api.py`: Main API router
- `app/api/v1/endpoints/`: Individual endpoint modules

**Service Modules:**
- `app/services/scan_service.py`: Scan management
- `app/services/device_service.py`: Device management
- `app/services/data_aggregator.py`: Data processing

## Development Workflow

### Feature Development

1. **Plan the feature:**
   - Create issue describing the feature
   - Discuss implementation approach
   - Get approval from maintainers

2. **Implement the feature:**
   - Create feature branch
   - Implement functionality
   - Add tests
   - Update documentation

3. **Submit for review:**
   - Create pull request
   - Address review feedback
   - Get approval and merge

### Bug Fixes

1. **Report the bug:**
   - Create detailed issue
   - Include reproduction steps
   - Provide system information

2. **Fix the bug:**
   - Create bug fix branch
   - Implement fix
   - Add regression test
   - Update documentation

3. **Submit fix:**
   - Create pull request
   - Reference original issue
   - Get approval and merge

## Security Considerations

### Security Guidelines

**Code Security:**
- Validate all input data
- Use parameterized queries
- Implement proper authentication
- Follow OWASP guidelines

**Secret Management:**
- Never commit secrets to repository
- Use environment variables
- Implement proper key rotation
- Follow security best practices

**Vulnerability Reporting:**
- Report security issues privately
- Use security@malsift.com
- Follow responsible disclosure
- Do not create public issues

### Security Review Process

**Security Checklist:**
- [ ] Input validation implemented
- [ ] Authentication/authorization checked
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Secure communication (HTTPS)
- [ ] Secret management
- [ ] Error handling

## Performance Considerations

### Performance Guidelines

**Code Performance:**
- Use efficient algorithms
- Minimize database queries
- Implement caching where appropriate
- Profile performance-critical code

**Database Performance:**
- Use appropriate indexes
- Optimize queries
- Implement connection pooling
- Monitor query performance

**Network Performance:**
- Implement rate limiting
- Use connection pooling
- Optimize API responses
- Monitor network usage

### Performance Testing

**Load Testing:**
```bash
# Use tools like Apache Bench or wrk
ab -n 1000 -c 10 http://localhost:8000/api/v1/devices/
```

**Performance Monitoring:**
- Monitor response times
- Track resource usage
- Identify bottlenecks
- Optimize critical paths

## Release Process

### Version Management

**Version Numbering:**
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

**Release Process:**
1. Update version numbers
2. Update changelog
3. Create release tag
4. Build and test release
5. Deploy to staging
6. Deploy to production

### Changelog

**Changelog Format:**
```markdown
## [1.1.0] - 2024-01-15

### Added
- New scanner integration
- Enhanced AI analysis
- Improved API endpoints

### Changed
- Updated authentication system
- Improved performance

### Fixed
- Fixed scan timeout issues
- Resolved database connection problems

### Security
- Enhanced input validation
- Improved secret management
```

## Community Guidelines

### Code of Conduct

**Our Pledge:**
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect different viewpoints

**Unacceptable Behavior:**
- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks
- Inappropriate language

### Getting Help

**Support Channels:**
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: General questions and discussions
- Email: support@malsift.com for enterprise support

**Community Resources:**
- Documentation: Comprehensive guides and references
- Examples: Code examples and use cases
- Tutorials: Step-by-step guides

## License

By contributing to MalsiftCND, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation
- Community acknowledgments

Thank you for contributing to MalsiftCND!
