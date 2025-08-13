import traceback
import urllib.parse

from Constant.http import HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR, HC_OK, HC_UNAUTHORISED, \
    HC_BAD_REQUEST, HEM_ITEM_NOT_FOUND, HSM_DELETED_SUCCESS
from Utils.V1.db import drive_collection
from Utils.V1.delete_function import deletes
from Utils.V1.logger import logger
from Utils.V1.response import errorResponse, successResponse
from Utils.V1.utility_functions import logger_details


def delete_item(item_id_list, user):
    """

    :param item_id_list: list of item_id to be deleted
    :param user: User information obtained from the authentication middleware
    :return: JSON response indicating the success or failure of the delete operation
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True, extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        user_drive = drive_collection.find_one({"_id": uid})
        if item_id_list:
            item_id_list = urllib.parse.unquote(item_id_list)

            for item_id in item_id_list.split(','):
                # Find the item to be deleted
                if not deletes.find_and_delete_item(user_drive, item_id):
                    logger.error(HEM_ITEM_NOT_FOUND, exc_info=True, extra=logger_details(uid))
                    return errorResponse(HC_BAD_REQUEST, HEM_ITEM_NOT_FOUND)

        # Update the user's drive in the database
        drive_collection.update_one({"_id": uid}, {"$set": user_drive})

        logger.info(HSM_DELETED_SUCCESS, extra=logger_details(uid))
        return successResponse(HC_OK, HSM_DELETED_SUCCESS)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"error while executing delete item API {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
