"""
Pydantic schema for business_functions.yml validation

This module defines the data models for validating the business functions
configuration file using Pydantic. It ensures type safety and provides
clear validation errors.

Author: OMF Development Team
Version: 1.0.0
"""

from typing import Dict, List, Optional

try:
    from pydantic import BaseModel, Field, field_validator

    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback if pydantic is not installed
    PYDANTIC_AVAILABLE = False
    BaseModel = object

    def Field(*args, **kwargs):
        return None

    def field_validator(*args, **kwargs):
        def decorator(f):
            return f

        return decorator


class BusinessFunctionMetadata(BaseModel if PYDANTIC_AVAILABLE else object):
    """Metadata for a single business function"""

    category: Optional[str] = Field(None, description="Category of the business function")
    requires_mqtt: bool = Field(True, description="Whether this function requires MQTT")

    if PYDANTIC_AVAILABLE:

        class Config:
            extra = "allow"  # Allow additional fields


class BusinessFunction(BaseModel if PYDANTIC_AVAILABLE else object):
    """Schema for a single business function definition"""

    enabled: bool = Field(..., description="Whether this business function is enabled")
    description: str = Field(..., description="Human-readable description of the function")
    module_path: str = Field(..., description="Python module path where the class is defined")
    class_name: str = Field(..., description="Name of the class implementing this function")
    routed_topics: List[str] = Field(default_factory=list, description="List of MQTT topics this function handles")
    priority: Optional[int] = Field(5, ge=1, le=10, description="Priority level (1-10, higher = more important)")
    metadata: Optional[BusinessFunctionMetadata] = Field(None, description="Additional metadata for the function")

    if PYDANTIC_AVAILABLE:

        @field_validator("module_path")
        @classmethod
        def validate_module_path(cls, v: str) -> str:
            """Validate that module_path is a valid Python module path"""
            if not v or not all(part.isidentifier() for part in v.split(".")):
                raise ValueError(f"Invalid module path: {v}")
            return v

        @field_validator("class_name")
        @classmethod
        def validate_class_name(cls, v: str) -> str:
            """Validate that class_name is a valid Python identifier"""
            if not v or not v.isidentifier():
                raise ValueError(f"Invalid class name: {v}")
            return v


class ConfigMetadata(BaseModel if PYDANTIC_AVAILABLE else object):
    """Metadata for the entire configuration file"""

    version: str = Field(..., description="Version of the configuration format")
    last_updated: str = Field(..., description="Last update date")
    author: str = Field(..., description="Configuration author")
    description: Optional[str] = Field(None, description="Configuration description")


class QoSSettings(BaseModel if PYDANTIC_AVAILABLE else object):
    """QoS settings for MQTT topics"""

    default_qos: int = Field(1, ge=0, le=2, description="Default QoS level")
    critical_topics: List[str] = Field(default_factory=list, description="Topics requiring higher QoS")
    qos: int = Field(2, ge=0, le=2, description="QoS for critical topics")


class RoutingConfig(BaseModel if PYDANTIC_AVAILABLE else object):
    """Routing configuration for topic matching"""

    enable_wildcard_matching: bool = Field(True, description="Enable wildcard matching in topics")
    topic_separator: str = Field("/", description="Topic separator character")


class ValidationRules(BaseModel if PYDANTIC_AVAILABLE else object):
    """Validation rules for business functions"""

    require_module_path: bool = Field(True, description="Require module_path field")
    require_class_name: bool = Field(True, description="Require class_name field")
    allow_disabled_functions: bool = Field(True, description="Allow disabled functions in config")


class BusinessFunctionsConfig(BaseModel if PYDANTIC_AVAILABLE else object):
    """Complete schema for business_functions.yml"""

    metadata: ConfigMetadata = Field(..., description="Configuration metadata")
    business_functions: Dict[str, BusinessFunction] = Field(
        ..., description="Map of function names to function definitions"
    )
    qos_settings: Optional[QoSSettings] = Field(None, description="QoS settings for MQTT")
    routing: Optional[RoutingConfig] = Field(None, description="Routing configuration")
    validation: Optional[ValidationRules] = Field(None, description="Validation rules")

    if PYDANTIC_AVAILABLE:

        @field_validator("business_functions")
        @classmethod
        def validate_business_functions(cls, v: Dict[str, BusinessFunction]) -> Dict[str, BusinessFunction]:
            """Validate that business_functions dict is not empty"""
            if not v:
                raise ValueError("business_functions cannot be empty")
            return v

        class Config:
            extra = "forbid"  # Don't allow extra fields at top level


def is_pydantic_available() -> bool:
    """Check if pydantic is available for validation"""
    return PYDANTIC_AVAILABLE
