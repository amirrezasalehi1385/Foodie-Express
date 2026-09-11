from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from dto.auth import TokenData
from services.user_service import UserService
from utils.security import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
from config.database import get_db
from models.user import User, UserRole

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id_str = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        user_id = int(user_id_str)

        if user_id <= 0:
            raise credentials_exception

        token_data = TokenData(user_id=user_id)

    except (InvalidTokenError, ValueError):
        raise credentials_exception

    user_service = UserService(db)

    user = user_service.get_user_by_id(
        user_id=token_data.user_id
    )

    if user is None:
        raise credentials_exception

    return user

async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:

    # if current_user.role != UserRole.ADMIN:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin access required",
    #     )

    return current_user

async def get_current_restaurant_owner(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User: 

    if current_user.role != UserRole.RESTAURANT_OWNER : 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Restaurant owner access required",
        )

    return current_user


async def get_current_admin_or_restaurant_owner(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:

    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.RESTAURANT_OWNER,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or restaurant owner access required",
        )

    return current_user

async def get_current_delivery_man(
        current_user: Annotated[User, Depends(get_current_user)],

) -> User:
    if current_user.role != UserRole.DELIVERY_MAN :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Delivery man access required",
        )
    return current_user
