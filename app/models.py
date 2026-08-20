from pydantic import BaseModel, EmailStr, Field


class CustomerCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )
    email: EmailStr


class CustomerUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    email: EmailStr | None = None


class Customer(BaseModel):
    id: int
    name: str
    email: EmailStr


class PaginationMetadata(BaseModel):
    page: int
    limit: int
    total: int
    has_next: bool


class CustomerListResponse(BaseModel):
    data: list[Customer]
    pagination: PaginationMetadata


class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str | None = None