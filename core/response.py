from rest_framework.response import Response

class Response(Response):
    def __init__(self, data=None, status=None, template_name=None, headers=None, exception=False, content_type=None):
        super().__init__(data, status, template_name, headers, exception, content_type)
        # print(data, status, template_name, headers, exception, content_type)
        # print("response data", data)
        data["settings"] = {
            "success": data['success'] if data['success'] else 0,
            "message": data['message'] if data['message'] else None,
            "status": 200
        }
        if "count" in data:
            data["settings"]["count"] = data["count"]
            del data["count"]
        if "page" in data:
            data["settings"]["page"] = data["page"]
            del data["page"]
        if "next_page" in data:
            data["settings"]["next_page"] = data["next_page"]
            del data["next_page"]
        if "prev_page" in data:
            data["settings"]["prev_page"] = data["prev_page"]
            del data["prev_page"]
        if "per_page" in data:
            data["settings"]["per_page"] = data["per_page"]
            del data["per_page"]
        del data['message']
        del data['success']
        # return data