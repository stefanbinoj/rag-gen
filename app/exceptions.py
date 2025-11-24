class NotFoundError(Exception):
    pass

def register_exception_handlers(app):
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=404)
