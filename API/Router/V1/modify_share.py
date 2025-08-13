from fastapi import APIRouter, Depends, Query

from API.Controller.V1.modify_share import modify_share
from Constant.general import UPDATE, DELETE
from Modules.V1 import schemas
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.post('/modify-share')
def share_modify(payload: schemas.ModifyShare,
                 action: str = Query(description=f"{UPDATE} | {DELETE}"),
                 user: dict = Depends(verify_user)):
    """

    :param action:
    :param payload:
    :param user:
    :return:
    """
    return modify_share(payload, action, user)
