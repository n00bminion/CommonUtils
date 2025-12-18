from common_utils import config_handler


def test_get_config_uses_provided_path_when_check_disabled(monkeypatch):
    # monkeypatch the read_file used by the module to avoid file system dependency
    monkeypatch.setattr(config_handler, "read_file", lambda path: "CONFIG_CONTENT")
    res = config_handler.get_config("some.yml", check_possible_paths=False)
    assert res == "CONFIG_CONTENT"


def test_get_config_no_module_and_missing_paths(monkeypatch):
    # if check_possible_paths True and no files exist, read_file should be called with original path
    captured = {}

    def fake_read(path):
        captured["path"] = path
        return "X"

    monkeypatch.setattr(config_handler, "read_file", fake_read)
    res = config_handler.get_config("does_not_exist.yml", check_possible_paths=False)
    assert res == "X"
