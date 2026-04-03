from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None: return None
    code_map = {400: "bad_request", 401: "unauthorized", 403: "forbidden",
                404: "not_found", 409: "conflict"}
    response.data = {"success": False,
                     "error": {"code": code_map.get(response.status_code, "error"),
                               "message": _msg(response.data), "details": response.data}}
    return response

def _msg(data):
    if isinstance(data, dict):
        for k in ["detail", "non_field_errors"]:
            if k in data:
                v = data[k]
                return str(v[0]) if isinstance(v, list) else str(v)
        first = next(iter(data.values()), None)
        return str(first[0]) if isinstance(first, list) else str(first or "")
    return str(data[0]) if isinstance(data, list) and data else str(data)