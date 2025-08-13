import os
import traceback
import zipfile
from datetime import datetime


class FileDownload:
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

    def create_zip_file(self, folder_path, uid, item_name):
        try:
            destination_folder = os.path.join(os.getcwd(), 'Downloads', 'FinalOutput', 'AllPDFzip')

            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            zip_file_path = os.path.join(destination_folder,
                                         f"{uid}_{item_name}_{datetime.today().strftime('%Y%d%m%H%M%S')}.zip")
            with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zip_relative_path = os.path.relpath(file_path, folder_path)
                        zip_file.write(file_path, arcname=zip_relative_path)
            return zip_file_path

        except Exception as e:
            print(traceback.print_exc())
            print(f"Error create_zip_file: {e}")
            return None

download = FileDownload()
