from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email:     EmailStr
    password:  str
    full_name: str


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class ResetPasswordRequest(BaseModel):
    password:        str
    confirmPassword: str


class UpdateProfileRequest(BaseModel):
    firstname: str
    lastname:  str
    email:     EmailStr
    phone:     str = ""
    location:  str = ""


class ChangePasswordRequest(BaseModel):
    currentPassword: str
    newPassword:     str


class UserResponse(BaseModel):
    id:              str
    email:           str
    full_name:       str
    role:            str
    phone:           str = ""
    location:        str = ""
    profile_picture: str = ""
    created_at:      str = ""


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserResponse
