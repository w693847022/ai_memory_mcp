"""HTTP 客户端连接池配置.

通过环境变量配置连接池参数，支持 HTTP/2 可选启用。
"""

import os
from dataclasses import dataclass
import httpx


@dataclass
class ConnectionPoolConfig:
    """HTTP 客户端连接池配置.

    通过环境变量配置连接池参数，支持 HTTP/2 可选启用。

    Attributes:
        max_connections: 最大连接数
        max_keepalive_connections: 最大保持连接数
        keepalive_expiry: 保持连接过期时间（秒）
        http2: 是否启用 HTTP/2
        timeout: 请求超时时间（秒）
    """
    max_connections: int
    max_keepalive_connections: int
    keepalive_expiry: float
    http2: bool
    timeout: float

    @classmethod
    def from_env(cls, timeout: float = 30.0) -> "ConnectionPoolConfig":
        """从环境变量加载配置.

        Args:
            timeout: 请求超时时间（秒），默认 30.0

        Returns:
            ConnectionPoolConfig 配置对象
        """
        return cls(
            max_connections=int(os.environ.get(
                "BUSINESS_API_MAX_CONNECTIONS", "100"
            )),
            max_keepalive_connections=int(os.environ.get(
                "BUSINESS_API_MAX_KEEPALIVE_CONNECTIONS", "20"
            )),
            keepalive_expiry=float(os.environ.get(
                "BUSINESS_API_KEEPALIVE_EXPIRY", "5.0"
            )),
            http2=os.environ.get("BUSINESS_API_HTTP2", "false").lower() in ("true", "yes", "1"),
            timeout=timeout,
        )

    def to_limits(self) -> httpx.Limits:
        """转换为 httpx.Limits 对象.

        Returns:
            httpx.Limits 对象
        """
        return httpx.Limits(
            max_connections=self.max_connections,
            max_keepalive_connections=self.max_keepalive_connections,
            keepalive_expiry=self.keepalive_expiry,
        )
