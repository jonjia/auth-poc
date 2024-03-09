from flask import Flask, request
import json
from authzed.api.v1 import (
  Client,
  CheckPermissionRequest,
  CheckPermissionResponse,
  ObjectReference,
  SubjectReference,
  LookupResourcesRequest
)
from grpcutil import insecure_bearer_token_credentials
from pprint import pprint

app = Flask(__name__)

client = Client(
    "localhost:50051",
    insecure_bearer_token_credentials("freshbeef"),
)

@app.route("/")
def index() -> str:
    return "<html><body><pre>AuthZed POC</pre></body></html>"

@app.route("/api/permission/<object_type>/<perm>", methods=["GET"])
async def get_content_permission(object_type: str, perm: str) -> str:
    user_id = request.headers.get("X-User-Id")
    req = LookupResourcesRequest(
        subject=SubjectReference(object=ObjectReference(object_id=user_id, object_type="user")),
        permission=perm,
        resource_object_type=object_type,
    )
    ret = []

    for item in client.LookupResources(req):
        ret.append(item.resource.object_id)
    return json.dumps({ "type": object_type, "permission": perm, "resources": ret })

@app.route("/api/content/<id>", methods=["GET"])
def get_content(id: int) -> str:
    return json.dumps({ "id": id, "content": "This is the content" })

@app.route("/api/content/<id>", methods=["POST"])
def update_content(id: int) -> str:
    return json.dumps({ "id": id, "content": "This is the updated content" })

@app.before_request
def before_request():
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        return "Unauthorized", 401
    if request.path.startswith("/api/content"):
        if request.method == "GET":
            if not check_content_permission(user_id, "read", int(request.view_args["id"])):
                return "Forbidden", 403
        elif request.method == "POST":
            if not check_content_permission(user_id, "write", int(request.view_args["id"])):
                return "Forbidden", 403 

    return None

@app.after_request
def after_request(response):
    if request.path.startswith("/api"):
        response.headers["Content-Type"] = "application/json"

    return response

def check_content_permission(user_id: str, perm: str, content_id: int) -> bool:
    return check_permission(user_id, perm, "content", str(content_id))

def check_permission(user_id: str, perm: str, object_type: str, object_id: str) -> bool:
    req = CheckPermissionRequest(
        subject=SubjectReference(object=ObjectReference(object_id=user_id, object_type="user")),
        permission=perm,
        resource=ObjectReference(object_id=object_id, object_type=object_type),
    )
    resp = client.CheckPermission(req)
    return resp.permissionship == CheckPermissionResponse.PERMISSIONSHIP_HAS_PERMISSION
