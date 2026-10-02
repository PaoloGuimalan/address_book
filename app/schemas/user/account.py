from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class AccountBase(BaseModel):
    """
    Core attributes shared across all account schemas.
    Validates email format out-of-the-box using Pydantic EmailStr.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="The unique system identifier username.",
    )
    email: EmailStr = Field(..., description="The contact primary email address.")
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The user's real or display name.",
    )


class AccountCreate(AccountBase):
    """
    Enforces strict structural rules when a new account is registering.
    Inherits username, email, and name from AccountBase, and demands a secure password.
    """

    password: str = Field(
        ...,
        min_length=8,
        description="Plaintext raw password. Must be at least 8 characters.",
    )


class AccountLogin(BaseModel):
    """
    Enforces requirements for the authentication login payload.
    Allows flexibility so the user can enter either their username or email.
    """

    username_or_email: str = Field(
        ...,
        min_length=1,
        description="Accepts either the user's username or registered email.",
    )
    password: str = Field(
        ..., min_length=1, description="The account authentication password."
    )


class AccountResponse(BaseModel):
    """
    Defines exactly what data is returned to the client over HTTP responses.
    Crucially drops the password parameter entirely so hashes never leave the server.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="The unique system identifier username.",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The user's real or display name.",
    )


class AccountListResponse(BaseModel):
    """
    Wraps an array list of account payloads alongside 1-indexed pagination metadata.
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
    data: list[AccountResponse] = Field(
        ..., description="The array matrix containing filtered account data objects."
    )
