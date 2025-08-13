import os
import shutil
import traceback
from datetime import datetime

from bson import ObjectId

from Constant.http import HEM_FILE_NAME_EXIST, HEM_FOLDER_NAME_EXIST, HEM_ITEM_NOT_FOUND, HEM_FOLDER_NOT_EXISTS


class CopyFileFolder:
    def find_item_in_drive(self, drive, item_id):
        for file in drive.get("files", []):
            if str(file["_id"]) == str(item_id):
                return file, "file"
        for folder in drive.get("folders", []):
            if str(folder["_id"]) == str(item_id):
                return folder, "folder"
            found_item, item_type = self.find_item_in_drive(folder, item_id)
            if found_item:
                return found_item, item_type
        return None, None

    # function to find the destination folder
    def find_folder_in_drive(self, drive, folder_id):
        if str(drive["_id"]) == str(folder_id):
            return drive
        for folder in drive.get("folders", []):
            if str(folder["_id"]) == str(folder_id):
                return folder
            found_folder = self.find_folder_in_drive(folder, folder_id)
            if found_folder:
                return found_folder
        return None

    def save_copied_item(self, item, destination_folder, item_type):
        if item_type == "folder":
            new_folder = {
                "_id": ObjectId(),
                "name": item["name"],
                "path": os.path.join(destination_folder["path"], item["name"]),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "folders": [],
                "files": []
            }
            destination_folder["folders"].append(new_folder)
            for sub_folder in item.get("folders", []):
                self.save_copied_item(sub_folder, new_folder, "folder")
            for file in item.get("files", []):
                self.save_copied_item(file, new_folder, "file")
        elif item_type == "file":
            new_file = {
                "_id": ObjectId(),
                "name": item["name"],
                "path": os.path.join(destination_folder["path"], item["name"]),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            destination_folder["files"].append(new_file)
            try:
                os.makedirs(os.path.dirname(new_file["path"]), exist_ok=True)
                shutil.copyfile(item["path"], new_file["path"])
            except shutil.SameFileError:
                return HEM_FILE_NAME_EXIST
        return None

    def item_name_exists_in_destination(self, item_to_move, item_type, destination_folder):
        try:
            if item_type == "file" and any(
                    f["name"] == item_to_move["name"] for f in destination_folder.get("files", [])):
                return HEM_FILE_NAME_EXIST
            if item_type == "folder" and any(
                    f["name"] == item_to_move["name"] for f in destination_folder.get("folders", [])):
                return HEM_FOLDER_NAME_EXIST
            return None
        except:
            traceback.print_exc()

    # # function to save folder structure
    # def save_folder_structure(self, folder, destination_folder):
    #     for existing_folder in destination_folder.get("folders", []):
    #         if existing_folder["name"] == folder["name"]:
    #             return HEM_FOLDER_NAME_EXIST
    #
    #     new_folder = {
    #         "_id": ObjectId(),
    #         "name": folder["name"],
    #         "path": os.path.join(destination_folder["path"], folder["name"]),
    #         "created_at": datetime.utcnow().isoformat(),
    #         "updated_at": datetime.utcnow().isoformat(),
    #         "folders": [],
    #         "files": []
    #     }
    #
    #     for sub_folder in folder.get("folders", []):
    #         result = self.save_folder_structure(sub_folder, new_folder)
    #         if result:
    #             return result
    #     for file in folder.get("files", []):
    #         result = self.save_file_structure(file, new_folder)
    #         if result:
    #             return result
    #
    #     destination_folder["folders"].append(new_folder)
    #     return None
    #
    # # function to save file structure
    # def save_file_structure(self, file, destination_folder):
    #     for existing_file in destination_folder.get("files", []):
    #         if existing_file["name"] == file["name"]:
    #             return HEM_FILE_NAME_EXIST
    #
    #     new_file = {
    #         "_id": ObjectId(),
    #         "name": file["name"],
    #         "path": os.path.join(destination_folder["path"], file["name"]),
    #         "created_at": datetime.utcnow().isoformat(),
    #         "updated_at": datetime.utcnow().isoformat()
    #     }
    #
    #     try:
    #         os.makedirs(os.path.dirname(new_file["path"]), exist_ok=True)
    #         shutil.copyfile(file["path"], new_file["path"])
    #     except shutil.SameFileError:
    #         return HEM_FILE_NAME_EXIST
    #
    #     destination_folder["files"].append(new_file)
    #     return None

    def find_item_and_destination(self, user_drive, item_id, destination_folder_id):
        item_to_copy, item_type = self.find_item_in_drive(user_drive, item_id)
        if not item_to_copy:
            return None, None, HEM_ITEM_NOT_FOUND

        if destination_folder_id:
            destination_folder = self.find_folder_in_drive(user_drive, destination_folder_id)
            if not destination_folder:
                return None, None, HEM_FOLDER_NOT_EXISTS
        else:
            destination_folder = user_drive

        return item_to_copy, item_type, destination_folder

    # def copy_item_to_destination(self, item_to_copy, item_type, destination_folder, user_host):
    #     if item_type == "file":
    #         result = self.save_file_structure(item_to_copy, destination_folder)
    #     elif item_type == "folder":
    #         result = self.save_folder_structure(item_to_copy, destination_folder)
    #     else:
    #         return HEM_ITEM_NOT_FOUND
    #     if result in [HEM_FOLDER_NAME_EXIST, HEM_FILE_NAME_EXIST]:
    #         return result
    #     return None


copies = CopyFileFolder()
