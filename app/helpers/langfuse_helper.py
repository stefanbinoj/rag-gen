import os
from langfuse.client import Langfuse
from langfuse.callback import CallbackHandler

_langfuse_client = None
_langfuse_handler = None


def get_langfuse_client() -> Langfuse:
    global _langfuse_client
    if _langfuse_client is None:
        _langfuse_client = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST"),
        )
    return _langfuse_client


def get_langfuse_handler() -> CallbackHandler:
    global _langfuse_handler
    if _langfuse_handler is None:
        _langfuse_handler = CallbackHandler(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST"),
        )
    return _langfuse_handler


def create_langfuse_handler(
    metadata: dict | None = None,
    tags: list[str] | None = None,
) -> CallbackHandler:
    handler = CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
        metadata=metadata,
        tags=tags,
    )
    return handler
