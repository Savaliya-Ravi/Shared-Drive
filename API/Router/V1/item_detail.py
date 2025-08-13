from fastapi import APIRouter, Depends

from API.Controller.V1.item_detail import item_details
from Modules.V1 import schemas
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.put('/item-detail')
def detail(payload: schemas.FileContent,
           user: dict = Depends(verify_user)):
    """

    :param payload:
    :param user:
    :return:
    """
    return item_details(payload, user)
