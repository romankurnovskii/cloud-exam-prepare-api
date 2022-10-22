import json
import os
import requests
import time

from jose import jwk, jwt
from jose.utils import base64url_decode
from flask import request
from functools import wraps

from src.db.mongo import db_aws_questions
from src.services.users_service import get_user_info

users_db = db_aws_questions.users


COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
COGNITO_POOL_DOMAIN = os.environ.get("COGNITO_POOL_DOMAIN")
COGNITO_REDIRECT_URI = os.environ.get("COGNITO_REDIRECT_URI")
COGNITO_REGION = os.environ.get("COGNITO_REGION")
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")

SERVER_URL = "https://cognito-idp." + COGNITO_REGION + ".amazonaws.com"

COGNITO_KEYS_URL = "/".join([SERVER_URL,
                            COGNITO_USER_POOL_ID, ".well-known/jwks.json"])

COGNITO_ACCESS_TOKEN_NAME = "CognitoAccessToken"
COGNITO_ID_TOKEN_NAME = "CognitoIdToken"
COGNITO_REFRESH_TOKEN_NAME = "CognitoRefreshToken"


# TODO lru cache
def get_cognito_keys():
    res = requests.get(COGNITO_KEYS_URL)
    keys = json.loads(res.text)["keys"]
    return keys


def verify_token(token):
    is_valid = False
    data = {}
    verify_data = {"is_valid": is_valid, "data": data}
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers["kid"]
    # search for the kid in the downloaded public keys
    key_index = -1
    keys = get_cognito_keys()
    for i in range(len(keys)):
        if kid == keys[i]["kid"]:
            key_index = i
            break
    if key_index == -1:
        print("Public key not found in jwks.json")
        return verify_data

    # construct the public key
    public_key = jwk.construct(keys[key_index])

    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit(".", 1)

    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print("Signature verification failed")
        return verify_data
    print("Signature successfully verified")

    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)

    # additionally we can verify the token expiration
    if time.time() > claims["exp"]:
        print("Token is expired")
        return verify_data
    # and the Audience  (use claims['client_id'] if verifying an access token)
    # this is from id_token
    try:
        if claims["aud"] != COGNITO_CLIENT_ID:
            print("Token was not issued for this audience")
            return verify_data
    except Exception as ex:
        print(ex)

    # now we can use the claims
    print("Updating verify data response")
    verify_data["is_valid"] = True
    verify_data["data"] = claims
    return verify_data


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = request.get_json()
        token = payload.get("visitorInfo", None)  # jwt token

        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized",
            }, 401
        try:
            verify_data = verify_token(token)
            user = get_user_info(verify_data)
            # user_sub = verify_data["data"].get("sub")
            # user = users_db.find_one({"sub": user_sub})
            if not user:
                return {
                    "message": "User not found",
                    "data": None,
                    "error": "User not found",
                }, 401

            verify_data["data"].update(user)
        except Exception as exc:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(exc),
            }, 500
        verify_data["payload"] = payload
        return f(verify_data, *args, **kwargs)

    return decorated


def if_authorized(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = request.get_json() or {}
        token = payload.get("visitorInfo", None)  # jwt token
        verify_data = {}
        if token:
            try:
                verify_data = verify_token(token)
            except Exception as exc:
                return {
                    "message": "Something went wrong",
                    "data": None,
                    "error": str(exc),
                }, 500
        verify_data["payload"] = payload
        return f(verify_data, *args, **kwargs)

    return decorated
