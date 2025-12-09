from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Schema for returning JWT tokens."""

    access_token: str
    token_type: str
