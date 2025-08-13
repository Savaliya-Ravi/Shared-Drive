from fastapi import APIRouter, Depends

from API.Controller.V1.sharing import sharing
from Modules.V1 import schemas
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.post('/sharing')
def share_item(payload: schemas.Sharing,
               user: dict = Depends(verify_user)):
    """

    :param payload:
    :param user:
    :return:
    """
    return sharing(payload, user)
