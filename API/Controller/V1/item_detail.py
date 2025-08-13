import traceback

from Constant.http import HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR, HC_OK, HC_UNAUTHORISED, \
    HC_BAD_REQUEST, HEM_ITEM_NOT_FOUND, HSM_RENAMED_SUCCESS
from Utils.V1.copy_folder_function import copies
from Utils.V1.db import drive_collection, sharing_collection
from Utils.V1.logger import logger
from Utils.V1.response import errorResponse, successResponse
from Utils.V1.utility_functions import logger_details


def item_details(payload, user):
    """
    Fetch details of a file or folder, including sharing information and metadata.

    :param payload: Payload containing item_id
    :param user: User information obtained from the authentication middleware
    :return: JSON response indicating the success or failure of the operation
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True, extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        # Find the user's drive in the database
        user_drive = drive_collection.find_one({"_id": uid})

        # Find the item in the user's drive
        item, item_type = copies.find_item_in_drive(user_drive, payload.item_id)
        if not item:
            logger.error(HEM_ITEM_NOT_FOUND, exc_info=True, extra=logger_details(uid))
            return errorResponse(HC_BAD_REQUEST, HEM_ITEM_NOT_FOUND)

        # Fetch sharing information for the item
        sharing_info = sharing_collection.find({"shared_item_id": payload.item_id})
        access_users = [info["shared_user"] for info in sharing_info]

        # Construct the response details
        details = {
            "name": item["name"],
            "access": access_users,
            "type": item_type,
            "size": item.get("size", "N/A"),  # Use "N/A" if size is not available
            "owner": item.get("owner", uid),  # Default to uid if owner is not available
            "created_at": item.get("created_at")
        }

        logger.info(HSM_RENAMED_SUCCESS, extra=logger_details(uid))
        return successResponse(HC_OK, HSM_RENAMED_SUCCESS, details)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error while fetching item details: {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
