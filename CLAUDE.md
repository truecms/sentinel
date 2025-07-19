# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based monitoring and reporting platform providing REST API endpoints for user, organization, and site management with role-based access control (RBAC).

## Repository Information

- Github repository for this project: https://github.com/truecms/sentinel

## 📚 Documentation Index

### Development
- **Setup Guide**: `docs/claude/development/DEVELOPMENT_SETUP.md` - Environment setup, Docker configuration
- **Testing Guide**: `docs/claude/development/TESTING.md` - Unit tests, integration tests, coverage
- **Database Management**: `docs/claude/development/DATABASE_MANAGEMENT.md` - Migrations, PostgreSQL operations

### Architecture
- **API Design**: `docs/claude/architecture/API_DESIGN.md` - Design patterns, structure, best practices
- **Authentication**: `docs/claude/api/AUTHENTICATION.md` - JWT, Drupal site auth, RBAC

### Tools
- **Postman Testing**: `docs/claude/tools/POSTMAN_TESTING.md` - Newman, collections, CI/CD integration

### Troubleshooting
- **Common Issues**: `docs/claude/troubleshooting/COMMON_ISSUES.md` - Solutions to frequent problems

## Quick Start

```bash
# Start services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Access API documentation
# http://localhost:8000/docs
```

## Key Points

### Database
- Uses `postgres` database (NOT `application_db`)
- Alembic handles all migrations
- No manual table creation

### Authentication
- JWT tokens for users
- Site UUID + API Token for Drupal sites
- Module data only from authenticated sites

### Testing
- 80% minimum coverage required
- Dedicated test container
- Postman collection for API testing

## Common Pitfalls

1. **Database initialization**: The app uses the default `postgres` database
2. **Circular dependencies**: Comment out circular FKs in migrations
3. **Table creation conflicts**: Don't use `Base.metadata.create_all()`
4. **Module creation**: Only via authenticated Drupal site submissions

## Environment Variables

Key variables (see `.env.example`):
- `POSTGRES_DB=postgres` (default database)
- `JWT_SECRET_KEY` (generate secure key)
- `SUPERUSER_EMAIL/PASSWORD` (initial admin)

## Core Development Principles

### 1. Code Quality Standards
- **Immutable Rule:** All code must pass linting and type checking before commit
- **Testing Required:** Minimum 80% test coverage for new features
- **Documentation:** All public APIs must be documented
- **Security:** Never commit secrets, always use environment variables

### 2. Modular Command Structure
This project uses the Claude Code modular command system for consistent workflows:
- Commands are organized in `.claude/commands/` by category
- Each command follows XML-structured format for clarity
- Use `/[category]:[command]` syntax for execution
- Commands are environment-aware and security-focused

### 3. Emergency Procedures
- **Build Failures:** Run `/dev:debug-session` for systematic troubleshooting
- **Test Failures:** Use `/test:coverage-analysis` to identify issues
- **Deployment Issues:** Execute `/deploy:rollback-procedure` for emergency rollback
- **Security Concerns:** Immediately run security scans and notify team

## Command Categories

### Project Management
- `/project:create-feature` - Full feature development with tests and docs
- `/project:scaffold-component` - Component creation with boilerplate
- `/project:setup-environment` - Development environment initialization

### Development Workflow
- `/dev:code-review` - Structured code review with quality checks
- `/dev:refactor-analysis` - Code improvement recommendations
- `/dev:debug-session` - Systematic debugging and problem solving

### Testing
- `/test:generate-tests` - Comprehensive test suite generation
- `/test:coverage-analysis` - Test coverage assessment and improvement
- `/test:integration-tests` - Integration test creation and execution

### Deployment
- `/deploy:prepare-release` - Release preparation with quality gates
- `/deploy:deploy-staging` - Staging deployment with validation
- `/deploy:rollback-procedure` - Emergency rollback execution

### Documentation
- `/docs:api-docs` - API documentation generation
- `/docs:update-readme` - README maintenance and updates
- `/docs:architecture-review` - Architecture documentation and review

## Architecture Notes

### Key Components
- **[Component 1]:** [Brief description and location]
- **[Component 2]:** [Brief description and location]
- **[Component 3]:** [Brief description and location]

### Data Flow
[Describe how data flows through your system]

### External Dependencies
- **[Service 1]:** [Purpose and integration notes]
- **[Service 2]:** [Purpose and integration notes]

### Security Considerations
- Authentication: [Describe your auth system]
- Authorization: [Describe your permission system]
- Data Protection: [Describe your data handling]

## Quality Gates

### Pre-commit Requirements
- [ ] All tests pass
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Security scan clean
- [ ] Code coverage maintained

### Pre-deployment Requirements
- [ ] All quality gates pass
- [ ] Documentation updated
- [ ] Migration scripts tested
- [ ] Performance benchmarks met
- [ ] Security review complete

## Token Management

### Context Optimization
- Use progressive disclosure for large codebases
- Load commands just-in-time based on current task
- Clear context when switching between major tasks
- Monitor token usage and optimize accordingly

### Memory Management
- Leverage MCP memory server for session continuity
- Store architectural decisions in external documentation
- Use modular instructions to reduce token overhead
- Implement context compression for repeated patterns

## Team Conventions

### Git Workflow
- **Branch Naming:** `feat/feature-name`, `fix/bug-name`, `docs/doc-name`
- **Commit Messages:** Follow conventional commits format
- **Pull Requests:** Require review and all checks passing
- **Merging:** Squash commits for clean history

### Code Review Process
- Use `/dev:code-review` for automated analysis
- Focus on security, performance, and maintainability
- Require documentation for public APIs
- Ensure test coverage for new features

### Release Process
- Use `/deploy:prepare-release` for release preparation
- Follow semantic versioning
- Generate changelog automatically
- Deploy to staging first, then production

## Configuration

### Environment Variables
```bash
# Required environment variables
DATABASE_URL=postgresql://...
API_KEY=your-api-key
JWT_SECRET=your-jwt-secret

# Optional environment variables
LOG_LEVEL=info
REDIS_URL=redis://localhost:6379
```

### Feature Flags
[Document any feature flags or configuration options]

## Troubleshooting

### Common Issues
- **Issue 1:** [Description and solution]
- **Issue 2:** [Description and solution]
- **Issue 3:** [Description and solution]

### Debug Commands
- Use `/dev:debug-session` for systematic debugging
- Check logs: `npm run logs` or `yarn logs`
- Monitor performance: `npm run monitor` or `yarn monitor`

## Resources

### Documentation
- [API Documentation](./docs/api.md)
- [Architecture Guide](./docs/architecture.md)
- [Deployment Guide](./docs/deployment.md)

### External Resources
- [Technology Documentation](https://example.com)
- [Team Wiki](https://example.com)
- [Issue Tracker](https://example.com)
