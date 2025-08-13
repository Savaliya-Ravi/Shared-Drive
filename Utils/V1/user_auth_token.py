from typing import Union

import requests
from fastapi import Header

from Utils.V1.config_reader import configure


def verify_user(auth_token: Union[str] = Header(...)):
    # print("auth_token", auth_token)
    api = f'{configure.get("EXTERNAL_APIs", "erp_token")}'
    token_data = {"authToken": auth_token}
    login_access = requests.get(api, headers=token_data)
    # print(login_access.text)
    if login_access.status_code != 200:
        return {"error_message": login_access.json()['message']}
    return login_access.json()
