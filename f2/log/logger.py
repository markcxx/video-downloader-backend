# path: f2/log/logger.py

import time
import logging
import datetime

from pathlib import Path
from rich.logging import RichHandler
from logging.handlers import TimedRotatingFileHandler

from f2.utils._singleton import Singleton


class LogManager(metaclass=Singleton):
    """
    日志管理器 (Log Manager)

    该类提供了一个全局日志管理器，使用单例模式，支持将日志输出到控制台和文件。

    文件日志会根据时间进行切割，每天生成一个新的日志文件，并保留一定数量的日志文件。

    还支持日志目录的管理和日志文件的清理功能。

    类属性:
    - logger (logging.Logger): 日志记录器实例，用于记录日志信息。
    - log_dir (Path | None): 日志文件存储路径。如果未设置，默认为 None。
    - _initialized (bool): 用于防止重复初始化。

    类方法:
    - __init__: 初始化日志管理器，并创建日志记录器实例。采用单例模式，确保只初始化一次。
    - setup_logging: 设置日志记录器的配置，包括日志级别、是否输出到控制台、日志文件路径等。
    - ensure_log_dir_exists: 确保日志目录存在。如果不存在，会自动创建。
    - clean_logs: 清理旧的日志文件，保留最新的n个日志文件。
    - shutdown: 关闭日志记录器并清理相关资源。

    异常处理:
    - 在清理日志文件时，如果日志文件正在被其他进程使用，将会捕获 `PermissionError` 异常，并记录警告信息。

    使用示例:
    ```python
        # 设置日志配置，并开始记录日志
        log_manager = LogManager()
        log_manager.setup_logging(log_to_console=True, log_path="./logs")

        # 清理过期日志，保留最新的10个日志文件
        log_manager.clean_logs(keep_last_n=10)

        # 使用日志记录器
        logger = logging.getLogger("f2")
        logger.info("This is an info message.")
    ```

    备注:
    - `setup_logging` 方法允许将日志输出到控制台和文件，并支持定期切割日志文件。
    - `clean_logs` 方法用于删除过期的日志文件，确保不会占用过多的磁盘空间。
    - 使用 `Singleton` 元类确保整个应用程序只有一个 `LogManager` 实例。
    """

    def __init__(self):
        if getattr(self, "_initialized", False):  # 防止重复初始化
            return

        self.logger = logging.getLogger("f2")
        self.logger.setLevel(logging.CRITICAL + 1)  # 默认禁用所有日志
        self.log_dir = None
        self._initialized = True

    def setup_logging(self, level=logging.INFO, log_to_console=False, log_path=None):
        # 禁用所有日志输出
        self.logger.handlers.clear()
        self.logger.setLevel(logging.CRITICAL + 1)  # 设置为比CRITICAL更高的级别，禁用所有日志
        
        # 不添加任何handler，确保没有日志输出到控制台或文件
        # 原有的控制台和文件日志功能已被禁用

    @staticmethod
    def ensure_log_dir_exists(log_path: Path):
        log_path.mkdir(parents=True, exist_ok=True)

    def clean_logs(self, keep_last_n=10):
        """保留最近的n个日志文件并删除其他文件"""
        if not self.log_dir:
            return
        # self.shutdown()
        all_logs = sorted(self.log_dir.glob("*.log"))
        if keep_last_n == 0:
            files_to_delete = all_logs
        else:
            files_to_delete = all_logs[:-keep_last_n]
        for log_file in files_to_delete:
            try:
                log_file.unlink()
            except PermissionError:
                self.logger.warning(
                    f"无法删除日志文件 {log_file}, 它正被另一个进程使用"
                )

    def shutdown(self):
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)
        self.logger.handlers.clear()
        time.sleep(1)  # 确保文件被释放


def log_setup(log_to_console=True):
    logger = logging.getLogger("f2")
    if logger.hasHandlers():
        # logger已经被设置，不做任何操作
        return logger

    # 禁用日志功能 - 不创建日志目录，不设置任何日志输出
    # 初始化日志管理器但禁用所有日志功能
    log_manager = LogManager()
    log_manager.setup_logging(
        level=logging.CRITICAL + 1, log_to_console=False, log_path=None
    )

    return logger


logger = log_setup()
