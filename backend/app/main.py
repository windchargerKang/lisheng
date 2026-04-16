"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import api_router


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
    )

    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
