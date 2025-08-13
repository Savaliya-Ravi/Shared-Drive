import re
from jose import jwt
from fastapi import HTTPException,status
from passlib.context import CryptContext
from datetime import datetime, timedelta

from Constant.http import *
import random,string
from Utils.V1.config_reader import configure


# ------------------------------------------------Token Generation ------------------------
def email(email_id):
    """
    This function check an email format

    :param email_id: str
                        Your email id
    :return: Boolean
    """
    # format = "^[a-zA-Z0-9-_.]+@[a-zA-Z0-9]+\.[a-z]{1,4}$"
    format = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.match(format, email_id):
        return True
    return False


def verifyUsername(username):
    '''
    checks username if it is alphanumeric

    :param username:
    :return bool:
    '''
    # Define a regular expression pattern to match alphanumeric characters
    if username.isalnum() and not username.isdigit():
    # if bool(re.search(r'[a-zA-Z]', username)) and not re.search(r'\s', username) and not username.isdigit():
        return True
    return False


def generate_otp():
    '''
    generates 6 digit random number
    :return: number
    '''
    otp = random.randint(100000, 999999)
    return otp


def create_access_token(data: dict):
    '''
    generates token on login
    :param data:
    :param expires_delta:
    :return: authToken
    '''
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=configure.getint("AUTHENTICATION","TOKEN_EXPIRE_MINUTES"))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, configure.get("AUTHENTICATION","TOKEN_KEY"), algorithm=configure.get("AUTHENTICATION","TOKEN_ALGORITHM"))
    return encoded_jwt


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/V1/login")
def decode_access_token(token):
    '''
    decode token generated on login
    :param token:
    :return: username
    '''

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Signature Expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, configure.get("AUTHENTICATION","TOKEN_KEY"), algorithms=[configure.get("AUTHENTICATION","TOKEN_ALGORITHM")])
        user: str = payload.get("user")
        # if user is None:
        #     raise credentials_exception
        # token_data = schemas.TokenData(username=user)
        # return successResponse(HC_OK,HEM_TOKEN_SUCCESS,{"username": user})
        return {"status_code":HC_OK,"status":HS_SUCCESS,"message":HEM_TOKEN_SUCCESS,"data":{"username":user}}
    except jwt.ExpiredSignatureError:
        # return errorResponse(HC_UNAUTHORISED,HEM_TOKEN_EXPIRED)
        return {"status_code":HC_UNAUTHORISED,"status":HS_ERROR,"message":HEM_TOKEN_EXPIRED}
    except:
        # return errorResponse(HC_UNAUTHORISED,HEM_TOKEN_EXPIRED)
        return {"status_code":HC_UNAUTHORISED,"status":HS_ERROR,"message":HEM_TOKEN_INVALID}

        # return {"error"}
        # return errorResponse(HC_UNAUTHORISED,HEM_TOKEN_INVALID)





pwd_cxt = CryptContext(schemes=['bcrypt'], deprecated="auto")

def get_pwd_hash( password):
    """
    This fuction convert plain password to hashed password

    Parameters
    __________

    :param password: str
                    Required param
    :return: str
            This fuction return hashed password
    """
    return pwd_cxt.hash(password)

def verify_pwd( plain_pwd, hashed_pwd):
    """
    This function verify the password given plain password and store hashed password same or not

    Parameters
    __________

    :param plain_pwd: str
                        User's password
    :param hashed_pwd: str
                        User's hashed password
    :return: Boolean
    """
    return pwd_cxt.verify(plain_pwd, hashed_pwd)




def generate_password(length):
    '''
    generates random password
    :param length:
    :return:
    '''
    # Define the possible characters to include in the password
    characters = string.ascii_letters +string.digits

    # Generate a password by randomly selecting characters from the defined set
    password = ''.join(random.choice(characters) for i in range(length))
    return password