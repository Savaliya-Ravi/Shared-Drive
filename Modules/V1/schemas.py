from typing import Optional, List

from pydantic import BaseModel


class SchemaName(BaseModel):
    request_1: str
    request_2: Optional[List]


class ResponseSchema():
    class Config:
        orm_mode = True


class CreateFolder(BaseModel):
    folder_name: str
    parent_folder_id: str


class GetDrive(BaseModel):
    folder_id: str
    owner_id: str


class Sharing(BaseModel):
    shared_user: List[str]
    shared_item_id: str
    access_type: str
    group_list: List[str]


class ModifyShare(BaseModel):
    shared_user: str
    shared_item_id: str
    new_access: str


class ActionOnItem(BaseModel):
    item_id: List[str]
    destination_folder_id: str


class FileContent(BaseModel):
    item_id: str
    owner_id: str


class Group(BaseModel):
    group_id: str = None
    group_name: str
    members: List[str]


class Favourite(BaseModel):
    item_id: str
    owner_id: str


class RenameItem(BaseModel):
    item_id: str
    new_name: str
