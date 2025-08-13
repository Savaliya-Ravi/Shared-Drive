import traceback
from datetime import datetime

import getmac
from bson import ObjectId

from Constant.http import HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR, HC_UNAUTHORISED, HC_OK, HSM_ITEM_SHARED_SUCCESS
from Utils.V1.db import sharing_collection, group_collection
from Utils.V1.response import errorResponse, successResponse
from Utils.V1.logger import logger
from Utils.V1.utility_functions import logger_details


def sharing(payload, user):
    """
    Share an item with specific users and groups.

    :param payload: Request payload containing shared_item_id, access_type, shared_user, and group_list
    :param user: User information obtained from the authentication middleware
    :return: JSON response indicating the success or failure of the sharing operation
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True,
                         extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        # Initialize a set for unique shared users
        unique_shared_users = set(payload.shared_user)

        # Retrieve members from each group in the group list and add them to the set of unique shared users
        if payload.group_list:
            group_ids = [ObjectId(group_id) for group_id in payload.group_list]
            groups = group_collection.find({"_id": {"$in": group_ids}})
            for group in groups:
                members = group.get("members", [])
                unique_shared_users.update(members)

        # Find existing shares to avoid duplicates
        existing_shares = sharing_collection.find({
            "shared_item_id": payload.shared_item_id,
            "shared_user": {"$in": list(unique_shared_users)}
        })

        # Remove users who already have the item shared with them
        for share in existing_shares:
            unique_shared_users.discard(share["shared_user"])

        # Prepare the shared items
        shared_items = [
            {
                "owner_id": uid,
                "shared_by": uid,
                "shared_user": shared_user,
                "shared_item_id": payload.shared_item_id,
                "access_type": payload.access_type,
                "shared_at": datetime.utcnow()
            }
            for shared_user in unique_shared_users
        ]

        # Insert all shared items into the sharing collection
        if shared_items:
            sharing_collection.insert_many(shared_items)

        logger.info(HSM_ITEM_SHARED_SUCCESS, extra=logger_details(uid))
        return successResponse(HC_OK, HSM_ITEM_SHARED_SUCCESS)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error while executing sharing API: {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
