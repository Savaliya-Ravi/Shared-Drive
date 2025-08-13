from fastapi import APIRouter, Depends, Query

from API.Controller.V1.favourites import action_on_favourite
from Constant.general import ADD, REMOVE
from Modules.V1 import schemas
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.post('/favourite')
def favourite(payload: schemas.Favourite,
              action: str = Query(description=f"{ADD} | {REMOVE}"),
              user: dict = Depends(verify_user)):
    """

    :param action:
    :param payload:
    :param user:
    :return:
    """
    return action_on_favourite(payload, action, user)

# @router.delete('/remove-favourite')
# def remove_favourite(request: Request,
#                      payload: schemas.Favourite,
#                      user: dict = Depends(verify_user)):
#     """
#
#     :param request:
#     :param payload:
#     :param user:
#     :return:
#     """
#     return remove_from_favourite(request, payload, user)
