from flask import Blueprint, request

from src.common.verify_token import if_authorized, token_required
from src.services.comments_service import add_comment


blp_comments = Blueprint('comments', __name__)


'''
payload: {
    question_id: str
    comment: str
}
'''
@blp_comments.route("/addComment", methods=["POST"])
@token_required
def add_comment_handler(token_data):
    payload = request.get_json()
    comment = payload.get('comment', None)
    question_id=payload.get('question_id', None)
    if not all([comment, question_id]):
        return {"message": "Missing parameters"}, 400
    return  add_comment(token_data, payload)
