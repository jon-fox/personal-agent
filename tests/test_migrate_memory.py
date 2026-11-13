import pytest

import agent.migrate_memory as migrate_module
from agent.migrate_memory import main


class FakeClient:
    instance = None

    def __init__(self, *args, **kwargs):
        FakeClient.instance = self
        self.clone_args = None
        self.result = {"success": True, "cloned_count": 3}

    def clone_user(self, src, dst):
        self.clone_args = (src, dst)
        return self.result


@pytest.fixture
def fake_client(monkeypatch):
    monkeypatch.setattr(migrate_module, "HyMemoryClient", FakeClient)
    return FakeClient


def test_migrate_defaults_destination_to_current_user(fake_client, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["personal-agent-migrate-memory", "old-id"])
    main()
    assert fake_client.instance.clone_args == ("old-id", migrate_module.MEMORY_USER_ID)
    assert "Copied 3 memories from 'old-id'" in capsys.readouterr().out


def test_migrate_explicit_destination(fake_client, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["personal-agent-migrate-memory", "old-id", "new-id"])
    main()
    assert fake_client.instance.clone_args == ("old-id", "new-id")
    assert "to 'new-id'" in capsys.readouterr().out


def test_migrate_failure_exits_with_error(fake_client, monkeypatch):
    monkeypatch.setattr("sys.argv", ["personal-agent-migrate-memory", "old-id"])

    def failing_clone(self, src, dst):
        return {"success": False, "error_message": "destination not empty"}

    monkeypatch.setattr(FakeClient, "clone_user", failing_clone)
    with pytest.raises(SystemExit, match="destination not empty"):
        main()
