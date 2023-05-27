from src.services.users_service import get_user_info


def is_valid_request(payload):
    pass


def is_view_exam_alowed(token_data, exam_code):
    user = get_user_info(token_data)
    subscriptions = user.get("subscriptions")
    if subscriptions:
        if exam_code in subscriptions or "ALL" in subscriptions:
            return True
    return False
