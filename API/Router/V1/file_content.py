from fastapi import APIRouter, Depends

from API.Controller.V1.file_content import get_file_content
from Modules.V1 import schemas
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.post('/file-content')
def file_content(payload: schemas.FileContent,
                 user: dict = Depends(verify_user)):
    """

    :param payload:
    :param user:
    :return:
    """
    return get_file_content(payload, user)
