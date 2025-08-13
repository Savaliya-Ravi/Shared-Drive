import traceback

from Constant.http import HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR, HC_OK, HC_UNAUTHORISED, \
    HC_BAD_REQUEST, HSM_COPIED_SUCCESS, HC_NOT_FOUND, HEM_NO_ITEM_SELECTED
from Utils.V1.copy_folder_function import copies
from Utils.V1.db import drive_collection
from Utils.V1.logger import logger
from Utils.V1.response import errorResponse, successResponse
from Utils.V1.utility_functions import logger_details


def copy_item(payload, user):
    """
    Copy an item (file or folder) to a destination folder.

    :param payload: Request payload containing list of item_id and destination_folder_id
    :param user: User information obtained from the authentication middleware
    :return: JSON response indicating the success or failure of the copy operation
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True,
                         extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        user_drive = drive_collection.find_one({"_id": uid})

        if payload.item_id:
            item_id_list = payload.item_id
        else:
            logger.error(HEM_NO_ITEM_SELECTED, exc_info=True, extra=logger_details(uid))
            return errorResponse(HC_NOT_FOUND, HEM_NO_ITEM_SELECTED)
        destination_folder_id = payload.destination_folder_id

        for item_id in item_id_list:
            item_to_copy, item_type, destination_folder_or_error = copies.find_item_and_destination(user_drive, item_id,
                                                                                                    destination_folder_id)
            if not item_to_copy:
                logger.error(destination_folder_or_error, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_BAD_REQUEST, destination_folder_or_error)

            # Check if item with the same name exists in the destination
            name_exists_error = copies.item_name_exists_in_destination(item_to_copy, item_type,
                                                                       destination_folder_or_error)
            if name_exists_error:
                logger.error(name_exists_error, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_BAD_REQUEST, name_exists_error)

            # Copy the item to the destination folder
            error_result = copies.save_copied_item(item_to_copy, destination_folder_or_error, item_type)
            if error_result:
                logger.error(error_result, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_BAD_REQUEST, error_result)

        drive_collection.update_one({"_id": uid}, {"$set": user_drive})

        logger.info(HSM_COPIED_SUCCESS, extra=logger_details(uid))
        return successResponse(HC_OK, HSM_COPIED_SUCCESS)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"error while executing copy item API {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
