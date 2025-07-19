"""Tests for module CRUD operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_module
from app.models.module import Module
from app.schemas.module import ModuleCreate, ModuleUpdate


class TestModuleCRUD:
    """Test cases for Module CRUD operations."""

    @pytest.fixture
    async def test_module(self, db_session: AsyncSession, test_user):
        """Create a test module for use in tests."""
        module = Module(
            machine_name="test_module",
            display_name="Test Module",
            module_type="contrib",
            is_covered=True,
            is_active=True,
            created_by=test_user.id,
            updated_by=test_user.id,
        )
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        return module

    async def test_get_module(self, db_session: AsyncSession, test_module):
        """Test getting a module by ID."""
        module = await crud_module.get_module(db_session, test_module.id)
        assert module is not None
        assert module.id == test_module.id
        assert module.machine_name == "test_module"

    async def test_get_module_not_found(self, db_session: AsyncSession):
        """Test getting a non-existent module."""
        module = await crud_module.get_module(db_session, 999999)
        assert module is None

    async def test_get_module_by_machine_name(self, db_session: AsyncSession, test_module):
        """Test getting a module by machine name."""
        module = await crud_module.get_module_by_machine_name(
            db_session, "test_module"
        )
        assert module is not None
        assert module.id == test_module.id
        assert module.machine_name == "test_module"

    async def test_get_modules_basic(self, db_session: AsyncSession, test_user):
        """Test getting a list of modules."""
        # Create test modules
        modules = []
        for i in range(5):
            module = Module(
                machine_name=f"module_{i}",
                display_name=f"Module {i}",
                module_type="contrib" if i % 2 == 0 else "core",
                is_covered=i % 2 == 0,
                is_active=True,
                created_by=test_user.id,
                updated_by=test_user.id,
            )
            modules.append(module)
            db_session.add(module)
        await db_session.commit()

        # Get all modules
        result = await crud_module.get_modules(db_session)
        # The result is a tuple (modules, total_count), so extract the modules list
        modules_list = result[0] if isinstance(result, tuple) else result
        # Count modules we just created (filter by machine_name pattern)
        created_modules = [m for m in modules_list if m.machine_name.startswith("module_")]
        assert len(created_modules) == 5

    async def test_create_module(self, db_session: AsyncSession, test_user):
        """Test creating a new module."""
        module_data = ModuleCreate(
            machine_name="new_module",
            display_name="New Module",
            module_type="contrib",
            drupal_org_link="https://drupal.org/project/new_module",
            is_covered=True,
        )
        
        module = await crud_module.create_module(
            db_session, module=module_data, created_by=test_user.id
        )
        
        assert module.id is not None
        assert module.machine_name == "new_module"
        assert module.display_name == "New Module"
        assert module.module_type == "contrib"
        # is_covered is not set by create_module, it defaults to False
        assert module.is_covered is False
        assert module.created_by == test_user.id

    async def test_update_module(self, db_session: AsyncSession, test_module):
        """Test updating a module."""
        # test_module starts with is_covered=True
        update_data = ModuleUpdate(
            display_name="Updated Module Name",
        )
        
        updated = await crud_module.update_module(
            db_session, module_id=test_module.id, module_update=update_data, updated_by=test_module.updated_by
        )
        
        assert updated.display_name == "Updated Module Name"
        assert updated.is_covered is True  # Should remain unchanged
        assert updated.machine_name == "test_module"  # Unchanged

    async def test_delete_module(self, db_session: AsyncSession, test_module):
        """Test soft deleting a module."""
        deleted = await crud_module.delete_module(
            db_session, module_id=test_module.id, updated_by=test_module.updated_by
        )
        
        assert deleted.is_deleted is True
        assert deleted.id == test_module.id
        
        # Verify it's not returned by get_module
        module = await crud_module.get_module(db_session, test_module.id)
        assert module is None