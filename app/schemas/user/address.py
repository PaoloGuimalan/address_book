from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, Field, BeforeValidator


def empty_form_field_to_none(v):
    if v == "" or v == "null" or v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return v


OptionalFormFloat = Annotated[float | None, BeforeValidator(empty_form_field_to_none)]


def empty_string_to_none(v):
    if v == "" or v is None:
        return None
    return str(v)


OptionalFormStr = Annotated[str | None, BeforeValidator(empty_string_to_none)]


class AddressBase(BaseModel):
    """Core attributes validated automatically on input and output loops."""

    title: str = Field(
        default="Home",
        min_length=1,
        max_length=100,
        description="Label for the entry (e.g., Home, Office, Work).",
    )
    street_address: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Street name and housing/building numbers.",
    )
    city: str = Field(..., min_length=1, max_length=100, description="City location.")
    state: str = Field(
        ..., min_length=1, max_length=100, description="State, province, or region."
    )
    postal_code: str = Field(
        ..., min_length=1, max_length=20, description="ZIP or zip code identifier."
    )
    country: str = Field(
        ..., min_length=1, max_length=100, description="Country classification."
    )

    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="GPS latitude location coordinate. Range: -90 to 90.",
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="GPS longitude location coordinate. Range: -180 to 180.",
    )


class AddressResponse(AddressBase):
    """
    Defines exactly what data structure is safely returned to the client over HTTP.
    Exposes structural record metadata without leaking cross-table properties.
    """

    id: int = Field(
        ..., description="The unique database primary key auto-increment row ID."
    )
    account_id: int = Field(
        ..., description="The database primary key ID of the owning Account record."
    )
    created_at: datetime = Field(
        ..., description="Database timestamp when the address record was generated."
    )
    updated_at: datetime = Field(
        ...,
        description="Database timestamp tracking the latest structural modifications.",
    )

    model_config = {"from_attributes": True}


class AddressListResponse(BaseModel):
    """
    Wraps an array list of addresses payloads alongside 1-indexed pagination metadata.
    """

    total_records: int = Field(
        ..., description="The count of entries fetched in this specific page batch."
    )
    current_page: int = Field(
        ..., description="The current active 1-indexed page number."
    )
    limit: int = Field(
        ..., description="The maximum allowed row volume ceiling per page."
    )
    data: list[AddressResponse] = Field(
        ..., description="The array matrix containing filtered account data objects."
    )


class AddressCreate(BaseModel):
    """Enforces strict validation constraints on incoming address bodies."""

    title: str = Field(
        default="Home",
        min_length=1,
        max_length=100,
        description="Label (e.g., Home, Office).",
    )
    street_address: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)


class AddressUpdate(BaseModel):
    """Enforces strict validation constraints for a complete PUT update."""

    title: str = Field(..., min_length=1, max_length=100)
    street_address: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)
    latitude: OptionalFormFloat = Field(
        default="",
        description="Manual GPS latitude override. Leave blank for auto-lookup.",
    )
    longitude: OptionalFormFloat = Field(
        default="",
        description="Manual GPS longitude override. Leave blank for auto-lookup.",
    )


class AddressPatch(BaseModel):
    """Enforces optional structural parameters for a partial PATCH update."""

    title: OptionalFormStr = Field(default=None, min_length=1, max_length=100)
    street_address: OptionalFormStr = Field(default=None, min_length=1, max_length=255)
    city: OptionalFormStr = Field(default=None, min_length=1, max_length=100)
    state: OptionalFormStr = Field(default=None, min_length=1, max_length=100)
    postal_code: OptionalFormStr = Field(default=None, min_length=1, max_length=20)
    country: OptionalFormStr = Field(default=None, min_length=1, max_length=100)

    # 🚀 FIXED: Cleans up numeric float boundaries safely on HTML form fields ingest
    latitude: OptionalFormFloat = Field(default=None, ge=-90.0, le=90.0)
    longitude: OptionalFormFloat = Field(default=None, ge=-180.0, le=180.0)


class AddressSearchNearby(BaseModel):
    """Validates parameters when searching for addresses inside a specific kilometer radius."""

    latitude: float = Field(
        ..., ge=-90.0, le=90.0, description="Center point GPS latitude."
    )
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="Center point GPS longitude."
    )
    radius_km: float = Field(
        default=5.0,
        gt=0.0,
        description="Search radius distance threshold in kilometers.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="The maximum number of closest results to return.",
    )
