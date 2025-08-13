from fastapi import APIRouter, Depends

from API.Controller.V1.rename_item import rename_item
from Modules.V1 import schemas
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.put('/rename-item')
def rename(payload: schemas.RenameItem,
           user: dict = Depends(verify_user)):
    """

    :param payload:
    :param user:
    :return:
    """
    return rename_item(payload, user)
