from fastapi import APIRouter, Depends

from API.Controller.V1.move_item import move_item
from Modules.V1 import schemas
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.post("/move-item")
def request_move(payload: schemas.ActionOnItem,
                 user: dict = Depends(verify_user)):
    """

    :param payload:
    :param user:
    :return:
    """
    return move_item(payload, user)
