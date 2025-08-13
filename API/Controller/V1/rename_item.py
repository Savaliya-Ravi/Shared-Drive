import traceback

import getmac

from Constant.http import HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR, HC_OK, HC_UNAUTHORISED, \
    HC_BAD_REQUEST, HEM_ITEM_NOT_FOUND, HEM_FOLDER_NAME_EXIST, \
    HEM_FILE_NAME_EXIST, HSM_RENAMED_SUCCESS, HEM_RENAME_ITEM
from Utils.V1.db import drive_collection
from Utils.V1.rename_function import rename
from Utils.V1.response import errorResponse, successResponse
from Utils.V1.logger import logger
from Utils.V1.utility_functions import logger_details


def rename_item(payload, user):
    """
    Rename a file or folder both in the database and in local storage.

    :param payload: RenameRequest object containing item_id and new_name
    :param user: User information obtained from the authentication middleware
    :return: JSON response indicating the success or failure of the rename operation
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True,
                         extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        # Fetch the user's drive entry
        user_drive = drive_collection.find_one({"_id": uid})

        # Find the item to rename
        item_to_rename, item_type, parent = rename.find_item_in_drive(user_drive, payload.item_id)
        if not item_to_rename:
            return errorResponse(HC_BAD_REQUEST, HEM_ITEM_NOT_FOUND)

        # Check for name conflicts in the same directory
        if item_type == "file" and any(f["name"] == payload.new_name for f in parent.get("files", [])):
            logger.error(HEM_FILE_NAME_EXIST, exc_info=True, extra=logger_details(uid))
            return errorResponse(HC_BAD_REQUEST, HEM_FILE_NAME_EXIST)

        if item_type == "folder" and any(f["name"] == payload.new_name for f in parent.get("folders", [])):
            logger.error(HEM_FOLDER_NAME_EXIST, exc_info=True, extra=logger_details(uid))
            return errorResponse(HC_BAD_REQUEST, HEM_FOLDER_NAME_EXIST)

        # Rename the item in the drive
        error = rename.rename_item_in_drive(item_to_rename, payload.new_name, item_type)
        if error:
            logger.error(HEM_RENAME_ITEM, exc_info=True, extra=logger_details(uid))
            return errorResponse(HC_BAD_REQUEST, HEM_RENAME_ITEM)

        # Update the user's drive in the database
        drive_collection.update_one({"_id": uid}, {"$set": user_drive})

        logger.info(HSM_RENAMED_SUCCESS, extra=logger_details(uid))
        return successResponse(HC_OK, HSM_RENAMED_SUCCESS)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error while executing rename item API: {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
