from typing import Annotated
from sqlalchemy.orm import Session

import jwt
from fastapi import Depends,  HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from utils.security import SECRET_KEY, ALGORITHM
from services.user_service import UserService
from dto.auth import TokenData
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
from config.database import get_db

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

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
