import secrets

def generate_random_string(length=32):
    return secrets.token_hex(length // 2)

random_string = generate_random_string()
print(random_string)





# from pymongo import MongoClient
# from bson.objectid import ObjectId
# from datetime import datetime
# from fastapi import FastAPI, Request, Depends, UploadFile, File, Form
# from typing import List
#
# from Utils.V1.config_reader import configure
#
# app = FastAPI()
#
# # MongoDB connection
# client = MongoClient("mongodb://sa:963852@192.168.102.120:27017/?authSource=admin")
# db = client["DRIVE_SHARING"]
#
# # Define MongoDB collections
# drive_collection = db["drive"]
# sharing_collection = db["sharing"]
#
# # Function to get new ID
# def get_new_id(prefix: str, count: int) -> str:
#     return f"{prefix}_{count + 1}"
#
# # Function to insert folder record
# def insert_folder_record(uid: str, folder_name: str, parent_id: str = None):
#     user_drive = drive_collection.find_one({"_id": uid})
#     folder_id = get_new_id("FOL", 0)
#     created_at = updated_at = datetime.utcnow().isoformat()
#
#     new_folder = {
#         "folder_id": folder_id,
#         "name": folder_name,
#         "path": f"G:\\DriveSharing\\LocalStorage\\{uid}\\{folder_name}",
#         "created_at": created_at,
#         "updated_at": updated_at,
#         "files": []
#     }
#
#     if parent_id:
#         for folder in user_drive["drive"]["folders"]:
#             if folder["folder_id"] == parent_id:
#                 folder.setdefault("folders", []).append(new_folder)
#     else:
#         user_drive["drive"]["folders"].append(new_folder)
#
#     drive_collection.update_one({"_id": uid}, {"$set": {"drive": user_drive["drive"]}})
#     return folder_id
#
# # Function to insert file record
# def insert_file_record(uid: str, file_name: str, parent_id: str = None):
#     user_drive = drive_collection.find_one({"_id": uid})
#     file_id = get_new_id("FIL", 0)
#     created_at = updated_at = datetime.utcnow().isoformat()
#
#     new_file = {
#         "file_id": file_id,
#         "name": file_name,
#         "path": f"G:\\DriveSharing\\LocalStorage\\{uid}\\{file_name}",
#         "created_at": created_at,
#         "updated_at": updated_at
#     }
#
#     if parent_id:
#         for folder in user_drive["drive"]["folders"]:
#             if folder["folder_id"] == parent_id:
#                 folder["files"].append(new_file)
#     else:
#         user_drive["drive"]["files"].append(new_file)
#
#     drive_collection.update_one({"_id": uid}, {"$set": {"drive": user_drive["drive"]}})
#     return file_id
#
# @app.post("/upload-folder")
# async def upload_folder(uid: str = Form(...), folder_name: str = Form(...), parent_id: str = Form(None)):
#     folder_id = insert_folder_record(uid, folder_name, parent_id)
#     return {"message": "Folder uploaded successfully", "folder_id": folder_id}
#
# @app.post("/upload-file")
# async def upload_file(uid: str = Form(...), file_name: str = Form(...), parent_id: str = Form(None)):
#     file_id = insert_file_record(uid, file_name, parent_id)
#     return {"message": "File uploaded successfully", "file_id": file_id}
#
# @app.get("/get-my-drive")
# async def get_my_drive(uid: str, folder_id: str = None):
#     user_drive = drive_collection.find_one({"_id": uid})
#     if folder_id:
#         for folder in user_drive["drive"]["folders"]:
#             if folder["folder_id"] == folder_id:
#                 return {"folders": folder.get("folders", []), "files": folder["files"]}
#     else:
#         return {"folders": user_drive["drive"]["folders"], "files": user_drive["drive"]["files"]}
#
# # API for sharing files and folders
# @app.post("/share")
# async def share_item(file_id: str = Form(None), folder_id: str = Form(None), shared_with: str = Form(...), permission: str = Form(...)):
#     sharing_data = {
#         "file_id": file_id,
#         "folder_id": folder_id,
#         "shared_with": shared_with,
#         "permission": permission,
#         "shared_at": datetime.utcnow().isoformat()
#     }
#     sharing_collection.insert_one(sharing_data)
#     return {"message": "Item shared successfully"}
#
# # Running the FastAPI server
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host=configure.get("SERVER", "HOST"), port=8765)










