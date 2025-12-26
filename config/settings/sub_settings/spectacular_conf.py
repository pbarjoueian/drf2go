from ..env import env

SPECTACULAR_SETTINGS = {
    "TITLE": env("SPECTACULAR_TITLE", default="Backend API"),
    "DESCRIPTION": env("SPECTACULAR_DESCRIPTION", default="Backend API"),
    "VERSION": env("SPECTACULAR_VERSION", default="1.0.0"),
    "SERVE_INCLUDE_SCHEMA": env.bool("SPECTACULAR_SERVE_INCLUDE_SCHEMA", default=False),
    "SCHEMA_PATH_PREFIX": "/api/schema/",
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "url": "/api/schema/",
        "syntaxHighlight.theme": "monokai",
        "layout": "BaseLayout",
        "docExpansion": "none",
        "defaultModelsExpandDepth": 3,
        "defaultModelExpandDepth": 3,
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
    },
    "SERVE_PUBLIC": True,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": None,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_DIST": "https://unpkg.com/swagger-ui-dist@5.11.0",
    "SWAGGER_UI_FAVICON_HREF": (
        "https://unpkg.com/swagger-ui-dist@5.11.0/favicon-32x32.png"
    ),
}

