"""Unit tests for the unified error handler."""

import json

import pytest

from super_dev.error_handler import EXIT_ERROR, EXIT_INTERRUPTED, EXIT_USAGE, handle_cli_error
from super_dev.exceptions import ConfigurationError, SuperDevError
from super_dev.i18n import get_locale, set_locale


class TestHandleCliError:
    """Tests for handle_cli_error."""

    def test_keyboard_interrupt_returns_130(self):
        code = handle_cli_error(KeyboardInterrupt(), command="test")
        assert code == EXIT_INTERRUPTED

    def test_super_dev_error_returns_1(self):
        err = SuperDevError("测试错误", code="TEST")
        code = handle_cli_error(err, command="test")
        assert code == EXIT_ERROR

    def test_super_dev_error_with_details(self):
        err = ConfigurationError("配置缺失", details={"key": "name"})
        code = handle_cli_error(err, command="config")
        assert code == EXIT_ERROR

    def test_file_not_found_returns_1(self):
        err = FileNotFoundError(2, "No such file", "/tmp/missing.yaml")
        code = handle_cli_error(err, command="init")
        assert code == EXIT_ERROR

    def test_permission_error_returns_1(self):
        err = PermissionError(13, "Permission denied", "/etc/passwd")
        code = handle_cli_error(err, command="init")
        assert code == EXIT_ERROR

    def test_json_decode_error_returns_1(self):
        err = json.JSONDecodeError("Expecting value", "doc", 0)
        code = handle_cli_error(err, command="config")
        assert code == EXIT_ERROR

    def test_connection_error_returns_1(self):
        err = ConnectionError("Connection refused")
        code = handle_cli_error(err, command="update")
        assert code == EXIT_ERROR

    def test_timeout_error_returns_1(self):
        err = TimeoutError("timed out")
        code = handle_cli_error(err, command="update")
        assert code == EXIT_ERROR

    def test_value_error_returns_usage_code(self):
        err = ValueError("invalid argument")
        code = handle_cli_error(err, command="init")
        assert code == EXIT_USAGE

    def test_type_error_returns_usage_code(self):
        err = TypeError("wrong type")
        code = handle_cli_error(err, command="init")
        assert code == EXIT_USAGE

    def test_generic_exception_returns_1(self):
        err = RuntimeError("something went wrong")
        code = handle_cli_error(err, command="workflow")
        assert code == EXIT_ERROR

    def test_is_a_directory_error(self):
        err = IsADirectoryError(21, "Is a directory", "/tmp")
        code = handle_cli_error(err, command="config")
        assert code == EXIT_ERROR

    def test_yaml_error_returns_1(self):
        try:
            import yaml

            err = yaml.YAMLError("bad yaml")
            code = handle_cli_error(err, command="config")
            assert code == EXIT_ERROR
        except ImportError:
            pytest.skip("pyyaml not installed")


class TestErrorHandlerI18n:
    """Verify error_handler uses i18n for user-facing messages."""

    def setup_method(self):
        self._original = get_locale()

    def teardown_method(self):
        set_locale(self._original)

    def test_chinese_error_messages_by_default(self, capsys):
        set_locale("zh")
        handle_cli_error(FileNotFoundError(2, "No such file", "/tmp/test.txt"))
        output = capsys.readouterr().out
        assert "文件不存在" in output

    def test_english_error_messages_when_locale_is_en(self, capsys):
        set_locale("en")
        handle_cli_error(FileNotFoundError(2, "No such file", "/tmp/test.txt"))
        output = capsys.readouterr().out
        assert "File not found" in output

    def test_english_network_failure(self, capsys):
        set_locale("en")
        handle_cli_error(ConnectionError("refused"))
        output = capsys.readouterr().out
        assert "Network connection failed" in output

    def test_english_timeout(self, capsys):
        set_locale("en")
        handle_cli_error(TimeoutError("timed out"))
        output = capsys.readouterr().out
        assert "Operation timed out" in output

    def test_chinese_cancelled(self, capsys):
        set_locale("zh")
        handle_cli_error(KeyboardInterrupt())
        output = capsys.readouterr().out
        assert "已取消" in output

    def test_english_cancelled(self, capsys):
        set_locale("en")
        handle_cli_error(KeyboardInterrupt())
        output = capsys.readouterr().out
        assert "Cancelled" in output
