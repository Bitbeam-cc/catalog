"""OpenAPI checking before and after requests."""
from json import dumps

from openapi_core.deserializing.parameters.exceptions import \
    EmptyParameterValue
from openapi_core.schema.media_types.exceptions import InvalidContentType
from openapi_core.schema.operations.exceptions import InvalidOperation
from openapi_core.schema.parameters.exceptions import (
    MissingParameter, MissingRequiredParameter, OpenAPIParameterError)
from openapi_core.schema.paths.exceptions import InvalidPath
from openapi_core.templating.paths.exceptions import (OperationNotFound,
                                                      PathNotFound)
from openapi_core.validation.exceptions import InvalidSecurity

from poorwsgi.response import Response, abort
from poorwsgi.openapi_wrapper import OpenAPIRequest, OpenAPIResponse

from . core import app
from . config import LOGGER as log

ERRORS = {
    OpenAPIParameterError: "BAD_PARAMETER",
    MissingParameter: "MISSING_PARAMETER",
    MissingRequiredParameter: "MISSING_PARAMETER",
    EmptyParameterValue: "EMPTY_PARAMETER",
}

IGNORE_EXTENSIONS = (".yaml", ".png", ".js", ".css")

def error_to_struct(error):
    """Return error struct from api error."""
    return {
        "code": ERRORS.get(type(error), "NOT_SPECIFIED"),
        "reason": str(error),
        "args": str(error.args)
    }


def before_request(req):
    """Check every input requests except / and openapi.yaml."""
    if req.uri in ('/') or req.uri.endswith(IGNORE_EXTENSIONS):
        return          # do not check doc and definition url
    req.api = OpenAPIRequest(req)
    if req.content_length > app.data_size:
        return  # req.data not available for validator
    result = app.cfg.request_validator.validate(req.api)
    if result.errors:
        errors = []
        for error in result.errors:
            log.debug("[%s] -> %s", req.uri, error)
            if isinstance(error, (InvalidOperation, OperationNotFound,
                                  InvalidPath, PathNotFound)):
                return  # not found
            if isinstance(error, InvalidSecurity):
                abort(Response(dumps({"errors": errors}), status_code=401,
                               content_type="application/json"))

            errors.append(error_to_struct(error))
        abort(Response(dumps({"errors": errors}), status_code=400,
                       content_type="application/json"))


def after_request(req, res):
    """Check every answer except of / and openapi.yaml."""
    if req.uri in ('/') or req.uri.endswith(IGNORE_EXTENSIONS):
        return res  # do not check doc and definition url
    result = app.cfg.response_validator.validate(
        req.api or OpenAPIRequest(req),     # on error in any before_request
        OpenAPIResponse(res))
    for error in result.errors:
        if isinstance(error, InvalidOperation):
            continue
        if isinstance(error, InvalidContentType):
            # https://github.com/p1c2u/openapi-core/issues/304
            # openapi_core expects
            #  mimetype='application/json' but gets
            #  mimetype='application/json; charset=utf-8'
            continue
        log.error("API output error: %s", str(error))
    return res


app.add_before_request(before_request)
if app.cfg.validate_response:
    app.add_after_request(after_request)
