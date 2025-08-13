import traceback

from Constant.http import HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR, HC_OK, HC_UNAUTHORISED, \
    HC_BAD_REQUEST, HSM_MOVED_SUCCESS
from Utils.V1.db import drive_collection
from Utils.V1.logger import logger
from Utils.V1.move_file_folder import moving
from Utils.V1.response import errorResponse, successResponse
from Utils.V1.utility_functions import logger_details


def move_item(payload, user):
    """
    Move an item (file or folder) to a destination folder.

    :param payload: Request payload containing list of item_id and destination_folder_id
    :param user: User information obtained from the authentication middleware
    :return: JSON response indicating the success or failure of the move operation
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True,
                         extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        # Fetch the user's drive entry
        user_drive = drive_collection.find_one({"_id": uid})

        # Process each item in the item_id_list
        for item_id in payload.item_id:
            item_to_move, item_type, destination_folder_or_error = moving.find_item_and_destination_for_move(
                user_drive, item_id, payload.destination_folder_id)

            if not item_to_move:
                logger.error(destination_folder_or_error, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_BAD_REQUEST, destination_folder_or_error)

            # Check if item with the same name exists in the destination
            name_exists_error = moving.item_name_exists_in_destination(item_to_move, item_type,
                                                                       destination_folder_or_error)

            if name_exists_error:
                logger.error(name_exists_error, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_BAD_REQUEST, name_exists_error)

            # Move the item to the destination folder
            move_error = moving.move_item_to_destination(item_to_move, destination_folder_or_error, item_type,
                                                         user_drive, item_id)

            if move_error:
                logger.error(move_error, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_BAD_REQUEST, move_error)

        # Update the user's drive in the database
        drive_collection.update_one({"_id": uid}, {"$set": user_drive})

        logger.info(HSM_MOVED_SUCCESS, extra=logger_details(uid))
        return successResponse(HC_OK, HSM_MOVED_SUCCESS)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error while executing move item API: {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
