from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from authentication.models import CustomUser
from rest_framework.pagination import PageNumberPagination

def get_tokens_for_user(user: CustomUser):
    token = RefreshToken.for_user(user)
    token["full_name"] = user.full_name
    token["email"] = user.email
    token["mobile"] = user.mobile
    return {
        'refresh': str(token),
        'access': str(token.access_token),
        'expiry_time': (token.access_token['exp'] * 1000)
    }

def datetime_fmt(datetime_obj=None) -> str:
    return datetime.strftime(datetime_obj, "%d %b %y %I:%M %p")
    
def handle_exception(exception: Exception):
    message = "Some Exception was thrown."
    if len(exception.args):
        message = exception.args[0]
    return message

def handle_pagination(paginator: PageNumberPagination):
    return_dict = {
        "page": 1,
        "next_page": 0,
        "prev_page": 0,
    }
    return_dict['page'] = paginator.page.number
    return_dict['next_page'] = True if paginator.get_next_link() else False
    return_dict['prev_page'] = True if paginator.get_previous_link() else False
    return return_dict

def copy_with_specific_properties(source_dict, properties):
    return {key: source_dict[key] for key in properties if key in source_dict}
