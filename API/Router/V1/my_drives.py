from fastapi import APIRouter, Depends, Query

from API.Controller.V1.my_drives import get_items
from Constant.general import MY_DRIVE, FAVOURITES, SHARED
from Modules.V1 import schemas
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.post('/my_drive')
def my_drive(payload: schemas.GetDrive,
             folder_type: str = Query(description=f"{MY_DRIVE} | {FAVOURITES} | {SHARED}"),
             user: dict = Depends(verify_user)):
    """

    :param payload:
    :param folder_type:
    :param user:
    :return:
    """
    return get_items(payload, folder_type, user)
