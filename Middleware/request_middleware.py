from contextvars import ContextVar

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

request_var = ContextVar("request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Set the request in the context variable
        token = request_var.set(request)
        response = await call_next(request)
        # Reset the context variable after the request is processed
        request_var.reset(token)
        return response
