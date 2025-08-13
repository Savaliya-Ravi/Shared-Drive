import base64
import mimetypes
import traceback
from io import BytesIO

import fitz
from PIL import Image, UnidentifiedImageError
from bson import ObjectId

from Constant.http import HEM_NO_THUMBNAIL, HEM_FOLDER_NOT_EXISTS
from Utils.V1.db import favorites_collection, sharing_collection, drive_collection


class MyDrive:

    def generate_thumbnail(self, file_path):
        try:
            mime_type, _ = mimetypes.guess_type(file_path)

            if mime_type and mime_type.startswith('image/'):
                return self.generate_image_thumbnail(file_path=file_path)
            elif mime_type and mime_type == 'application/pdf':
                return self.generate_pdf_thumbnail(file_path=file_path)
            elif mime_type and mime_type == 'application/zip':
                return HEM_NO_THUMBNAIL
            else:
                # Handle other file types (e.g., .py, .php, .html) with a default thumbnail
                return HEM_NO_THUMBNAIL
        except:
            print("Error in generate thumbnail.")
            traceback.print_exc()

    def generate_image_thumbnail(self, file_path=None, size=(512, 512)):
        try:
            with Image.open(file_path) as img:
                img.thumbnail(size)
                if img.mode in ("RGBA", "LA"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, (0, 0), img)
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                return base64.b64encode(buffered.getvalue()).decode()
        except UnidentifiedImageError:
            return self.generate_image_thumbnail()

    def generate_pdf_thumbnail(self, file_path, size=(512, 512)):
        doc = fitz.open(file_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img.thumbnail(size)
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()

    def is_favorite(self, uid, item_id):
        return favorites_collection.find_one({"favourite_by": uid, "item_id": item_id}) is not None

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

    def fetch_shared_items(self, uid):
        shared_items = sharing_collection.find({"shared_user": uid})
        folders_data = []
        files_data = []

        for item in shared_items:
            owner_drive = drive_collection.find_one({"_id": item["owner_id"]})
            if owner_drive:
                shared_item, item_type = drive.find_item_in_drive(owner_drive, item["shared_item_id"])
                if shared_item:
                    if item_type == "file":
                        files_data.append(self.create_file_data(shared_item, item["shared_item_id"], item["owner_id"], uid))
                    elif item_type == "folder":
                        folders_data.append(
                            self.create_folder_data(shared_item, item["shared_item_id"], item["owner_id"], uid))

        return {"folders": folders_data, "files": files_data}

    def fetch_my_drive_items(self, uid, payload):
        user_drive = drive_collection.find_one({"_id": payload.owner_id if payload.owner_id else uid})
        if not user_drive:
            return {}

        if payload.folder_id:
            folder_id = ObjectId(payload.folder_id)
            parent_folder = drive.find_folder_in_drive(user_drive, folder_id)
            if not parent_folder:
                return HEM_FOLDER_NOT_EXISTS

            folders = parent_folder.get("folders", [])
            files = parent_folder.get("files", [])
        else:
            folders = user_drive.get("folders", [])
            files = user_drive.get("files", [])

        folders_data = [self.create_folder_data(folder, folder["_id"], uid, uid) for folder in folders]
        files_data = [self.create_file_data(file, file["_id"], uid, uid) for file in files]

        return {"folders": folders_data, "files": files_data}

    def fetch_favorite_items(self, uid):
        favorite_items = favorites_collection.find({"favourite_by": uid})
        folders_data = []
        files_data = []

        for item in favorite_items:
            owner_drive = drive_collection.find_one({"_id": item["owner_id"]})
            if owner_drive:
                favorite_item, item_type = drive.find_item_in_drive(owner_drive, item["item_id"])
                if favorite_item:
                    if item_type == "file":
                        files_data.append(self.create_file_data(favorite_item, item["item_id"], item["owner_id"], uid))
                    elif item_type == "folder":
                        folders_data.append(self.create_folder_data(favorite_item, item["item_id"], item["owner_id"], uid))

        return {"folders": folders_data, "files": files_data}

    def create_file_data(self, file, file_id, owner_id, uid):
        return {
            "_id": str(file_id),
            "owner_id": owner_id,
            "name": file["name"],
            "created_at": file.get("created_at", ""),
            "access_users": self.get_access_users(file_id),
            "size": file.get("size", 0),
            "mimetype": mimetypes.guess_type(file["name"])[0],
            "thumbnail": drive.generate_thumbnail(file["path"]),
            "favorite": drive.is_favorite(uid, str(file_id))
        }

    def create_folder_data(self, folder, folder_id, owner_id, uid):
        return {
            "_id": str(folder_id),
            "owner_id": owner_id,
            "name": folder["name"],
            "created_at": folder.get("created_at", ""),
            "access_users": self.get_access_users(folder_id),
            "mimetype": "folder",
            "item_count": len(folder.get("folders", [])) + len(folder.get("files", [])),
            "favorite": drive.is_favorite(uid, str(folder_id))
        }

    def get_access_users(self, item_id):
        return [{"user_id": info["shared_user"], "access": info["access_type"]}
                for info in sharing_collection.find({"shared_item_id": str(item_id)})]


drive = MyDrive()
