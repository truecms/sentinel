import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module


class TestModuleModel:
    """Test cases for the Module model."""

    @pytest.mark.asyncio
    async def test_create_module_success(self, db_session: AsyncSession):
        """Test creating a module with valid data."""
        module = Module(
            machine_name="views",
            display_name="Views",
            module_type="contrib",
            description="Create customized lists and queries from your database.",
        )

        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)

        assert module.id is not None
        assert module.machine_name == "views"
        assert module.display_name == "Views"
        assert module.module_type == "contrib"
        assert module.is_active is True
        assert module.is_deleted is False
        assert module.created_at is not None
        assert module.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_module_with_minimal_data(self, db_session: AsyncSession):
        """Test creating a module with only required fields."""
        module = Module(machine_name="custom_module", display_name="Custom Module")

        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)

        assert module.id is not None
        assert module.machine_name == "custom_module"
        assert module.display_name == "Custom Module"
        assert module.module_type == "contrib"  # Default value
        assert module.description is None
        assert module.drupal_org_link is None

    @pytest.mark.asyncio
    async def test_module_machine_name_unique_constraint(
        self, db_session: AsyncSession
    ):
        """Test that machine_name must be unique."""
        # Create first module
        module1 = Module(machine_name="duplicate_name", display_name="First Module")
        db_session.add(module1)
        await db_session.commit()

        # Try to create second module with same machine_name
        module2 = Module(machine_name="duplicate_name", display_name="Second Module")
        db_session.add(module2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_module_type_variations(self, db_session: AsyncSession):
        """Test different module types."""
        types_to_test = ["contrib", "custom", "core"]

        for i, module_type in enumerate(types_to_test):
            module = Module(
                machine_name=f"test_module_{i}",
                display_name=f"Test Module {i}",
                module_type=module_type,
            )
            db_session.add(module)

        await db_session.commit()

        # Verify all modules were created
        for i, module_type in enumerate(types_to_test):
            stmt = db_session.get(Module, i + 1)
            module = await stmt
            assert module.module_type == module_type

    @pytest.mark.asyncio
    async def test_module_with_drupal_org_link(self, db_session: AsyncSession):
        """Test creating a module with Drupal.org link."""
        module = Module(
            machine_name="webform",
            display_name="Webform",
            drupal_org_link="https://www.drupal.org/project/webform",
            _="Enables the creation of webforms and questionnaires.",
        )

        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)

        assert module.drupal_org_link == "https://www.drupal.org/project/webform"

    @pytest.mark.asyncio
    async def test_module_soft_delete(self, db_session: AsyncSession):
        """Test soft delete functionality."""
        module = Module(
            machine_name="soft_delete_test", display_name="Soft Delete Test"
        )

        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)

        # Mark as deleted
        module.is_deleted = True
        module.is_active = False
        await db_session.commit()

        assert module.is_deleted is True
        assert module.is_active is False

    @pytest.mark.asyncio
    async def test_module_string_representation(self, db_session: AsyncSession):
        """Test string representation of module."""
        module = Module(machine_name="test_repr", display_name="Test Representation")

        # The model should have a readable representation
        assert "test_repr" in str(module) or "Test Representation" in str(module)

    @pytest.mark.asyncio
    async def test_module_relationships_structure(self, db_session: AsyncSession):
        """Test that relationships are properly defined."""
        module = Module(_="relationship_test", display_name="Relationship Test")

        # Check that relationship attributes exist
        assert hasattr(module, "versions")
        assert hasattr(module, "site_modules")
        assert hasattr(module, "creator")
        assert hasattr(module, "updater")
