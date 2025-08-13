from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form

from API.Controller.V1.upload_item import upload_item
from Utils.V1.user_auth_token import verify_user

router = APIRouter()


@router.post('/upload-item')
def item_upload(folder_id: str = Form(None),
                files: List[UploadFile] = File(None),
                user: dict = Depends(verify_user)):
    """

    :param folder_id:
    :param files:
    :param user:
    :return:
    """
    return upload_item(folder_id, files, user)

#
# @router.post('/upload-item')
# def item_upload(drag_n_drop: bool = Form(False),
#                 folder_id: str = Form(None),
#                 files: List[UploadFile] = File(None),
#                 file_name: List[str] = Form(None),
#                 user: dict = Depends(verify_user)):
#     """
#
#     :param drag_n_drop:
#     :param folder_id:
#     :param files:
#     :param file_name:
#     :param user:
#     :return:
#     """
#     return upload_item(drag_n_drop, folder_id, files, file_name, user)
