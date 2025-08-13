from fastapi import APIRouter, Depends, Query

from API.Controller.V1.group import group_creation, group_detail
from Constant.general import ADD, UPDATE, DELETE
from Modules.V1 import schemas
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.post('/group')
def group(payload: schemas.Group,
          action: str = Query(description=f"{ADD} | {UPDATE} | {DELETE}"),
          user: dict = Depends(verify_user)):
    """

    :param payload:
    :param action:
    :param user:
    :return:
    """
    return group_creation(payload, action, user)


@router.get('/group_detail')
def get_group_detail(user: dict = Depends(verify_user)):
    """

    :param user:
    :return:
    """
    return group_detail(user)

# cursor: pyodbc.Cursor = Depends(get_db_cursor)
