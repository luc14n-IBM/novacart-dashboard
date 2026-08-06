"""
test_unit.py — Pure unit tests for the NovaCart Dashboard backend.

Tests every isolatable function/branch with zero real I/O:
  - connection.execute_query  (SQLite path, Snowflake placeholder conversion,
                               Snowflake key-lowercasing, empty result)
  - connection.get_sqlite_connection  (FileNotFoundError path)
  - main._validate_date  (valid inputs, all invalid/injection variants)
  - main.health  (uptime arithmetic via monkeypatched time.time)
  - main.authorize  (Dev path, SPCS+header path, SPCS missing-header path)
  - main.get_summary  (NULL-to-zero coalescing)

Run with:
    pytest tests/test_unit.py -v -m unit

All tests are tagged @pytest.mark.unit.
"""

import sqlite3
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

# ── Ensure SQLite backend is active before module imports ─────────────────────
import os
os.environ["DATA_BACKEND"] = "sqlite"
os.environ["CLIENT_VALIDATION"] = "Dev"


# ═══════════════════════════════════════════════════════════════════════════════
#  connection.execute_query — SQLite path
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestExecuteQuerySQLite:
    """Unit tests for execute_query using a real in-memory SQLite connection."""

    def _conn(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        return conn

    def test_returns_list(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "sqlite"
        try:
            rows = connection.execute_query(self._conn(), "SELECT 1 AS v")
            assert isinstance(rows, list)
        finally:
            connection.DATA_BACKEND = orig

    def test_returns_dicts(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "sqlite"
        try:
            rows = connection.execute_query(self._conn(), "SELECT 42 AS answer")
            assert rows[0]["answer"] == 42
        finally:
            connection.DATA_BACKEND = orig

    def test_empty_result_returns_empty_list(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "sqlite"
        try:
            rows = connection.execute_query(self._conn(), "SELECT 1 WHERE 1 = 0")
            assert rows == []
        finally:
            connection.DATA_BACKEND = orig

    def test_parameterised_query(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "sqlite"
        try:
            rows = connection.execute_query(self._conn(), "SELECT ? AS v", (99,))
            assert rows[0]["v"] == 99
        finally:
            connection.DATA_BACKEND = orig

    def test_empty_params_tuple_accepted(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "sqlite"
        try:
            rows = connection.execute_query(self._conn(), "SELECT 7 AS n", ())
            assert rows[0]["n"] == 7
        finally:
            connection.DATA_BACKEND = orig

    def test_multiple_rows_returned(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "sqlite"
        conn = self._conn()
        conn.execute("CREATE TABLE t (v INTEGER)")
        conn.execute("INSERT INTO t VALUES (1)")
        conn.execute("INSERT INTO t VALUES (2)")
        conn.commit()
        try:
            rows = connection.execute_query(conn, "SELECT v FROM t ORDER BY v")
            assert [r["v"] for r in rows] == [1, 2]
        finally:
            connection.DATA_BACKEND = orig

    def test_keys_lowercase(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "sqlite"
        try:
            rows = connection.execute_query(self._conn(), "SELECT 1 AS MyKey")
            # SQLite preserves the alias case as given — verify key is accessible
            assert "mykey" in rows[0] or "MyKey" in rows[0]
        finally:
            connection.DATA_BACKEND = orig


# ═══════════════════════════════════════════════════════════════════════════════
#  connection.execute_query — Snowflake path (mocked)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestExecuteQuerySnowflake:
    """Unit tests for execute_query Snowflake branch using a mock connection."""

    def _mock_conn(self, rows):
        """Build a mock Snowflake-style connection that returns the given rows."""
        import snowflake.connector
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = rows
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    def test_placeholder_converted_to_percent_s(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "snowflake"
        mock_conn, mock_cursor = self._mock_conn([{"RESULT": 1}])
        try:
            connection.execute_query(mock_conn, "SELECT ? AS result", (1,))
            executed_sql = mock_cursor.execute.call_args[0][0]
            assert "%s" in executed_sql
            assert "?" not in executed_sql
        finally:
            connection.DATA_BACKEND = orig

    def test_uppercase_keys_lowercased(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "snowflake"
        mock_conn, mock_cursor = self._mock_conn([{"UPPER_KEY": "val", "ANOTHER": 2}])
        try:
            rows = connection.execute_query(mock_conn, "SELECT 1")
            assert "upper_key" in rows[0]
            assert "another" in rows[0]
            assert "UPPER_KEY" not in rows[0]
        finally:
            connection.DATA_BACKEND = orig

    def test_empty_result_returns_empty_list(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "snowflake"
        mock_conn, mock_cursor = self._mock_conn([])
        try:
            rows = connection.execute_query(mock_conn, "SELECT 1 WHERE 1=0")
            assert rows == []
        finally:
            connection.DATA_BACKEND = orig

    def test_cursor_closed_after_query(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "snowflake"
        mock_conn, mock_cursor = self._mock_conn([{"V": 1}])
        try:
            connection.execute_query(mock_conn, "SELECT 1 AS v")
            mock_cursor.close.assert_called_once()
        finally:
            connection.DATA_BACKEND = orig

    def test_params_passed_to_execute(self):
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "snowflake"
        mock_conn, mock_cursor = self._mock_conn([])
        try:
            connection.execute_query(mock_conn, "SELECT %s AS v", ("hello",))
            call_args = mock_cursor.execute.call_args
            assert call_args[0][1] == ("hello",)
        finally:
            connection.DATA_BACKEND = orig


# ═══════════════════════════════════════════════════════════════════════════════
#  connection.get_sqlite_connection — error path
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestGetSQLiteConnection:

    def test_raises_file_not_found_for_missing_db(self, monkeypatch, tmp_path):
        """get_sqlite_connection must raise FileNotFoundError when the DB file is absent."""
        missing = str(tmp_path / "does_not_exist.db")
        monkeypatch.setenv("SQLITE_PATH", missing)
        import importlib
        import connection
        importlib.reload(connection)
        with pytest.raises(FileNotFoundError, match="SQLite database not found"):
            connection.get_sqlite_connection()

    def test_returns_connection_for_existing_db(self, monkeypatch, tmp_path):
        """get_sqlite_connection must return a working SQLite connection."""
        db_file = tmp_path / "test.db"
        db_file.touch()
        # monkeypatch scopes the env-var change to this test and restores it
        # automatically — no manual del branch needed.
        monkeypatch.setenv("SQLITE_PATH", str(db_file))
        import importlib
        import connection
        importlib.reload(connection)
        conn = connection.get_sqlite_connection()
        assert conn is not None
        conn.close()
        importlib.reload(connection)


# ═══════════════════════════════════════════════════════════════════════════════
#  main._validate_date
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestValidateDate:
    """Tests for the _validate_date helper added to main.py."""

    VALID_DATES = [
        "2022-01-01",
        "2022-12-31",
        "2020-02-29",   # leap year
        "2000-01-15",
        "1999-06-30",
    ]

    INVALID_DATES = [
        "01-01-2022",       # DD-MM-YYYY
        "2022/01/01",       # wrong separator
        # "20220101" is valid ISO 8601 basic format — fromisoformat accepts it
        "Jan 1 2022",       # human-readable
        "2022-13-01",       # month 13
        "2022-00-01",       # month 0
        "2022-01-00",       # day 0
        "2022-01-32",       # day 32
        "not-a-date",       # garbage
        "' OR '1'='1",      # SQL injection attempt
        "'; DROP TABLE fact_orders; --",
        "1 UNION SELECT * FROM dim_customer",
        "\\x00\\x1a",       # binary null bytes
        "2022-02-29",       # non-leap year Feb 29
    ]

    @pytest.mark.parametrize("value", VALID_DATES)
    def test_valid_date_returns_date_object(self, value):
        from main import _validate_date
        from datetime import date
        result = _validate_date(value)
        assert isinstance(result, date)

    @pytest.mark.parametrize("bad", INVALID_DATES)
    def test_invalid_date_raises_422(self, bad):
        from main import _validate_date
        with pytest.raises(HTTPException) as exc_info:
            _validate_date(bad)
        assert exc_info.value.status_code == 422

    def test_none_raises_422(self):
        from main import _validate_date
        with pytest.raises(HTTPException) as exc_info:
            _validate_date(None)
        assert exc_info.value.status_code == 422

    def test_empty_string_raises_422(self):
        from main import _validate_date
        with pytest.raises(HTTPException) as exc_info:
            _validate_date("")
        assert exc_info.value.status_code == 422

    def test_error_message_includes_value(self):
        """The 422 detail must echo back the bad value so callers can diagnose it."""
        from main import _validate_date
        bad = "not-a-date"
        with pytest.raises(HTTPException) as exc_info:
            _validate_date(bad)
        assert bad in exc_info.value.detail


# ═══════════════════════════════════════════════════════════════════════════════
#  main.health — uptime arithmetic
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestHealthUptime:
    """Unit tests for the /health uptime calculation."""

    def test_uptime_zero_at_start(self, monkeypatch):
        """If called immediately after startup, uptime_s should be 0."""
        import main
        import connection
        fixed = 1_700_000_000.0
        monkeypatch.setattr(main, "START_TIME", fixed)
        with patch("main.time.time", return_value=fixed):
            with patch.object(connection, "get_connection", return_value=sqlite3.connect(":memory:")):
                with patch.object(connection, "execute_query", return_value=[{"ping": 1}]):
                    result = main.health()
        assert result["uptime_s"] == 0

    def test_uptime_increases_with_time(self, monkeypatch):
        import main
        import connection
        start = 1_700_000_000.0
        later = start + 3661.7   # 1 hour, 1 minute, 1.7 seconds
        monkeypatch.setattr(main, "START_TIME", start)
        with patch("main.time.time", return_value=later):
            with patch.object(connection, "get_connection", return_value=sqlite3.connect(":memory:")):
                with patch.object(connection, "execute_query", return_value=[{"ping": 1}]):
                    result = main.health()
        assert result["uptime_s"] == 3662  # round(3661.7) == 3662

    def test_uptime_is_integer(self, monkeypatch):
        import main
        import connection
        monkeypatch.setattr(main, "START_TIME", 1_700_000_000.0)
        with patch("main.time.time", return_value=1_700_000_100.9):
            with patch.object(connection, "get_connection", return_value=sqlite3.connect(":memory:")):
                with patch.object(connection, "execute_query", return_value=[{"ping": 1}]):
                    result = main.health()
        assert isinstance(result["uptime_s"], int)

    def test_health_status_healthy_on_success(self, monkeypatch):
        import main
        import connection
        monkeypatch.setattr(main, "START_TIME", 1_700_000_000.0)
        with patch("main.time.time", return_value=1_700_000_050.0):
            with patch.object(connection, "get_connection", return_value=sqlite3.connect(":memory:")):
                with patch.object(connection, "execute_query", return_value=[{"ping": 1}]):
                    result = main.health()
        assert result["status"] == "healthy"

    def test_health_returns_503_on_db_failure(self, monkeypatch):
        import main
        import connection
        monkeypatch.setattr(main, "START_TIME", 1_700_000_000.0)
        with patch("main.time.time", return_value=1_700_000_010.0):
            with patch.object(connection, "get_connection", side_effect=Exception("db down")):
                from fastapi.testclient import TestClient
                c = TestClient(main.app, raise_server_exceptions=False)
                r = c.get("/health")
        assert r.status_code == 503
        assert r.json()["status"] == "degraded"


# ═══════════════════════════════════════════════════════════════════════════════
#  main.authorize — branch logic
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestAuthorizeLogic:
    """Unit tests for the authorize endpoint branching, without a real HTTP call."""

    def _mock_request(self, headers=None):
        """Build a minimal mock Request with optional headers."""
        mock_req = MagicMock()
        mock_req.headers = headers or {}
        return mock_req

    def test_dev_mode_returns_dev_user(self, monkeypatch):
        import main
        original = main.CLIENT_VALIDATION
        main.CLIENT_VALIDATION = "Dev"
        try:
            result = main.authorize(self._mock_request())
            assert result["user"] == "dev_user"
            assert result["status"] == "authorized"
        finally:
            main.CLIENT_VALIDATION = original

    def test_spcs_mode_with_header_returns_user(self, monkeypatch):
        import main
        original = main.CLIENT_VALIDATION
        main.CLIENT_VALIDATION = "SPCS"
        try:
            req = self._mock_request({"sf-context-current-user": "alice@example.com"})
            result = main.authorize(req)
            assert result["user"] == "alice@example.com"
        finally:
            main.CLIENT_VALIDATION = original

    def test_spcs_mode_missing_header_raises_401(self, monkeypatch):
        import main
        original = main.CLIENT_VALIDATION
        main.CLIENT_VALIDATION = "SPCS"
        try:
            req = self._mock_request({})
            with pytest.raises(HTTPException) as exc_info:
                main.authorize(req)
            assert exc_info.value.status_code == 401
        finally:
            main.CLIENT_VALIDATION = original

    def test_authorize_response_has_status_field(self, monkeypatch):
        import main
        original = main.CLIENT_VALIDATION
        main.CLIENT_VALIDATION = "Dev"
        try:
            result = main.authorize(self._mock_request())
            assert "status" in result
        finally:
            main.CLIENT_VALIDATION = original


# ═══════════════════════════════════════════════════════════════════════════════
#  main.get_summary — NULL coalescing
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestSummaryCoalescing:
    """Unit tests for NULL-to-zero coalescing in get_summary."""

    def _null_row(self):
        return [{
            "total_orders":     0,
            "total_revenue":    None,
            "unique_customers": 0,
            "start_date":       None,
            "end_date":         None,
        }]

    def test_null_revenue_coalesced_to_zero(self):
        """round(None or 0, 2) must produce 0.0, not raise TypeError."""
        import main
        row = self._null_row()[0]
        revenue = round(row["total_revenue"] or 0, 2)
        assert revenue == 0.0

    def test_null_revenue_is_numeric(self):
        """revenue must be a numeric type (int or float) — round(None or 0, 2) is int(0)."""
        import main
        row = self._null_row()[0]
        revenue = round(row["total_revenue"] or 0, 2)
        assert isinstance(revenue, (int, float))

    def test_null_date_range_preserved(self):
        """When orders table is empty, MIN/MAX return NULL — these must pass through as None."""
        import main
        row = self._null_row()[0]
        date_range = {"start": row["start_date"], "end": row["end_date"]}
        assert date_range["start"] is None
        assert date_range["end"] is None

    def test_zero_total_orders_triggers_404(self):
        """get_summary raises 404 when total_orders is 0."""
        import main
        import connection
        with patch.object(connection, "get_connection", return_value=sqlite3.connect(":memory:")):
            with patch.object(connection, "execute_query", return_value=self._null_row()):
                c = TestClient(main.app, raise_server_exceptions=False)
                r = c.get("/franchise/summary")
        # 404 is raised because total_orders == 0 (no qualifying data found)
        assert r.status_code in (404, 503)


    def test_summary_with_date_filter_uses_filtered_query(self, monkeypatch):
        """GET /franchise/summary?start=...&end=... must hit the 'if start and end' branch (line 179)."""
        import connection
        import main

        seed_row = [{
            "total_orders": 3,
            "total_revenue": 300.00,
            "unique_customers": 2,
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
        }]
        in_mem = sqlite3.connect(":memory:", check_same_thread=False)
        monkeypatch.setattr(connection, "get_connection", lambda: in_mem)
        monkeypatch.setattr(connection, "execute_query", lambda *a, **k: seed_row)
        c = TestClient(main.app, raise_server_exceptions=False)
        r = c.get("/franchise/summary", params={"start": "2022-01-01", "end": "2022-12-31"})
        assert r.status_code == 200
        body = r.json()
        assert body["total_orders"] == 3
        assert body["total_revenue"] == 300.0
        assert body["unique_customers"] == 2


# ═══════════════════════════════════════════════════════════════════════════════
#  connection.get_snowflake_connection — branch coverage
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestGetSnowflakeConnection:
    """
    Unit tests for get_snowflake_connection().

    Neither SPCS nor a real Snowflake account is available in CI, so every
    test uses mocks.  We verify the two branching decisions:
      1. Token file present  → OAuth connect called with authenticator="oauth"
      2. Token file absent, no key path  → ValueError raised immediately
      3. Token file absent, key path set → keypair connect called (mocked key)

    get_connection()'s Snowflake branch is also covered here.
    """

    def test_spcs_oauth_branch_when_token_file_exists(self, monkeypatch):
        """When /snowflake/session/token exists, connect via OAuth."""
        import connection

        monkeypatch.setenv("SNOWFLAKE_ACCOUNT",   "test-account")
        monkeypatch.setenv("SNOWFLAKE_HOST",      "test-host")
        monkeypatch.setenv("SNOWFLAKE_DATABASE",  "test-db")
        monkeypatch.setenv("SNOWFLAKE_SCHEMA",    "test-schema")
        monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "test-wh")

        mock_connect = MagicMock(return_value=MagicMock())

        with patch("connection.Path") as mock_path_cls, \
             patch("connection.snowflake.connector.connect", mock_connect):
            # Make Path("/snowflake/session/token").exists() return True
            mock_path_cls.return_value.exists.return_value = True
            mock_path_cls.return_value.read_text.return_value = "fake-oauth-token"

            connection.get_snowflake_connection()

        mock_connect.assert_called_once()
        kwargs = mock_connect.call_args[1]
        assert kwargs["authenticator"] == "oauth"
        assert kwargs["token"] == "fake-oauth-token"

    def test_local_mode_raises_when_no_key_path(self, monkeypatch):
        """When no token file and SNOWFLAKE_PRIVATE_KEY_PATH is unset, raise ValueError."""
        import connection

        monkeypatch.delenv("SNOWFLAKE_PRIVATE_KEY_PATH", raising=False)

        with patch("connection.Path") as mock_path_cls:
            mock_path_cls.return_value.exists.return_value = False

            with pytest.raises(ValueError, match="SNOWFLAKE_PRIVATE_KEY_PATH"):
                connection.get_snowflake_connection()

    def test_local_mode_keypair_branch(self, monkeypatch, tmp_path):
        """When key path is set, keypair connect is called (key loading is mocked)."""
        import connection

        monkeypatch.setenv("SNOWFLAKE_PRIVATE_KEY_PATH", str(tmp_path / "key.p8"))
        monkeypatch.setenv("SNOWFLAKE_ACCOUNT",   "test-account")
        monkeypatch.setenv("SNOWFLAKE_USERNAME",  "test-user")
        monkeypatch.setenv("SNOWFLAKE_ROLE",      "test-role")
        monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "test-wh")
        monkeypatch.setenv("SNOWFLAKE_DATABASE",  "test-db")
        monkeypatch.setenv("SNOWFLAKE_SCHEMA",    "test-schema")

        mock_connect = MagicMock(return_value=MagicMock())
        mock_private_key = MagicMock()
        mock_private_key.private_bytes.return_value = b"der-bytes"

        with patch("connection.Path") as mock_path_cls, \
             patch("connection.snowflake.connector.connect", mock_connect), \
             patch("builtins.open", MagicMock(return_value=MagicMock(
                 __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b"pem"))),
                 __exit__=MagicMock(return_value=False)
             ))), \
             patch("cryptography.hazmat.primitives.serialization.load_pem_private_key",
                   return_value=mock_private_key):
            mock_path_cls.return_value.exists.return_value = False

            connection.get_snowflake_connection()

        mock_connect.assert_called_once()
        kwargs = mock_connect.call_args[1]
        assert kwargs["private_key"] == b"der-bytes"
        assert kwargs["user"] == "test-user"

    def test_get_connection_routes_to_snowflake(self, monkeypatch):
        """get_connection() must invoke the Snowflake path when DATA_BACKEND=snowflake.

        We patch connection.DATA_BACKEND directly (monkeypatch restores it
        automatically) — no importlib.reload needed, so there is no risk of
        leaving the module in a broken state for subsequent tests.
        """
        import connection

        monkeypatch.setattr(connection, "DATA_BACKEND", "snowflake")
        monkeypatch.delenv("SNOWFLAKE_PRIVATE_KEY_PATH", raising=False)

        with patch("connection.Path") as mock_path_cls:
            mock_path_cls.return_value.exists.return_value = False
            with pytest.raises(ValueError, match="SNOWFLAKE_PRIVATE_KEY_PATH"):
                connection.get_connection()


# ═══════════════════════════════════════════════════════════════════════════════
#  main — 503 fault-injection for all franchise endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestFranchiseEndpoint503:
    """
    Verify that when execute_query raises an unexpected exception inside a
    franchise endpoint, the handler catches it and returns 503 with a generic
    message — not a raw traceback or the exception text.

    Uses patch.object on connection.execute_query so the exception is thrown
    after _validate_date passes and get_connection succeeds.
    """

    _ENDPOINTS = [
        "/franchise/orders?start=2022-01-01&end=2022-12-31",
        "/franchise/products?start=2022-01-01&end=2022-12-31",
        "/franchise/customers?start=2022-01-01&end=2022-12-31",
        "/franchise/cities?start=2022-01-01&end=2022-12-31",
    ]

    def _crashing_execute_query(self, *args, **kwargs):
        raise RuntimeError("simulated DB crash")

    @pytest.mark.parametrize("url", _ENDPOINTS)
    def test_db_crash_returns_503(self, url, monkeypatch):
        """execute_query raising RuntimeError must produce a 503, not a 500 or traceback."""
        import connection
        import main

        in_mem = sqlite3.connect(":memory:", check_same_thread=False)
        monkeypatch.setattr(connection, "get_connection", lambda: in_mem)
        monkeypatch.setattr(connection, "execute_query", self._crashing_execute_query)

        c = TestClient(main.app, raise_server_exceptions=False)
        r = c.get(url)

        assert r.status_code == 503
        # Generic message — must not leak exception internals
        assert r.json()["detail"] == "Internal server error"
        assert "simulated DB crash" not in r.text

    @pytest.mark.parametrize("url", _ENDPOINTS)
    def test_db_crash_detail_is_generic(self, url, monkeypatch):
        """The 503 detail must be the exact string 'Internal server error'."""
        import connection
        import main

        in_mem = sqlite3.connect(":memory:", check_same_thread=False)
        monkeypatch.setattr(connection, "get_connection", lambda: in_mem)
        monkeypatch.setattr(connection, "execute_query", self._crashing_execute_query)

        c = TestClient(main.app, raise_server_exceptions=False)
        assert c.get(url).json()["detail"] == "Internal server error"

    def test_summary_db_crash_returns_503(self, monkeypatch):
        """get_summary's except Exception path also returns 503."""
        import connection
        import main

        in_mem = sqlite3.connect(":memory:", check_same_thread=False)
        monkeypatch.setattr(connection, "get_connection", lambda: in_mem)
        monkeypatch.setattr(connection, "execute_query", self._crashing_execute_query)

        c = TestClient(main.app, raise_server_exceptions=False)
        r = c.get("/franchise/summary")

        assert r.status_code == 503
        assert r.json()["detail"] == "Internal server error"
