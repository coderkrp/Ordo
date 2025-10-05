from pydantic import BaseModel


class Profile(BaseModel):
    client_id: str
    name: str
    email: str
