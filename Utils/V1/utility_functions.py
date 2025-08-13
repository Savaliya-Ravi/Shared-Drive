import datetime
import os
import traceback

from bson import ObjectId

from Constant.general import PROJECT
from Utils.V1.config_reader import configure


def logger_details(uid):
    return {"user_id": uid}


class Utils:
    def get_path(self, config_path, *directories, file_name=None):
        """
        create directory from relative path if not exist

        :param config_path:
        :param file_name:
        :return absolute path of directory:
        """

        loc = os.getcwd().split(PROJECT)
        # final_directory_path = os.path.join(relative_path,)
        path = os.path.join(loc[0], PROJECT, config_path, *directories)

        file_path = path

        # check and create directory if not exist
        if not os.path.exists(path):
            os.makedirs(path)

        if file_name:
            file_path = os.path.join(path, file_name)

        return file_path

    def create_directory(self, path):
        """
        Creates a directory if it does not exist.

        :param path: The path of the directory to create.
        :return: The path of the directory.
        """
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_ini_path(self, config_path, path, is_absolute=True):
        """
        get path from ini file

        :param is_absolute:
        :param path:
        :param ini variable name from PATH section:
        :return absolute path:
        """

        loc = os.getcwd().split(PROJECT)
        directory = os.path.join(loc[0], configure.get(config_path, path))

        if is_absolute:
            directory = configure.get(config_path, path)
        return directory

    def dateConverter(self, date, input_format, output_format):
        """
        convert date to specific format

        :param date:
        :param input_format:
        :param output_format:
        :return formated date:
        """
        if type(date) == type("date"):
            date_obj = datetime.datetime.strptime(date, input_format)
            date_output = date_obj.strftime(output_format)
        else:
            date_output = date.strftime(output_format)
        return date_output

    def addHeader(self, cursor, type="fetchall"):
        """
        Add Header to mysql query output

        :param type:
        :param cursor:
        :return data:
        """
        if type == "fetchall":
            fetch_data = cursor.fetchall()
            if not fetch_data:
                return []
            column_names = [column[0] for column in cursor.description]
            data = []
            for i in fetch_data:
                x = {}
                for k, j in enumerate(column_names):
                    x.update({j: i[k]})
                data.append(x)

        elif type == "fetchone":
            fetch_data = cursor.fetchone()
            if not fetch_data:
                return {}
            column_names = [column[0] for column in cursor.description]
            data = {}
            for k, j in enumerate(column_names):
                data.update({j: fetch_data[k]})

        elif type == "tab_data":
            fetch_data = cursor.fetchall()
            column_names = [column[0] for column in cursor.description]
            data = []
            for i in fetch_data:
                x = {}
                for k, j in enumerate(column_names):
                    if j == 'Units':
                        x.update({j: int(i[k])})
                    else:
                        x.update({j: i[k]})
                data.append(x)

        return data

    def find_folder(self, folders, folder_id):
        try:
            for folder in folders:
                if str(folder["_id"]) == str(folder_id):
                    return folder
                found_folder = self.find_folder(folder.get("folders", []), folder_id)
                if found_folder:
                    return found_folder
            return None
        except Exception as e:
            traceback.print_exc()

    def convert_object_id(self, data):
        if isinstance(data, list):
            for item in data:
                self.convert_object_id(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, ObjectId):
                    data[key] = str(value)
        return data


utility = Utils()
