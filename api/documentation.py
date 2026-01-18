"""
Complete API Documentation with OpenAPI/Swagger
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any

def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Generate custom OpenAPI documentation"""
    
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title="Roastify Pro API",
        version="2.0.0",
        description="""
        # 🚀 Roastify Pro - Complete API Documentation
        
        ## Overview
        Roastify Pro is an advanced Telegram bot system with comprehensive features.
        
        ## Features
        - 🤖 Advanced bot management
        - 🎨 Image generation with 3D effects
        - 👥 Group management
        - 📊 Real-time analytics
        - 🔒 Complete security system
        - 📱 Web dashboard
        
        ## Authentication
        Most endpoints require authentication via:
        - API Key header: `X-API-Key`
        - JWT Token: `Authorization: Bearer <token>`
        
        ## Rate Limiting
        - Default: 100 requests per minute per IP
        - Burst: 150 requests allowed
        - Headers returned:
          - `X-RateLimit-Limit`
          - `X-RateLimit-Remaining`
          - `X-RateLimit-Reset`
        
        ## Error Responses
        All errors return JSON with:
        ```json
        {
          "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "details": {}
          }
        }
        ```
        
        ## Status Codes
        - 200: Success
        - 400: Bad Request
        - 401: Unauthorized
        - 403: Forbidden
        - 404: Not Found
        - 429: Too Many Requests
        - 500: Internal Server Error
        
        ## Contact
        - Support: support@roastify.com
        - Website: https://roastify.com
        - Documentation: https://docs.roastify.com
        """,
        routes=app.routes,
    )
    
    # Customize OpenAPI schema
    openapi_schema["info"]["x-logo"] = {
        "url": "https://roastify.com/logo.png",
        "backgroundColor": "#1a1a2e",
        "altText": "Roastify Logo"
    }
    
    openapi_schema["servers"] = [
        {
            "url": "https://api.roastify.com/v1",
            "description": "Production server"
        },
        {
            "url": "https://staging.api.roastify.com/v1",
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8080/v1",
            "description": "Local development"
        }
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key for service-to-service communication"
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token for user authentication"
        }
    }
    
    # Default security
    openapi_schema["security"] = [
        {"ApiKeyAuth": []},
        {"BearerAuth": []}
    ]
    
    # Add tags
    openapi_schema["tags"] = [
        {
            "name": "authentication",
            "description": "Authentication and authorization endpoints"
        },
        {
            "name": "users",
            "description": "User management and operations"
        },
        {
            "name": "groups",
            "description": "Group chat management"
        },
        {
            "name": "roasts",
            "description": "Roast generation and management"
        },
        {
            "name": "images",
            "description": "Image generation and processing"
        },
        {
            "name": "analytics",
            "description": "Statistics and analytics"
        },
        {
            "name": "admin",
            "description": "Administrative functions"
        },
        {
            "name": "system",
            "description": "System health and monitoring"
        }
    ]
    
    # Add examples
    openapi_schema["components"]["schemas"] = {
        **openapi_schema.get("components", {}).get("schemas", {}),
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "VALIDATION_ERROR"},
                        "message": {"type": "string", "example": "Invalid input provided"},
                        "details": {"type": "object", "example": {"field": "email"}}
                    }
                }
            }
        },
        "SuccessResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": True},
                "message": {"type": "string", "example": "Operation completed successfully"},
                "data": {"type": "object"}
            }
        },
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 123456789},
                "username": {"type": "string", "example": "johndoe"},
                "first_name": {"type": "string", "example": "John"},
                "last_name": {"type": "string", "example": "Doe"},
                "roast_count": {"type": "integer", "example": 42},
                "created_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"}
            }
        },
        "Roast": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "example": "roast_abc123"},
                "text": {"type": "string", "example": "Your roast text here"},
                "category": {"type": "string", "example": "funny"},
                "image_url": {"type": "string", "example": "https://cdn.roastify.com/images/abc123.png"},
                "votes": {
                    "type": "object",
                    "properties": {
                        "funny": {"type": "integer", "example": 15},
                        "mid": {"type": "integer", "example": 3},
                        "savage": {"type": "integer", "example": 8}
                    }
                },
                "created_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"}
            }
        }
    }
    
    # Customize paths
    for path in openapi_schema["paths"].values():
        for method in path.values():
            # Add common responses
            method["responses"].update({
                "400": {
                    "description": "Bad Request",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                },
                "401": {
                    "description": "Unauthorized",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                },
                "403": {
                    "description": "Forbidden",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                },
                "429": {
                    "description": "Too Many Requests",
                    "headers": {
                        "X-RateLimit-Limit": {
                            "schema": {"type": "integer", "example": 100}
                        },
                        "X-RateLimit-Remaining": {
                            "schema": {"type": "integer", "example": 75}
                        },
                        "X-RateLimit-Reset": {
                            "schema": {"type": "integer", "example": 1625097600}
                        }
                    },
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                },
                "500": {
                    "description": "Internal Server Error",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            })
            
    app.openapi_schema = openapi_schema
    return app.openapi_schema