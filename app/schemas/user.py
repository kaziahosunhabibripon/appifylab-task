from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token:str
    token_type: str        