"""
User tests are split into multiple files for better organization and readability.
Please see the following files for specific test cases:

1. test_user_create.py - Creation and validation tests
2. test_user_read.py - Read/List-related tests
3. test_user_update.py - Update-related tests
4. test_user_delete.py - Delete-related tests
5. test_user_me.py - Current user profile tests
6. test_user_organization.py - Organization association tests
7. test_user_permissions.py - Permission and authorization tests
8. test_user_pagination.py - Pagination and filtering tests
"""

from .test_user_create import *
from .test_user_delete import *
from .test_user_me import *
from .test_user_organization import *
from .test_user_pagination import *
from .test_user_permissions import *
from .test_user_read import *
from .test_user_update import *
