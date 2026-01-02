from pydantic import BaseModel

class UserView(BaseModel):
    id: str
    name: str
    email: str
    preferred_username: str

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    title: str
    content: str
    owner_id: str


class PostView(BaseModel):
    id: str
    title: str
    content: str
    owner_id: str

    class Config:
        from_attributes = True