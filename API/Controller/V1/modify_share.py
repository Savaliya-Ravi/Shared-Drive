import traceback

from Constant.general import UPDATE, DELETE
from Constant.http import HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR, HC_UNAUTHORISED, HC_OK, HC_BAD_REQUEST, \
    HEM_ITEM_NOT_FOUND, HSM_ITEM_UPDATED_SUCCESS, HSM_ITEM_DELETED_SUCCESS, \
    HEM_INVALID_ACTION
from Utils.V1.db import sharing_collection, favorites_collection
from Utils.V1.logger import logger
from Utils.V1.response import errorResponse, successResponse
from Utils.V1.utility_functions import logger_details


def modify_share(payload, action, user):
    """
    Update or delete the shared item, based on the specified action.

    :param action: The action to be performed, either 'update' or 'delete'.
    :param payload: Request payload containing shared_user, shared_item_id, new_access.
    :param user: Dictionary containing user information obtained from the authentication middleware.
    :return: JSON response indicating the success or failure of the operation.
    """

    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True,
                         extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        if action == UPDATE:
            # Find and update the shared item
            result = sharing_collection.update_one(
                {"shared_user": payload.shared_user, "shared_item_id": payload.shared_item_id},
                {"$set": {"access_type": payload.new_access}}
            )

            # Check if any document was updated
            if result.matched_count == 0:
                logger.error(HEM_ITEM_NOT_FOUND, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_BAD_REQUEST, HEM_ITEM_NOT_FOUND)

            logger.info(HSM_ITEM_UPDATED_SUCCESS, extra=logger_details(uid))
            return successResponse(HC_OK, HSM_ITEM_UPDATED_SUCCESS)

        elif action == DELETE:
            # Delete the shared item
            result = sharing_collection.delete_one(
                {"shared_user": payload.shared_user, "shared_item_id": payload.shared_item_id}
            )

            # Delete corresponding favorite entry if exists
            favorites_collection.delete_one({"item_id": payload.shared_item_id, "favourite_by": uid})

            # Check if any document was deleted
            if result.deleted_count == 0:
                logger.error(HEM_ITEM_NOT_FOUND, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_BAD_REQUEST, HEM_ITEM_NOT_FOUND)

            logger.info(HSM_ITEM_DELETED_SUCCESS, extra=logger_details(uid))
            return successResponse(HC_OK, HSM_ITEM_DELETED_SUCCESS)

        else:
            logger.error(HEM_INVALID_ACTION, exc_info=True, extra=logger_details(uid))
            return errorResponse(HC_BAD_REQUEST, HEM_INVALID_ACTION)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error while executing modify share API: {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
