# Issue #4: Create standardized mock JSON input data for Drupal module submission testing

## Problem Statement

We need to establish standardized mock JSON input data that represents what Drupal modules will be sending to our monitoring platform. This data will serve multiple purposes:

1. **API Testing**: Enable comprehensive Postman/Newman testing with realistic payloads
2. **Development**: Provide consistent data structure for development and debugging
3. **Documentation**: Serve as reference for Drupal module developers integrating with our platform
4. **Maintenance**: Ensure data compatibility as our system evolves

## Sprint Planning Recommendation

Given the scope of this issue, I recommend breaking it across sprints:

### 🎯 Sprint 1 (Recommended Focus)
**Goal**: Get the minimal viable JSON structure working end-to-end

#### Deliverables:
1. **Variant 1 (Minimal) Implementation**
   - Finalize JSON structure for basic module reporting
   - Create 5-10 real Drupal module examples
   - Test with existing `/api/v1/modules/bulk` endpoint
   - Basic Postman tests

2. **Core Validation**
   - Validate against existing database models
   - Ensure authentication flow works
   - Test with 50+ modules payload

3. **Newman Integration**
   - Create mock JSON data files in `/examples/` directory
   - Configure Newman to read example data from files
   - Set up data-driven tests using mock JSON payloads
   - Ensure Newman CI pipeline uses the example data

4. **Initial Documentation**
   - Document Variant 1 structure
   - Basic integration example
   - Add to CLAUDE.md
   - Document how to run Newman tests with mock data

**Effort**: 1 sprint (achievable)


## Acceptance Criteria for Sprint 1

- [ ] Variant 1 JSON structure documented and working
- [ ] Successfully submit 50+ modules via bulk endpoint
- [ ] Postman collection includes Variant 1 examples
- [ ] Newman tests configured to use mock JSON data from `/examples/` directory
- [ ] All tests passing (manual testing acceptable)
- [ ] Basic README documentation added
- [ ] JSON examples stored in `/examples/` directory

## Example Structure (Variant 1 - Sprint 1 Focus)

```json
{
  "site": {
    "url": "https://example.com",
    "name": "Example Drupal Site",
    "token": "site-auth-token-123"
  },
  "drupal_info": {
    "core_version": "10.5.0",
    "php_version": "8.3.2",
    "ip_address": "195.12.13.14"
  },
  "modules": [
    {
      "machine_name": "views",
      "display_name": "Views",
      "module_type": "core",
      "enabled": true,
      "version": "10.1.6"
    },
    {
      "machine_name": "admin_toolbar",
      "display_name": "Admin Toolbar", 
      "module_type": "contrib",
      "enabled": true,
      "version": "3.4.2"
    }
  ]
}
```

## Definition of Done
- [ ] Code reviewed and approved
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Successfully tested with Newman
- [ ] No regression in existing endpoints

## Labels
`enhancement` `testing` `api` `documentation` `sprint-1`

## Assignees
_To be assigned_

## Milestone
Sprint 1

---

**Note**: This issue focuses on Sprint 1 deliverables to ensure achievable goals. The token field will be used to validate that submissions match authorized sites in our system.

## Related Issues to Create
- **Site Authentication Token System** - Implement token-based authentication to ensure data submissions match URL/token combinations and prevent malicious submissions
