import base64
import mimetypes
import os
import traceback

from Constant.http import HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR, HC_OK, HC_UNAUTHORISED, \
    HSM_DATA_FETCHED_SUCCESS, HC_BAD_REQUEST, HEM_FILE_NOT_FOUND, \
    HC_NOT_FOUND, HEM_ITEM_NOT_FOUND, HEM_ZIP_CREATION_FAILED, HSM_DOWNLOAD_SUCCESSFULLY
from Utils.V1.db import drive_collection
from Utils.V1.file_content_function import download
from Utils.V1.logger import logger
from Utils.V1.response import errorResponse, successResponse
from Utils.V1.utility_functions import logger_details


def get_file_content(payload, user):
    """
    Retrieve the content of a file or folder.

    :param payload: Request payload containing owner_id and item_id
    :param user: User information obtained from the authentication middleware
    :return: JSON response indicating the success or failure of the retrieval
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True,
                         extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        # Fetch the owner's drive
        user_drive = drive_collection.find_one({"_id": payload.owner_id})

        # Find the item in the owner's drive
        item, item_type = download.find_item_in_drive(user_drive, payload.item_id)
        if not item:
            logger.error(HEM_ITEM_NOT_FOUND, exc_info=True, extra=logger_details(uid))
            return errorResponse(HC_BAD_REQUEST, HEM_ITEM_NOT_FOUND)

        item_path = item["path"]
        item_name = item["name"]

        # Handle file type item
        if item_type == "file":
            if os.path.exists(item_path):
                with open(item_path, "rb") as file:
                    file_content = base64.b64encode(file.read()).decode('utf-8')
                logger.info(HSM_DATA_FETCHED_SUCCESS, extra=logger_details(uid))
                return successResponse(HC_OK, HSM_DATA_FETCHED_SUCCESS, {
                    "file_content": file_content,
                    "file_name": item_name,
                    "mimetype": mimetypes.guess_type(item_name)[0]
                })
            else:
                logger.error(HEM_FILE_NOT_FOUND, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_NOT_FOUND, HEM_FILE_NOT_FOUND)

        # Handle folder type item
        elif item_type == "folder":
            zip_file_path = download.create_zip_file(item_path, uid, item_name)
            if zip_file_path:
                with open(zip_file_path, "rb") as zip_file:
                    zip_content = base64.b64encode(zip_file.read()).decode('utf-8')

                # Remove the zip file after encoding it
                os.remove(zip_file_path)

                logger.info(HSM_DOWNLOAD_SUCCESSFULLY, extra=logger_details(uid))
                return successResponse(HC_OK, HSM_DOWNLOAD_SUCCESSFULLY, {
                    "file_content": zip_content,
                    "file_name": f"{item_name}.zip",
                    "mimetype": "application/zip"
                })
            else:
                logger.error(HEM_ZIP_CREATION_FAILED, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_ZIP_CREATION_FAILED)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error while executing get_file_content API: {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
