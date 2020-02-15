"""OpenAPI checking before and after requests."""
from json import dumps

from openapi_core.schema.operations.exceptions import InvalidOperation
from openapi_core.schema.parameters.exceptions import \
    OpenAPIParameterError, MissingParameter, MissingRequiredParameter, \
    EmptyParameterValue, InvalidParameterValue
from openapi_core.schema.servers.exceptions import InvalidServer
from openapi_core.schema.paths.exceptions import InvalidPath

from poorwsgi.response import Response, abort
from poorwsgi.openapi_wrapper import OpenAPIRequest, OpenAPIResponse

from . core import app
from . config import LOGGER as log

ERRORS = {
    OpenAPIParameterError: "BAD_PARAMETER",
    MissingParameter: "MISSING_PARAMETER",
    MissingRequiredParameter: "MISSING_PARAMETER",
    EmptyParameterValue: "EMPTY_PARAMETER",
    InvalidParameterValue: "INVALID_PARAMETER"
}


def error_to_struct(error):
    """Return error struct from api error."""
    return {
        "code": ERRORS.get(type(error), "NOT_SPECIFIED"),
        "reason": str(error),
        "args": str(error.args)
    }


def before_request(req):
    """Check every input requests except / and openapi.yaml."""
    if req.uri in ('/') or req.uri.endswith(".yaml"):
        return          # do not check doc and definition url
    req.api = OpenAPIRequest(req)
    result = app.cfg.request_validator.validate(req.api)
    if result.errors:
        errors = []
        for error in result.errors:
            log.debug(error)
            if isinstance(error, (InvalidOperation, InvalidServer,
                                  InvalidPath)):
                return  # not found
            errors.append(error_to_struct(error))
        abort(Response(dumps({"errors": errors}), status_code=400,
                       content_type="application/json"))


def after_request(req, res):
    """Check every answer except of / and openapi.yaml."""
    if req.uri in ('/') or req.uri.endswith(".yaml"):
        return res  # do not check doc and definition url
    result = app.cfg.response_validator.validate(
        req.api or OpenAPIRequest(req),     # on error in any before_request
        OpenAPIResponse(res))
    for error in result.errors:
        if isinstance(error, InvalidOperation):
            continue
        log.error("API output error: %s", str(error))
    return res


app.add_before_request(before_request)
if app.cfg.validate_response:
    app.add_after_request(after_request)
