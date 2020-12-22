import logging
import os

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.database_connections import databases
from app.json_web_token import JsonWebToken, JsonWebTokenException
from app.routers.apis import api_router

api_prefix: str = os.getenv("API_PREFIX")
swagger_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png"
templates: Jinja2Templates = Jinja2Templates(directory="/app/templates")

app: FastAPI = FastAPI(
    title="Demo App",
    description="<p>All web services except the web services in the authorization section "
                "require an Authorization header in each request.</p>"
                "<p><font color=green>"
                "An Authorization header is a token type plus a space and an access token."
                "</font></p>"
                "<p>An access token can be acquired from the web services in the authorization section below.</p>"
                "<hr><br>"
                "These are abbreviations in this documentation."
                "<ol>"
                "<li><b>SPA</b> stands for 'Single Page Application'.</li>"
                "</ol>"
                f"<br>See also the <a href='{api_prefix}/error-codes' target='_blank'>error codes reference</a>.",
    version=os.getenv("API_VERSION"),
    docs_url=None,
    redoc_url=None,
    openapi_url=api_prefix + "/openapi.json",
)

app.mount("/static", StaticFiles(directory="/app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGIN"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def __display_error(exception: Exception, error_code: int) -> None:
    """Display and log an error.

    :param exception: Exception
    :param error_code: Error code
    """
    logging.error(f"[{error_code}] {exception.__str__()}")

    app.description = "### <font color=red>Internal Server Error: Please help to contact the system administrator " \
                      f"with error code {error_code}.</font> "


@app.get(api_prefix, include_in_schema=False)
async def get_custom_swagger_ui_html() -> HTMLResponse:
    """Get a custom Swagger UI HTML.

    :return: Custom Swagger UI HTML
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_css_url="/static/swagger-ui.min.css",
        swagger_favicon_url=swagger_favicon_url
    )


@app.get(
    api_prefix + "/error-codes",
    include_in_schema=False,
    response_class=HTMLResponse
)
async def get_error_codes_template(request: Request):
    """Get the error codes template.

    :param request: HTTP request
    :return: Error codes template
    """
    return templates.TemplateResponse(
        "error_codes.html",
        {"request": request, "title": app.title, "version": app.version, "icon": swagger_favicon_url}
    )


@app.on_event("startup")
async def start_up() -> None:
    """Execute this function before this application starts up.
    """
    try:
        await databases.connect()
        await JsonWebToken.set_up()
        app.include_router(api_router, prefix=api_prefix)
    except ConnectionError as mongodb_connections_error:
        await __display_error(mongodb_connections_error, 10001)
    except JsonWebTokenException as json_web_token_error:
        await __display_error(json_web_token_error, 10002)


@app.on_event("shutdown")
async def shut_down() -> None:
    """Execute this function before this application is shutting down.
    """
    await databases.disconnect()
