import os


class DeleteFileFolder:
    def find_and_delete_item(self, drive, item_id):
        for i, file in enumerate(drive.get("files", [])):
            if str(file["_id"]) == str(item_id):
                del drive["files"][i]
                # Delete file from local storage
                if os.path.exists(file["path"]):
                    os.remove(file["path"])
                return True
        for i, folder in enumerate(drive.get("folders", [])):
            if str(folder["_id"]) == str(item_id):
                # Delete folder recursively from local storage
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


deletes = DeleteFileFolder()
