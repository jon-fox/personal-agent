import importlib

import constants.agent_constants as consts


def _reload(monkeypatch, **env):
    for key in ("MEMORY_USER_ID", "AGENT_MODEL", "ADVISOR_MODEL", "MEMORY_MODE"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return importlib.reload(consts)


def test_defaults(monkeypatch):
    mod = _reload(monkeypatch)
    assert mod.AGENT_MODEL == mod.OPENAI_SOL
    assert mod.ADVISOR_MODEL == mod.OPENAI_SOL
    assert mod.MEMORY_MODE == "pro"


def test_env_overrides(monkeypatch):
    mod = _reload(monkeypatch, AGENT_MODEL="anthropic:x", MEMORY_MODE="lite", MEMORY_USER_ID="me")
    assert mod.AGENT_MODEL == "anthropic:x"
    assert mod.MEMORY_MODE == "lite"
    assert mod.MEMORY_USER_ID == "me"


def test_empty_user_id_falls_back_to_os_user(monkeypatch):
    monkeypatch.setattr("getpass.getuser", lambda: "osuser")
    assert _reload(monkeypatch, MEMORY_USER_ID="").MEMORY_USER_ID == "osuser"


def test_user_id_falls_back_to_default_when_getuser_fails(monkeypatch):
    def boom():
        raise OSError

    monkeypatch.setattr("getpass.getuser", boom)
    assert _reload(monkeypatch).MEMORY_USER_ID == "default"
