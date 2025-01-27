from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.api.auth.crud import get_staff_from_by_login, validate_password
from api.api.schemas import LoginSchema, Response
from api.db import get_db
from api.utils.auth_middleware import create_access_token
from api.utils.constants import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()


@router.post("/login")
async def login(staff: LoginSchema, db: Session = Depends(get_db)):
    _current_staff = get_staff_from_by_login(db=db, login=staff.login)
    if not _current_staff:
        raise HTTPException(status_code=401, detail="Login or password invalid")
    check_password = validate_password(
        hashed_password=_current_staff.password, password=staff.password
    )
    if not check_password:
        raise HTTPException(status_code=400, detail="Login or password invalid")
    return Response(
        code=200,
        status="ok",
        message="Successfully login",
        result={
            "role": _current_staff.role,
            "access_token": create_access_token(
                data={"id": str(_current_staff.id), "role": _current_staff.role},
                expires_delta=timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)),
            ),
        },
    ).model_dump()
