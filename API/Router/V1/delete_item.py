from fastapi import APIRouter, Depends

from API.Controller.V1.delete_item import delete_item
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.delete('/delete-item')
def delete(item_id_list: str,
           user: dict = Depends(verify_user)):
    """

    :param item_id_list:
    :param user:
    :return:
    """
    return delete_item(item_id_list, user)
