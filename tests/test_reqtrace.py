"""
Tests untuk reqtrace v0.1.0
Jalankan dengan: pytest tests/ -v
"""

import pytest
from reqtrace import ReqTrace
from reqtrace.config import ReqTraceConfig
from reqtrace.formatter import format_log


# ---------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------


class TestReqTraceConfig:

    def test_default_output_is_terminal(self):
        cfg = ReqTraceConfig()
        assert cfg.output == "terminal"
        assert cfg.use_terminal is True
        assert cfg.use_file is False

    def test_file_output_requires_file_path(self):
        with pytest.raises(ValueError, match="file_path"):
            ReqTraceConfig(output="file")

    def test_both_output_requires_file_path(self):
        with pytest.raises(ValueError, match="file_path"):
            ReqTraceConfig(output="both")

    def test_valid_file_config(self):
        cfg = ReqTraceConfig(output="file", file_path="logs/trace.json")
        assert cfg.use_file is True
        assert cfg.use_terminal is False

    def test_valid_both_config(self):
        cfg = ReqTraceConfig(output="both", file_path="logs/trace.json")
        assert cfg.use_file is True
        assert cfg.use_terminal is True

    def test_invalid_output_mode(self):
        with pytest.raises(ValueError, match="Invalid output mode"):
            ReqTraceConfig(output="stdout")  # type: ignore

    def test_invalid_file_format(self):
        with pytest.raises(ValueError, match="Invalid file_format"):
            ReqTraceConfig(output="file", file_path="log.xml", file_format="xml")  # type: ignore

    def test_enabled_defaults_to_true(self):
        cfg = ReqTraceConfig()
        assert cfg.enabled is True

    def test_disabled_config(self):
        cfg = ReqTraceConfig(enabled=False)
        assert cfg.enabled is False


class TestReqTrace:

    def test_reqtrace_creates_config(self):
        rt = ReqTrace(output="terminal")
        assert isinstance(rt.config, ReqTraceConfig)

    def test_reqtrace_file_mode(self):
        rt = ReqTrace(output="file", file_path="logs/test.json")
        assert rt.config.use_file is True
        assert rt.config.file_path == "logs/test.json"

    def test_reqtrace_both_mode(self):
        rt = ReqTrace(output="both", file_path="logs/test.txt", file_format="txt")
        assert rt.config.use_terminal is True
        assert rt.config.use_file is True
        assert rt.config.file_format == "txt"


# ---------------------------------------------------------------
# Formatter tests
# ---------------------------------------------------------------


class TestFormatter:

    def test_format_log_returns_string(self):
        result = format_log(
            method="GET",
            url="/users",
            status_code=200,
            latency_ms=12.5,
        )
        assert isinstance(result, str)
        assert "GET" in result
        assert "/users" in result
        assert "200" in result

    def test_format_log_with_body(self):
        result = format_log(
            method="POST",
            url="/users",
            status_code=201,
            latency_ms=35.0,
            request_body={"name": "Diz", "email": "diz@mail.com"},
            response_body={"id": 3, "name": "Diz"},
        )
        assert "POST" in result
        assert "201" in result
        assert "Diz" in result

    def test_format_log_500_present(self):
        result = format_log(
            method="GET",
            url="/crash",
            status_code=500,
            latency_ms=5.0,
        )
        assert "500" in result
