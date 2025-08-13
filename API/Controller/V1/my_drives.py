import traceback

from Constant.general import SHARED, MY_DRIVE, FAVOURITES
from Constant.http import HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR, HC_OK, HC_UNAUTHORISED, \
    HSM_DATA_FETCHED_SUCCESS, HEM_FOLDER_NOT_EXISTS, HC_NOT_FOUND
from Utils.V1.logger import logger
from Utils.V1.my_drive_function import drive
from Utils.V1.response import errorResponse, successResponse
from Utils.V1.utility_functions import logger_details


def get_items(payload, folder_type, user):
    """
    Retrieve items from the user's drive based on the specified folder type.

    :param payload: Request payload containing the necessary parameters.
    :param folder_type: The type of folder to retrieve items from (e.g., SHARED, MY_DRIVE, FAVOURITES).
    :param user: User information obtained from the authentication middleware.
    :return: JSON response indicating the success or failure of the operation.
    """
    try:
        if 'error_message' in user:
            logger.error(user['error_message'], exc_info=True, extra=logger_details("-"))
            return errorResponse(HC_UNAUTHORISED, user['error_message'])

        uid = user['data']['uid']

        if folder_type == SHARED:
            data = drive.fetch_shared_items(uid)

        elif folder_type == MY_DRIVE:
            data = drive.fetch_my_drive_items(uid, payload)
            if data == HEM_FOLDER_NOT_EXISTS:
                logger.error(HEM_FOLDER_NOT_EXISTS, exc_info=True, extra=logger_details(uid))
                return errorResponse(HC_NOT_FOUND, HEM_FOLDER_NOT_EXISTS)

        elif folder_type == FAVOURITES:
            data = drive.fetch_favorite_items(uid)
        else:
            data = {}

        logger.info(HSM_DATA_FETCHED_SUCCESS, extra=logger_details(uid))
        return successResponse(HC_OK, HSM_DATA_FETCHED_SUCCESS, data)

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"error while executing my drive API {e}", exc_info=True, extra=logger_details(uid))
        return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)

# def get_items(payload, folder_type, user):
#     """
#     Retrieve items from the user's drive based on the specified folder type.
#
#     :param payload: Request payload containing the necessary parameters.
#     :param folder_type: The type of folder to retrieve items from (e.g., SHARED, MY_DRIVE, FAVOURITES).
#     :param user: User information obtained from the authentication middleware.
#     :return: JSON response indicating the success or failure of the operation.
#     """
#     try:
#         if 'error_message' in user:
#             logger.error(user['error_message'], exc_info=True,
#                          extra=logger_details("-"))
#             return errorResponse(HC_UNAUTHORISED, user['error_message'])
#
#         uid = user['data']['uid']
#
#         if folder_type == SHARED:
#             # Fetch all shared items for the given user
#             shared_items = sharing_collection.find({"shared_user": uid})
#             folders_data = []
#             files_data = []
#             for item in shared_items:
#                 owner_drive = drive_collection.find_one({"_id": item["owner_id"]})
#
#                 if owner_drive:
#                     # Find the shared item in the owner's drive
#                     shared_item, item_type = drive.find_item_in_drive(owner_drive, item["shared_item_id"])
#                     if shared_item:
#                         if item_type == "file":
#                             files_data.append({
#                                 "_id": item["shared_item_id"],
#                                 "owner_id": item["owner_id"],
#                                 "name": shared_item["name"],
#                                 "created_at": shared_item.get("created_at", ""),
#                                 "access_users": [{"user_id": info["shared_user"], "access": info["access_type"]} for
#                                                  info in
#                                                  sharing_collection.find({"shared_item_id": str(shared_item["_id"])})],
#                                 "size": shared_item.get("size", 0),
#                                 "mimetype": mimetypes.guess_type(shared_item["name"])[0],
#                                 "thumbnail": drive.generate_thumbnail(shared_item["path"]),
#                                 "favorite": drive.is_favorite(uid, str(item["shared_item_id"]))
#                             })
#
#                         elif item_type == "folder":
#                             num_folders = len(shared_item.get("folders", []))
#                             num_files = len(shared_item.get("files", []))
#                             folders_data.append({
#                                 "_id": item["shared_item_id"],
#                                 "owner_id": item["owner_id"],
#                                 "name": shared_item["name"],
#                                 "created_at": shared_item.get("created_at", ""),
#                                 "access_users": [{"user_id": info["shared_user"], "access": info["access_type"]} for
#                                                  info in
#                                                  sharing_collection.find({"shared_item_id": str(shared_item["_id"])})],
#                                 "mimetype": "folder",
#                                 "item_count": num_folders + num_files,
#                                 "favorite": drive.is_favorite(uid, str(item["shared_item_id"]))
#                             })
#
#                 else:
#                     continue
#
#             data = {"folders": folders_data, "files": files_data}
#
#         elif folder_type == MY_DRIVE:
#             # Fetch the user's drive entry
#             if payload.owner_id:
#                 user_drive = drive_collection.find_one({"_id": payload.owner_id})
#             else:
#                 user_drive = drive_collection.find_one({"_id": uid})
#
#             if not user_drive:
#                 data = {}
#                 logger.info(HSM_DATA_FETCHED_SUCCESS, extra=logger_details(uid))
#                 return successResponse(HC_OK, HSM_DATA_FETCHED_SUCCESS, data)
#
#             if payload.folder_id:
#                 folder_id = ObjectId(payload.folder_id)
#                 parent_folder = drive.find_folder_in_drive(user_drive, folder_id)
#                 if not parent_folder:
#                     logger.error(HEM_FOLDER_NOT_EXISTS, exc_info=True, extra=logger_details(uid))
#                     return errorResponse(HC_NOT_FOUND, HEM_FOLDER_NOT_EXISTS)
#
#                 folders = parent_folder.get("folders", [])
#                 files = parent_folder.get("files", [])
#             else:
#                 folders = user_drive.get("folders", [])
#                 files = user_drive.get("files", [])
#
#             folders_data = [{"_id": str(folder["_id"]),
#                              "owner_id": payload.owner_id if payload.owner_id else uid,
#                              "name": folder["name"],
#                              "created_at": folder.get("created_at", ""),
#                              "access_users": [{"user_id": info["shared_user"], "access": info["access_type"]} for info
#                                               in sharing_collection.find({"shared_item_id": str(folder["_id"])})],
#                              "mimetype": "folder",
#                              "item_count": len(folder.get("folders", [])) + len(folder.get("files", [])),
#                              "favorite": drive.is_favorite(uid, str(folder["_id"]))} for folder in folders]
#
#             files_data = [
#                 {"_id": str(file["_id"]),
#                  "owner_id": payload.owner_id if payload.owner_id else uid,
#                  "name": file["name"],
#                  "created_at": file.get("created_at", ""),
#                  "access_users": [{"user_id": info["shared_user"], "access": info["access_type"]} for info in
#                                   sharing_collection.find({"shared_item_id": str(file["_id"])})],
#                  "size": file.get("size", 0),
#                  "mimetype": mimetypes.guess_type(file["name"])[0],
#                  "thumbnail": drive.generate_thumbnail(file["path"]),
#                  "favorite": drive.is_favorite(uid, str(file["_id"]))}
#                 for file in files]
#
#             data = {"folders": folders_data, "files": files_data}
#
#         elif folder_type == FAVOURITES:
#             # Fetch all shared items for the given user
#             favorite_items = favorites_collection.find({"favourite_by": uid})
#             folders_data = []
#             files_data = []
#             for item in favorite_items:
#                 owner_drive = drive_collection.find_one({"_id": item["owner_id"]})
#
#                 if owner_drive:
#                     # Find the shared item in the owner's drive
#                     favorite_item, item_type = drive.find_item_in_drive(owner_drive, item["item_id"])
#                     if favorite_item:
#                         if item_type == "file":
#                             files_data.append({
#                                 "_id": item["item_id"],
#                                 "owner_id": item["owner_id"],
#                                 "name": favorite_item["name"],
#                                 "created_at": favorite_item.get("created_at", ""),
#                                 "access_users": [{"user_id": info["shared_user"], "access": info["access_type"]} for
#                                                  info in sharing_collection.find(
#                                         {"shared_item_id": str(favorite_item["_id"])})],
#                                 "size": favorite_item.get("size", 0),
#                                 "mimetype": mimetypes.guess_type(favorite_item["name"])[0],
#                                 "thumbnail": drive.generate_thumbnail(favorite_item["path"]),
#                                 "favorite": drive.is_favorite(uid, str(item["item_id"]))
#                             })
#
#                         elif item_type == "folder":
#                             num_folders = len(favorite_item.get("folders", []))
#                             num_files = len(favorite_item.get("files", []))
#                             folders_data.append({
#                                 "_id": item["item_id"],
#                                 "owner_id": item["owner_id"],
#                                 "name": favorite_item["name"],
#                                 "created_at": favorite_item.get("created_at", ""),
#                                 "access_users": [{"user_id": info["shared_user"], "access": info["access_type"]} for
#                                                  info in
#                                                  sharing_collection.find(
#                                                      {"shared_item_id": str(favorite_item["_id"])})],
#                                 "mimetype": "folder",
#                                 "item_count": num_folders + num_files,
#                                 "favorite": drive.is_favorite(uid, str(item["item_id"]))
#                             })
#
#                 else:
#                     continue
#
#             data = {"folders": folders_data, "files": files_data}
#
#         else:
#             data = {}
#
#         logger.info(HSM_DATA_FETCHED_SUCCESS, extra=logger_details(uid))
#         return successResponse(HC_OK, HSM_DATA_FETCHED_SUCCESS, data)
#
#     except Exception as e:
#         traceback.print_exc()
#         logger.exception(f"error while executing get items API {e}", exc_info=True, extra=logger_details(uid))
#         return errorResponse(HC_INTERNAL_SERVER_ERROR, HEM_SERVER_ERROR)
