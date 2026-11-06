from types import SimpleNamespace

import pytest

import agent.agent as agent_module
from agent.agent import forget_memory, list_memories, recall_memories, save_memory


class FakeMemory:
    def __init__(self, *, search_result=None, list_result=None, fail=False):
        self.search_result = search_result or {}
        self.list_result = list_result or {}
        self.fail = fail
        self.calls = []

    def _record(self, name, *args, **kwargs):
        self.calls.append((name, args, kwargs))
        if self.fail:
            raise RuntimeError("backend down")

    def add(self, *args, **kwargs):
        self._record("add", *args, **kwargs)

    def search(self, *args, **kwargs):
        self._record("search", *args, **kwargs)
        return self.search_result

    def list_memories(self, *args, **kwargs):
        self._record("list_memories", *args, **kwargs)
        return self.list_result

    def delete(self, *args, **kwargs):
        self._record("delete", *args, **kwargs)


@pytest.fixture
def use_memory(monkeypatch):
    def _install(fake):
        monkeypatch.setattr(agent_module, "memory", fake)
        return fake

    return _install


def test_save_memory_adds_fact(use_memory):
    fake = use_memory(FakeMemory())
    assert save_memory("User prefers uv over pip.") == "Saved to long-term memory."
    assert fake.calls[0][0] == "add"
    assert fake.calls[0][1] == ("User prefers uv over pip.",)


def test_save_memory_reports_backend_failure(use_memory):
    use_memory(FakeMemory(fail=True))
    assert "Failed to save" in save_memory("anything")


def test_list_memories_formats_id_and_content(use_memory):
    use_memory(
        FakeMemory(
            list_result={
                "vdb": {
                    "memories": [
                        {"memory_id": "m1", "content": "fact one"},
                        {"memory_id": "m2", "content": "fact two"},
                        {"memory_id": "m3", "content": ""},
                    ]
                }
            }
        )
    )
    assert list_memories() == "m1: fact one\nm2: fact two"


def test_list_memories_empty(use_memory):
    use_memory(FakeMemory(list_result={"vdb": {"memories": []}}))
    assert list_memories() == "No memories stored."


def test_list_memories_reports_backend_failure(use_memory):
    use_memory(FakeMemory(fail=True))
    assert "Failed to list" in list_memories()


def test_forget_memory_deletes_by_id(use_memory):
    fake = use_memory(FakeMemory())
    assert forget_memory("m1") == "Deleted memory m1."
    assert fake.calls[0] == ("delete", ("m1",), {})


def test_forget_memory_reports_backend_failure(use_memory):
    use_memory(FakeMemory(fail=True))
    assert "Failed to delete" in forget_memory("m1")


def test_recall_memories_formats_bullets(use_memory):
    use_memory(
        FakeMemory(
            search_result={
                "memories": {
                    "profile": [{"content": "likes terse answers"}],
                    "facts": [{"content": "works in Python"}, {"not_content": "ignored"}],
                }
            }
        )
    )
    out = recall_memories(SimpleNamespace(prompt="hello"))
    assert out.startswith("Memories about the user recalled")
    assert "- likes terse answers" in out
    assert "- works in Python" in out


def test_recall_memories_skips_blank_or_non_string_prompt(use_memory):
    fake = use_memory(FakeMemory())
    assert recall_memories(SimpleNamespace(prompt="   ")) == ""
    assert recall_memories(SimpleNamespace(prompt=None)) == ""
    assert fake.calls == []


def test_recall_memories_swallows_backend_failure(use_memory):
    use_memory(FakeMemory(fail=True))
    assert recall_memories(SimpleNamespace(prompt="hello")) == ""
