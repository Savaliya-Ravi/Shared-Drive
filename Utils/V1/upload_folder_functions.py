import os
import shutil
import traceback
from bson import ObjectId
from datetime import datetime
from Constant.http import HEM_FILE_NAME_EXIST, HEM_FOLDER_NAME_EXIST
from Utils.V1.utility_functions import utility


class UploadFileFolder:
    def save_folder_structure(self, drive, files, base_path, parent_folder_id):
        try:
            for upload_file in files:
                parent_folder = utility.find_folder(drive["folders"], parent_folder_id) if parent_folder_id else None
                if parent_folder:
                    current_path = parent_folder['path']
                else:
                    current_path = base_path

                path_parts = upload_file.filename.split('/')

                for i, part in enumerate(path_parts):
                    if part:
                        current_path = os.path.join(current_path, part)

                        if i < len(path_parts) - 1:
                            # It's a folder
                            if parent_folder:
                                result = self.create_or_find_subfolder(parent_folder, part, current_path)
                            else:
                                result = self.create_or_find_subfolder(drive, part, current_path)
                            if result == HEM_FOLDER_NAME_EXIST:
                                return HEM_FOLDER_NAME_EXIST
                            parent_folder = result
                        else:
                            # It's a file
                            os.makedirs(os.path.dirname(current_path), exist_ok=True)
                            self.save_file_to_disk(upload_file, current_path)
                            file_size = upload_file.size

                            new_file = {
                                "_id": ObjectId(),
                                "name": part,
                                "path": current_path,
                                "size": file_size,
                                "created_at": datetime.utcnow().isoformat(),
                                "updated_at": datetime.utcnow().isoformat()
                            }
                            if parent_folder:
                                if not self.check_duplicate_file_path(parent_folder["files"], current_path):
                                    parent_folder["files"].append(new_file)
                                else:
                                    return HEM_FILE_NAME_EXIST
                            else:
                                if not self.check_duplicate_file_path(drive["files"], current_path):
                                    drive["files"].append(new_file)
                                else:
                                    return HEM_FILE_NAME_EXIST
        except Exception as e:
            print(traceback.print_exc())

    def save_file_structure(self, drive, file, base_path, parent_folder_id):
        try:
            filename = file.filename
            parent_folder = utility.find_folder(drive["folders"], parent_folder_id) if parent_folder_id else None

            if parent_folder:
                current_path = parent_folder['path']
            else:
                current_path = base_path

            current_path = os.path.join(current_path, filename)

            # Save the file
            os.makedirs(os.path.dirname(current_path), exist_ok=True)
            self.save_file_to_disk(file, current_path)

            file_size = file.size
            new_file = {
                "_id": ObjectId(),
                "name": filename,
                "path": current_path,
                "size": file_size,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            if parent_folder:
                if not uploads.check_duplicate_file_path(parent_folder["files"], current_path):
                    parent_folder["files"].append(new_file)
                else:
                    return HEM_FILE_NAME_EXIST
            else:
                if not uploads.check_duplicate_file_path(drive["files"], current_path):
                    drive["files"].append(new_file)
                else:
                    return HEM_FILE_NAME_EXIST

        except Exception as e:
            print(traceback.print_exc())

    def create_or_find_subfolder(self, parent, folder_name, folder_path):
        try:
            # Find if the subfolder already exists within the same parent folder based on path
            for folder in parent.get("folders", []):
                if folder["path"] == folder_path:
                    return folder

            # If not, create a new subfolder
            new_folder = {
                "_id": ObjectId(),
                "name": folder_name,
                "path": folder_path,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "files": [],
                "folders": []
            }
            if "folders" not in parent:
                parent["folders"] = []
            parent["folders"].append(new_folder)
            return new_folder
        except Exception as e:
            print(traceback.print_exc())

    def check_duplicate_file_path(self, files, file_path):
        for file in files:
            if file["path"] == file_path:
                return True
        return False

    def save_file_to_disk(self, upload_file, destination):
        try:
            with open(destination, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
        except Exception as e:
            print(traceback.print_exc())

    def create_subfolder(self, parent, folder_name, folder_path):
        try:
            # Find if the subfolder already exists within the same parent folder based on path
            for folder in parent.get("folders", []):
                if folder["path"] == folder_path:
                    return HEM_FOLDER_NAME_EXIST

            # If not, create a new subfolder
            new_folder = {
                "_id": ObjectId(),
                "name": folder_name,
                "path": folder_path,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "files": [],
                "folders": []
            }
            if "folders" not in parent:
                parent["folders"] = []
            parent["folders"].append(new_folder)
            return new_folder
        except Exception as e:
            print(traceback.print_exc())


uploads = UploadFileFolder()
