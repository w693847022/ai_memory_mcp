"""自定义中间件 - 请求追踪和日志增强."""

import time
import uuid
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestTrackerMiddleware(BaseHTTPMiddleware):
    """请求追踪中间件 - 为每个请求添加追踪 ID 并记录处理时间."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求 ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录开始时间
        start_time = time.time()

        # 记录请求开始
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"client={request.client.host if request.client else 'unknown'}"
        )

        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        process_time = (time.time() - start_time) * 1000  # 毫秒

        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        # 记录请求完成
        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            log_level,
            f"[{request_id}] {request.method} {request.url.path} "
            f"status={response.status_code} time={process_time:.2f}ms"
        )

        return response
