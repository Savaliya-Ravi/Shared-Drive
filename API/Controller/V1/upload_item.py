import os
import traceback

import getmac
from bson import ObjectId

from Constant.general import BASE_PATH
from Constant.http import HC_INTERNAL_SERVER_ERROR, HC_OK, HC_UNAUTHORISED, HEM_FOLDER_NAME_EXIST, \
    HC_BAD_REQUEST, HEM_FILE_NAME_EXIST, HEM_SERVER_ERROR, HSM_ITEM_UPLOAD_SUCCESS, HC_NOT_FOUND, HEM_NO_ITEM_UPLOADED
from Utils.V1.db import drive_collection
from Utils.V1.response import successResponse, errorResponse
from Utils.V1.upload_folder_functions import uploads
from Utils.V1.utility_functions import utility, logger_details
from Utils.V1.logger import logger


def upload_item(folder_id, files, user):
    """
    Handle the upload of files and folders to a user's drive.

    :param folder_id: ID of the folder where files should be uploaded.
    :param files: List of file objects to be uploaded.
    :param user: Dictionary containing user information obtained from the authentication middleware.
    :return: JSON response indicating the success or failure of the upload operation.
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True,
                         extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        # Define the base path for the user's files
        base_path = os.path.join(os.getcwd(), BASE_PATH, uid)
        if not files:
            logger.error(HEM_NO_ITEM_UPLOADED, exc_info=True, extra=logger_details(uid))
            return errorResponse(HC_NOT_FOUND, HEM_NO_ITEM_UPLOADED)

        # Get the outer path of the first file (used for folder structure)
        outer_path = files[0].filename.split("/")

        # Fetch or initialize the user's drive entry
        user_drive = drive_collection.find_one({"_id": uid})
        if not user_drive:
            user_drive = {
                "_id": uid,
                "path": base_path,
                "folders": [],
                "files": []
            }

        # Determine the current path based on the parent folder
        parent_folder = utility.find_folder(user_drive["folders"], folder_id) if folder_id else None
        current_path = parent_folder['path'] if parent_folder else base_path

        # Ensure the base path exists
        os.makedirs(base_path, exist_ok=True)

        # Handle nested folder structures
        if len(outer_path) > 1:
            if os.path.exists(current_path + '/' + outer_path[0]):
                logger.error(HEM_FOLDER_NAME_EXIST, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_BAD_REQUEST, HEM_FOLDER_NAME_EXIST)

            result = uploads.save_folder_structure(
                user_drive, files, base_path, ObjectId(folder_id) if folder_id else None
            )

        else:
            # Check for existing files with the same name
            for file in files:
                if os.path.exists(current_path + '/' + file.filename):
                    logger.error(HEM_FILE_NAME_EXIST, exc_info=True, extra=logger_details(uid))
                    return errorResponse(HC_BAD_REQUEST, HEM_FILE_NAME_EXIST)

            for file in files:
                result = uploads.save_file_structure(
                    user_drive, file, base_path, ObjectId(folder_id) if folder_id else None
                )

        # Handle potential errors from save functions
        if result in [HEM_FOLDER_NAME_EXIST, HEM_FILE_NAME_EXIST]:
            logger.error(result, exc_info=True, extra=logger_details(uid))
            return errorResponse(HC_BAD_REQUEST, result)

        # Update the user's drive entry in the database
        drive_collection.update_one({"_id": uid}, {"$set": user_drive}, upsert=True)

        logger.info(HSM_ITEM_UPLOAD_SUCCESS, extra=logger_details(uid))
        return successResponse(HC_OK, HSM_ITEM_UPLOAD_SUCCESS)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error while executing upload item API: {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
