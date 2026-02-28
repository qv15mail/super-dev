"""
开发:Excellent(11964948@qq.com)
功能:自定义异常类
作用:提供结构化的异常处理体系
创建时间:2025-01-29
最后修改:2025-01-29
"""

from typing import Any


class SuperDevError(Exception):
    """Super Dev 基础异常类"""

    def __init__(
        self, message: str, code: str | None = None, details: dict[str, Any] | None = None
    ):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"[{self.code}] {self.message} - {self.details}"
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {"error": self.code, "message": self.message, "details": self.details}


# === 工作流异常 ===


class WorkflowError(SuperDevError):
    """工作流执行异常"""

    pass


class PhaseExecutionError(WorkflowError):
    """阶段执行异常"""

    def __init__(self, phase: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, "PHASE_EXECUTION_ERROR", details)
        self.phase = phase


class QualityGateError(WorkflowError):
    """质量门禁检查失败"""

    def __init__(self, score: float, threshold: float, details: dict[str, Any] | None = None):
        message = f"质量分数 {score:.1f} 低于阈值 {threshold:.1f}"
        super().__init__(message, "QUALITY_GATE_ERROR", details)
        self.score = score
        self.threshold = threshold


# === 配置异常 ===


class ConfigurationError(SuperDevError):
    """配置异常"""

    pass


class ValidationError(SuperDevError):
    """验证异常"""

    def __init__(self, field: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field


# === 外部服务异常 ===


class ExternalServiceError(SuperDevError):
    """外部服务调用异常"""

    def __init__(
        self,
        service: str,
        message: str,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)
        self.service = service
        self.status_code = status_code


class OpenAIError(ExternalServiceError):
    """OpenAI API调用异常"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__("openai", message, None, details)


# === 文件系统异常 ===


class FileSystemError(SuperDevError):
    """文件系统操作异常"""

    def __init__(self, path: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, "FILESYSTEM_ERROR", details)
        self.path = path


# === 输入输出异常 ===


class IOError(SuperDevError):
    """输入输出异常"""

    pass
