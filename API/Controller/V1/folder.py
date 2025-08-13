import os
import traceback

from Constant.general import BASE_PATH
from Constant.http import HC_OK, HEM_SERVER_ERROR, HC_INTERNAL_SERVER_ERROR, \
    HC_UNAUTHORISED, HC_NOT_FOUND, HSM_FOLDER_CREATE_SUCCESS, \
    HEM_FOLDER_NAME_EXIST, HEM_FOLDER_NOT_EXISTS, HC_BAD_REQUEST
from Utils.V1.db import drive_collection
from Utils.V1.logger import logger
from Utils.V1.response import successResponse, errorResponse
from Utils.V1.upload_folder_functions import uploads
from Utils.V1.utility_functions import utility, logger_details


def folder_creation(payload, user):
    """
    Create a new folder in the user's drive.

    :param payload: Request payload containing parent_folder_id and folder_name
    :param user: User information obtained from the authentication middleware
    :return: JSON response indicating the success or failure of the folder creation
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True,
                         extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']
        base_path = os.path.join(os.getcwd(), BASE_PATH, uid)

        # Fetch the user's drive entry, create one if it doesn't exist
        user_drive = drive_collection.find_one({"_id": uid})
        if not user_drive:
            user_drive = {
                "_id": uid,
                "path": base_path,
                "folders": [],
                "files": []
            }

        # Determine the base path for the new folder
        if payload.parent_folder_id:
            parent_folder = utility.find_folder(user_drive["folders"], payload.parent_folder_id)
            if not parent_folder:
                logger.error(HEM_FOLDER_NOT_EXISTS, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_NOT_FOUND, HEM_FOLDER_NOT_EXISTS)

            current_path = os.path.join(parent_folder["path"], payload.folder_name)
        else:
            parent_folder = user_drive
            current_path = os.path.join(base_path, payload.folder_name)

        # Check if a folder with the same name already exists in the same path
        if os.path.exists(current_path):
            logger.error(HEM_FOLDER_NAME_EXIST, exc_info=True, extra=logger_details(uid))
            return errorResponse(HC_BAD_REQUEST, HEM_FOLDER_NAME_EXIST)

        # Create the new folder on disk
        os.makedirs(current_path, exist_ok=True)

        # Add the new folder to the parent's subfolders
        uploads.create_subfolder(parent_folder, payload.folder_name, current_path)

        # Update the user's drive entry in the database
        drive_collection.update_one({"_id": uid}, {"$set": user_drive}, upsert=True)

        logger.info(HSM_FOLDER_CREATE_SUCCESS, extra=logger_details(uid))
        return successResponse(HC_OK, HSM_FOLDER_CREATE_SUCCESS)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error while creating folder: {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
