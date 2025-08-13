import os
import shutil
from datetime import datetime

from bson import ObjectId

from Constant.http import HEM_FILE_NAME_EXIST, HEM_ITEM_NOT_FOUND, HEM_FOLDER_NAME_EXIST, HEM_FOLDER_NOT_EXISTS


class MoveFileFolder:

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

    def save_moved_item(self, item, destination_folder, item_type):
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
                self.save_moved_item(sub_folder, new_folder, "folder")
            for file in item.get("files", []):
                self.save_moved_item(file, new_folder, "file")
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

    def find_and_delete_item(self, drive, item_id):
        for i, file in enumerate(drive.get("files", [])):
            if str(file["_id"]) == str(item_id):
                del drive["files"][i]
                if os.path.exists(file["path"]):
                    os.remove(file["path"])
                return True
        for i, folder in enumerate(drive.get("folders", [])):
            if str(folder["_id"]) == str(item_id):
                self.delete_folder_recursive(folder["path"])
                del drive["folders"][i]
                return True
            if self.find_and_delete_item(folder, item_id):
                return True
        return False

    def delete_folder_recursive(self, folder_path):
        if os.path.exists(folder_path):
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(folder_path)

    def find_item_and_destination_for_move(self, user_drive, item_id, destination_folder_id):
        item_to_move, item_type = moving.find_item_in_drive(user_drive, item_id)
        if not item_to_move:
            return None, None, HEM_ITEM_NOT_FOUND

        if destination_folder_id:
            destination_folder = moving.find_folder_in_drive(user_drive, destination_folder_id)
            if not destination_folder:
                return None, None, HEM_FOLDER_NOT_EXISTS
        else:
            destination_folder = user_drive

        return item_to_move, item_type, destination_folder

    def item_name_exists_in_destination(self, item_to_move, item_type, destination_folder):
        if item_type == "file" and any(f["name"] == item_to_move["name"] for f in destination_folder.get("files", [])):
            return HEM_FILE_NAME_EXIST
        if item_type == "folder" and any(
                f["name"] == item_to_move["name"] for f in destination_folder.get("folders", [])):
            return HEM_FOLDER_NAME_EXIST
        return None

    def move_item_to_destination(self, item_to_move, destination_folder, item_type, user_drive, item_id):
        move_result = moving.save_moved_item(item_to_move, destination_folder, item_type)
        if move_result:
            return move_result

        if not moving.find_and_delete_item(user_drive, item_id):
            return HEM_ITEM_NOT_FOUND

        return None


moving = MoveFileFolder()
