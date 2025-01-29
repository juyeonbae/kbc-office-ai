from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from exceptions import ChatbotException


logger = logging.getLogger(__name__)

def create_response(message, details, http_status, data, type):
    return JSONResponse(content={
        "timeStamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "code": http_status,
        "message": message,
        "details": details,
        "data": data,
        "type": type
    }, status_code=http_status)

async def error_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except ChatbotException as e:
        return create_response(
            "GENERATED_FAILED",
            str(e),
            e.status_code,
            None,
            "error"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return create_response(
            "GENERATED_FAILED",
            "An unexpected error occurred",
            500,
            None,
            "error"
        )