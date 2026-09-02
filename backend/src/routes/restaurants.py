from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dto.user import UserResponse, UserUpdate, AdminUserUpdate
from services.user_service import UserService
from dependencies.auth import get_current_user, get_current_admin
from models.user import User
from config.database import get_db
from typing import List


router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"],
)