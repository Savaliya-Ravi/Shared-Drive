from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from API.Router.V1 import my_drives, folder, upload_item, sharing, copy_item, delete_item, file_content, \
    move_item, group, rename_item, modify_share, favourites
from Middleware.request_middleware import RequestContextMiddleware
from Utils.V1.config_reader import configure


def app():
    app = FastAPI(title="Drive Sharing API")

    app.add_middleware(SessionMiddleware, secret_key=configure.get("AUTHENTICATION", "MIDDLEWARE_KEY"))
    app.add_middleware(CorrelationIdMiddleware, header_name='X-Correlation-ID')
    app.add_middleware(RequestContextMiddleware)

    app.include_router(my_drives.router, prefix="/v1", tags=["My Drive"])
    app.include_router(folder.router, prefix="/v1", tags=["Folder"])
    app.include_router(upload_item.router, prefix="/v1", tags=["Folder"])
    app.include_router(sharing.router, prefix="/v1", tags=["Share"])
    app.include_router(file_content.router, prefix="/v1", tags=["File Data"])
    app.include_router(copy_item.router, prefix="/v1", tags=["Action"])
    app.include_router(delete_item.router, prefix="/v1", tags=["Action"])
    app.include_router(move_item.router, prefix="/v1", tags=["Action"])
    app.include_router(group.router, prefix="/v1", tags=["Group"])
    app.include_router(rename_item.router, prefix="/v1", tags=["Action"])
    app.include_router(modify_share.router, prefix="/v1", tags=["Action"])
    app.include_router(favourites.router, prefix="/v1", tags=["Favourite"])

    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    return app
