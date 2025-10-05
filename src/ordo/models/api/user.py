from pydantic import BaseModel, Field, EmailStr


class Profile(BaseModel):
    client_id: str = Field(..., description="Unique identifier for the client.")
    name: str = Field(..., description="Name of the client.")
    email: EmailStr = Field(
        ...,
        description="Email address of the client.",
        json_schema_extra={"example": "user@example.com"},
    )
