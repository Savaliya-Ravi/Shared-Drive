import traceback
from datetime import datetime

import getmac

from Constant.general import ADD, REMOVE
from Constant.http import HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR, HC_OK, HC_UNAUTHORISED, \
    HC_NOT_FOUND, HEM_ITEM_NOT_FOUND, HSM_ADD_FAVOURITE, HSM_REMOVE_FAVOURITE, HEM_INVALID_ACTION
from Utils.V1.copy_folder_function import copies
from Utils.V1.db import favorites_collection, drive_collection
from Utils.V1.response import errorResponse, successResponse
from Utils.V1.logger import logger
from Utils.V1.utility_functions import logger_details


def action_on_favourite(payload, action, user):
    """
    Handle actions related to adding or removing items from the user's favorites.

    :param action: Action to be performed (ADD or REMOVE)
    :param payload: Request payload containing owner_id and item_id
    :param user: User information obtained from the authentication middleware
    :return: JSON response indicating the success or failure of the action
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True,
                         extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        if action == ADD:
            # Fetch the owner's drive to find the item
            owner_drive = drive_collection.find_one({"_id": payload.owner_id})

            # Find the item in the owner's drive
            item, item_type = copies.find_item_in_drive(owner_drive, payload.item_id)
            if item:
                # Create a favorite item document
                favorite_item = {
                    "favourite_by": uid,
                    "owner_id": payload.owner_id,
                    "item_id": payload.item_id,
                    "added_at": datetime.utcnow()
                }

                # Insert the favorite item into the favorites collection
                favorites_collection.insert_one(favorite_item)
                logger.info(HSM_ADD_FAVOURITE, extra=logger_details(uid))
                return successResponse(HC_OK, HSM_ADD_FAVOURITE)
            else:
                return errorResponse(HC_NOT_FOUND, HEM_ITEM_NOT_FOUND)

        elif action == REMOVE:
            # Remove the favorite item from the favorites collection
            favorites_collection.delete_one({"item_id": payload.item_id, "favourite_by": uid})
            logger.info(HSM_REMOVE_FAVOURITE, extra=logger_details(uid))
            return successResponse(HC_OK, HSM_REMOVE_FAVOURITE)

        else:
            logger.error(HEM_INVALID_ACTION, exc_info=True, extra=logger_details(uid))
            return errorResponse(HC_NOT_FOUND, HEM_ITEM_NOT_FOUND)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error while executing favorite action API: {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
