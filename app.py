import responder
import os
import json
import requests

CLIENT_ID = os.environ["GH_BASIC_CLIENT_ID"]
CLIENT_SECRET = os.environ["GH_BASIC_SECRET_ID"]

api = responder.API()

@api.route("/")
async def index(req, resp):
    resp.html = api.template("index.html", client_id=CLIENT_ID)

@api.route("/callback")
async def callback(req, resp):
    # get temporary GitHub code...
    session_code = req.params["code"]

    # ... and POST it back to GitHub
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": session_code,
    }
    headers = { "accept": "application/json" }
    result = requests.post("https://github.com/login/oauth/access_token", data=data, headers=headers)

    # extract the token and granted scopes
    result_json = result.json()

    access_token = result_json["access_token"]
    scopes = result_json["scope"].split(",")

    has_user_email_scope = "user:email" in scopes

    # fetch user information
    params = { "access_token": access_token }
    auth_result = requests.get("https://api.github.com/user", params=params).json()

    # if the user authorized it, fetch private emails
    if has_user_email_scope:
        params = { "access_token": access_token }
        auth_result["private_emails"] = requests.get("https://api.github.com/user/emails", params=params).json()

        print(auth_result)
        resp.text = "Success"
    else:
        resp.text = "Failed"

if __name__ == "__main__":
    api.run()
