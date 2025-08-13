from fastapi import APIRouter, Depends

from API.Controller.V1.folder import folder_creation
from Modules.V1 import schemas
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.post('/folder')
def folder(payload: schemas.CreateFolder,
           user: dict = Depends(verify_user)
           # cursor: pyodbc.Cursor = Depends(get_db_cursor)
           ):
    """

    :param payload:
    :param user:
    :return:
    """
    return folder_creation(payload, user)
