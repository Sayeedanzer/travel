from rest_framework.views import exception_handler

class SerializerError(Exception):
    
    def __init__(self, data):
        error_messages = []
        for field, error in data.items():
            error_message = str(error[0])
            error_messages.append(error_message)
        self.data = error_messages[0]
    
    def __str__(self):
        return self.data
    
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data["settings"] = {
            "success": 0,
            "message": "",
            "status": response.status_code if response.status_code else 200
        }
        response.data["settings"]["message"] = response.data["detail"]
        del response.data["detail"]
    return response