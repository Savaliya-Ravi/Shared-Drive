import os


class RenameFileFolder:
    def find_item_in_drive(self, drive, item_id):
        for file in drive.get("files", []):
            if str(file["_id"]) == str(item_id):
                return file, "file", drive
        for folder in drive.get("folders", []):
            if str(folder["_id"]) == str(item_id):
                return folder, "folder", drive
            found_item, item_type, parent = self.find_item_in_drive(folder, item_id)
            if found_item:
                return found_item, item_type, parent
        return None, None, None

    def update_paths_recursively(self, item, old_base_path, new_base_path):
        item["path"] = item["path"].replace(old_base_path, new_base_path)
        if "folders" in item:
            for folder in item["folders"]:
                self.update_paths_recursively(folder, old_base_path, new_base_path)
        if "files" in item:
            for file in item["files"]:
                file["path"] = file["path"].replace(old_base_path, new_base_path)

    def rename_item_in_drive(self, item, new_name, item_type):
        old_path = item["path"]
        if item_type == "file":
            old_extension = os.path.splitext(old_path)[-1]
            new_name = f"{new_name}{old_extension}"

        new_path = os.path.join(os.path.dirname(old_path), new_name)
        item["name"] = new_name
        item["path"] = new_path

        try:
            os.rename(old_path, new_path)
        except OSError as e:
            return str(e)

        if item_type == "folder":
            self.update_paths_recursively(item, old_path, new_path)

        return None


rename = RenameFileFolder()
