"""Integration tests for duratypes with Pydantic models."""

import pytest
from pydantic import BaseModel, ValidationError, Field
from typing import Optional, List

from duratypes import Duration, Seconds, Minutes, Hours, parse_duration


class SimpleTaskModel(BaseModel):
    """Simple model with a duration field."""
    name: str
    duration: Duration


class DetailedTaskModel(BaseModel):
    """Model with different duration types and constraints."""
    name: str
    estimated_duration: Duration = Field(description="Estimated time in seconds")
    timeout_seconds: Seconds = Field(gt=0, description="Timeout must be positive")
    break_minutes: Minutes = Field(default=15, description="Break time in minutes")
    max_hours: Hours = Field(le=24*3600, description="Max hours per day")  # 24 hours in seconds


class ProjectModel(BaseModel):
    """Complex model with nested duration fields."""
    name: str
    tasks: List[SimpleTaskModel]
    total_duration: Optional[Duration] = None

    def model_post_init(self, __context) -> None:
        """Calculate total duration from tasks."""
        if self.total_duration is None:
            self.total_duration = sum(task.duration for task in self.tasks)


class ConfigModel(BaseModel):
    """Model for configuration with various duration formats."""
    cache_ttl: Duration = Field(default=300, description="Cache time-to-live")  # 5m pre-parsed
    session_timeout: Duration = Field(default=1800)  # 30m pre-parsed
    cleanup_interval: Duration = Field(default=3600)  # 1h pre-parsed
    max_request_time: Duration = Field(default=30)  # 30s pre-parsed


class TestPydanticIntegration:
    """Test Pydantic integration with various model patterns."""

    def test_simple_model_creation(self):
        """Test creating simple models with duration fields."""
        task = SimpleTaskModel(name="Test Task", duration="30m")
        assert task.name == "Test Task"
        assert task.duration == 1800  # 30 minutes in seconds

        # Test with different formats
        task2 = SimpleTaskModel(name="Another Task", duration="1h30m")
        assert task2.duration == 5400  # 1.5 hours in seconds

        # Test with numeric input
        task3 = SimpleTaskModel(name="Numeric Task", duration=3600)
        assert task3.duration == 3600

    def test_detailed_model_validation(self):
        """Test model with field constraints and validation."""
        model = DetailedTaskModel(
            name="Complex Task",
            estimated_duration="2h30m",
            timeout_seconds="45s",
            break_minutes="10m",
            max_hours="8h"
        )

        assert model.estimated_duration == 9000  # 2.5 hours
        assert model.timeout_seconds == 45
        assert model.break_minutes == 600  # 10 minutes
        assert model.max_hours == 28800  # 8 hours

    def test_model_validation_errors(self):
        """Test that validation errors are properly raised."""
        # Test negative timeout (should fail gt=0 constraint)
        with pytest.raises(ValidationError) as exc_info:
            DetailedTaskModel(
                name="Bad Task",
                estimated_duration="1h",
                timeout_seconds="-30s",  # Negative value
                max_hours="8h"
            )

        error = exc_info.value
        assert "timeout_seconds" in str(error)

        # Test invalid duration format
        with pytest.raises(ValidationError) as exc_info:
            SimpleTaskModel(name="Bad Format", duration="invalid")

        error = exc_info.value
        assert "duration" in str(error)

    def test_nested_model_with_calculations(self):
        """Test complex model with nested duration fields."""
        project = ProjectModel(
            name="Test Project",
            tasks=[
                SimpleTaskModel(name="Task 1", duration="30m"),
                SimpleTaskModel(name="Task 2", duration="1h"),
                SimpleTaskModel(name="Task 3", duration="45m"),
            ]
        )

        # Total should be calculated automatically
        expected_total = 1800 + 3600 + 2700  # 30m + 1h + 45m
        assert project.total_duration == expected_total

        # Test with explicit total
        project2 = ProjectModel(
            name="Explicit Total",
            tasks=[SimpleTaskModel(name="Task", duration="1h")],
            total_duration="2h"
        )
        assert project2.total_duration == 7200  # Explicit value takes precedence

    def test_config_model_defaults(self):
        """Test model with default duration values."""
        config = ConfigModel()

        # Check defaults are parsed correctly
        assert config.cache_ttl == 300  # 5 minutes
        assert config.session_timeout == 1800  # 30 minutes
        assert config.cleanup_interval == 3600  # 1 hour
        assert config.max_request_time == 30  # 30 seconds

        # Test overriding defaults
        custom_config = ConfigModel(
            cache_ttl="10m",
            session_timeout="1h",
            cleanup_interval="2h",
            max_request_time="1m"
        )

        assert custom_config.cache_ttl == 600
        assert custom_config.session_timeout == 3600
        assert custom_config.cleanup_interval == 7200
        assert custom_config.max_request_time == 60

    def test_model_serialization(self):
        """Test that models serialize and deserialize correctly."""
        original = DetailedTaskModel(
            name="Serialization Test",
            estimated_duration="2h",
            timeout_seconds="30s",
            break_minutes="15m",
            max_hours="8h"
        )

        # Test dict serialization
        data = original.model_dump()
        assert data["estimated_duration"] == 7200
        assert data["timeout_seconds"] == 30
        assert data["break_minutes"] == 900
        assert data["max_hours"] == 28800

        # Test JSON serialization
        json_str = original.model_dump_json()
        assert "7200" in json_str
        assert "30" in json_str

        # Test deserialization
        recreated = DetailedTaskModel.model_validate(data)
        assert recreated.estimated_duration == original.estimated_duration
        assert recreated.timeout_seconds == original.timeout_seconds

    def test_iso_format_integration(self):
        """Test ISO 8601 format integration with Pydantic."""
        task = SimpleTaskModel(name="ISO Task", duration="PT1H30M")
        assert task.duration == 5400  # 1.5 hours

        config = ConfigModel(
            cache_ttl="PT5M",
            session_timeout="PT30M",
            cleanup_interval="PT1H",
            max_request_time="PT30S"
        )

        assert config.cache_ttl == 300
        assert config.session_timeout == 1800
        assert config.cleanup_interval == 3600
        assert config.max_request_time == 30

    def test_negative_durations(self):
        """Test handling of negative durations in models."""
        # This should work for models that don't have constraints
        task = SimpleTaskModel(name="Negative", duration="-30m")
        assert task.duration == -1800

        # But should fail for constrained fields
        with pytest.raises(ValidationError):
            DetailedTaskModel(
                name="Negative Timeout",
                estimated_duration="1h",
                timeout_seconds="-30s",  # Violates gt=0 constraint
                max_hours="8h"
            )

    def test_type_annotations_work(self):
        """Test that different duration type annotations work identically."""
        class TypeTestModel(BaseModel):
            duration_generic: Duration
            duration_seconds: Seconds
            duration_minutes: Minutes
            duration_hours: Hours

        model = TypeTestModel(
            duration_generic="1h",
            duration_seconds="1h",
            duration_minutes="1h",
            duration_hours="1h"
        )

        # All should be the same value (3600 seconds)
        assert model.duration_generic == 3600
        assert model.duration_seconds == 3600
        assert model.duration_minutes == 3600
        assert model.duration_hours == 3600

    def test_field_info_and_descriptions(self):
        """Test that field descriptions and info work correctly."""
        schema = DetailedTaskModel.model_json_schema()

        # Check that descriptions are preserved
        props = schema["properties"]
        assert "description" in props["estimated_duration"]
        assert "description" in props["timeout_seconds"]
        assert "description" in props["break_minutes"]
        assert "description" in props["max_hours"]

        # Check that constraints are preserved
        assert props["timeout_seconds"]["exclusiveMinimum"] == 0
        assert props["max_hours"]["maximum"] == 24*3600

    def test_model_copy_and_update(self):
        """Test model copying and updating with duration fields."""
        original = ConfigModel(cache_ttl=300, session_timeout=1800)  # Use parsed values

        # Test copy with updates - need to create new model to parse string
        updated_data = original.model_dump()
        updated_data["cache_ttl"] = "10m"  # String that needs parsing
        updated = ConfigModel.model_validate(updated_data)
        assert updated.cache_ttl == 600  # 10 minutes
        assert updated.session_timeout == 1800  # Unchanged

        # Test deep copy behavior
        project = ProjectModel(
            name="Original",
            tasks=[SimpleTaskModel(name="Task", duration="1h")]
        )

        copied = project.model_copy(deep=True)
        copied.tasks[0].duration = parse_duration("2h")

        # Original should be unchanged
        assert project.tasks[0].duration == 3600  # 1 hour
        assert copied.tasks[0].duration == 7200   # 2 hours
