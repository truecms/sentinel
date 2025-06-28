Cursor Rules
============

Available Rules
--------------
1. api-standards: RESTful API design and documentation standards
2. build-optimization: Webpack/Vite configuration and build process optimization
3. git-commit-standards: Enforce structured Git commit messages
4. javascript-standards: Standards for JavaScript development in Drupal
5. php-drupal-best-practices: PHP & Drupal Development Standards and Best Practices
6. python-fastapi-best-practices: Best practices for FastAPI
7. security-practices: Security best practices for PHP, JavaScript, and Drupal
8. test-debugging-rules: Comprehensive guidelines for test debugging and optimization
9. third-party-integration: Standards for integrating external services

Rule Format
----------
Each rule should be defined in a markdown file under the .cursor/rules directory with the following structure:

1. Clear title and description
2. Detailed sections with examples
3. Code snippets where applicable
4. Best practices and guidelines
5. Common pitfalls to avoid

Example Rule Structure:
```markdown
Rule Title
=========

1. Overview
----------
Brief description of the rule's purpose

2. Guidelines
------------
- Guideline 1
- Guideline 2

3. Examples
----------
```code
example code
```

4. Best Practices
---------------
- Practice 1
- Practice 2
```

Creating New Rules
-----------------
1. Create a new .md file in .cursor/rules/
2. Follow the rule format structure
3. Include practical examples
4. Add to the available rules list
5. Update documentation references 