from fastapi import APIRouter, Depends

from API.Controller.V1.copy_item import copy_item
from Modules.V1 import schemas
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.post("/copy-item")
def request_copy(payload: schemas.ActionOnItem,
                 user: dict = Depends(verify_user)):
    """

    :param payload:
    :param user:
    :return:
    """
    return copy_item(payload, user)
