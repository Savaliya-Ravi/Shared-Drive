import traceback
from datetime import datetime

from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from Constant.general import ADD, UPDATE, DELETE
from Constant.http import HC_OK, HEM_SERVER_ERROR, HC_INTERNAL_SERVER_ERROR, \
    HC_UNAUTHORISED, HC_NOT_FOUND, \
    HSM_GROUP_CREATE_SUCCESS, HEM_INVALID_ACTION, \
    HSM_GROUP_UPDATE_SUCCESS, HSM_GROUP_DELETE_SUCCESS, HEM_GROUP_NOT_FOUND, HSM_DATA_FETCHED_SUCCESS
from Utils.V1.db import group_collection
from Utils.V1.logger import logger
from Utils.V1.response import successResponse, errorResponse
from Utils.V1.utility_functions import utility, logger_details


def group_creation(payload, action, user):
    """
    Handle group creation, update, and deletion based on the action parameter.

    :param action: Action to perform (ADD, UPDATE, DELETE)
    :param payload: Request payload containing group details
    :param user: User information obtained from the authentication middleware
    :return: JSON response indicating the success or failure of the operation
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True,
                         extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        if action == ADD:
            # Prepare group data for insertion
            group_data = {
                "group_name": payload.group_name,
                "members": payload.members,
                "owner": uid,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            group_collection.insert_one(group_data)
            logger.info(HSM_GROUP_CREATE_SUCCESS, extra=logger_details(uid))
            return successResponse(HC_OK, HSM_GROUP_CREATE_SUCCESS)

        elif action == UPDATE:
            # Prepare data for updating the group
            update_data = {
                "group_name": payload.group_name,
                "members": payload.members,
                "updated_at": datetime.now()
            }

            # Update the group in the database
            result = group_collection.update_one({"_id": ObjectId(payload.group_id)}, {"$set": update_data})
            if result.matched_count == 0:
                logger.error(HEM_GROUP_NOT_FOUND, extra=logger_details(uid))
                return errorResponse(HC_NOT_FOUND, HEM_GROUP_NOT_FOUND)
            logger.info(HSM_GROUP_UPDATE_SUCCESS, extra=logger_details(uid))
            return successResponse(HC_OK, HSM_GROUP_UPDATE_SUCCESS)

        elif action == DELETE:
            # Delete the group from the database
            result = group_collection.delete_one({"_id": ObjectId(payload.group_id)})
            if result.deleted_count == 0:
                logger.error(HEM_GROUP_NOT_FOUND, extra=logger_details(uid))
                return errorResponse(HC_NOT_FOUND, HEM_GROUP_NOT_FOUND)
            logger.info(HSM_GROUP_DELETE_SUCCESS, extra=logger_details(uid))
            return successResponse(HC_OK, HSM_GROUP_DELETE_SUCCESS)

        else:
            # Handle invalid action parameter
            logger.info(HEM_INVALID_ACTION, extra=logger_details(uid))
            return errorResponse(HC_NOT_FOUND, HEM_INVALID_ACTION)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error while handling group action: {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)


def group_detail(user):
    """
    Fetch and return the details of all groups owned by the user.

    :param user: User information obtained from the authentication middleware
    :return: JSON response containing the details of the groups
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True,
                         extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        # Fetch groups owned by the user
        result = list(group_collection.find({"owner": uid}))

        # Convert ObjectId to string in the result
        utility.convert_object_id(result)
        logger.info(HSM_DATA_FETCHED_SUCCESS, extra=logger_details(uid))
        return successResponse(HC_OK, HSM_DATA_FETCHED_SUCCESS, jsonable_encoder(result))

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error while fetching group details: {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
