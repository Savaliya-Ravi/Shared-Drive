from fastapi.responses import JSONResponse, FileResponse, Response
from Constant.http import HS_SUCCESS, HS_ERROR


def successResponse(statusCode, message, data={}):
    return JSONResponse(status_code=statusCode,
                        content={"status": HS_SUCCESS, "message": message, "data": data})


def errorResponse(statusCode, message, data={}):
    return JSONResponse(status_code=statusCode,
                        content={"status": HS_ERROR, "message": message, "data": data})


def fileResponse(statusCode, path, filename):
    return FileResponse(status_code=statusCode, path=path, filename=filename)
