from session_manager.components import replay_station


def test_is_local_mqtt_host_variants() -> None:
    assert replay_station._is_local_mqtt_host("localhost")
    assert replay_station._is_local_mqtt_host("127.0.0.1")
    assert replay_station._is_local_mqtt_host("::1")
    assert replay_station._is_local_mqtt_host("0.0.0.0")
    assert not replay_station._is_local_mqtt_host("192.168.0.100")
    assert not replay_station._is_local_mqtt_host("example.local")


def test_preflight_skips_non_local_hosts() -> None:
    ok, reason = replay_station._mqtt_single_instance_preflight("192.168.0.100", 1883)
    assert ok
    assert reason == ""


def test_preflight_fails_on_duplicate_mqtt_listener(monkeypatch) -> None:
    monkeypatch.setattr(
        replay_station,
        "_local_single_broker_pid",
        lambda host, port: (None, "Duplicate MQTT listeners detected on localhost:1883 (pids: 1, 2)."),
    )

    ok, reason = replay_station._mqtt_single_instance_preflight("localhost", 1883)
    assert not ok
    assert "Duplicate MQTT listeners" in reason


def test_preflight_fails_when_ws_pid_differs(monkeypatch) -> None:
    monkeypatch.setattr(replay_station, "_local_single_broker_pid", lambda host, port: (101, ""))

    def fake_listener_pids(port: int):
        if port == 9001:
            return {202}, ""
        return set(), ""

    monkeypatch.setattr(replay_station, "_local_listener_pids", fake_listener_pids)
    monkeypatch.setattr(replay_station, "_local_mqtt_related_pids", lambda: ({101}, ""))

    ok, reason = replay_station._mqtt_single_instance_preflight("localhost", 1883)
    assert not ok
    assert "websocket port 9001" in reason


def test_preflight_fails_when_multiple_mqtt_processes_found(monkeypatch) -> None:
    monkeypatch.setattr(replay_station, "_local_single_broker_pid", lambda host, port: (101, ""))
    monkeypatch.setattr(
        replay_station, "_local_listener_pids", lambda port: ({101}, "") if port == 9001 else (set(), "")
    )
    monkeypatch.setattr(replay_station, "_local_mqtt_related_pids", lambda: ({101, 202}, ""))

    ok, reason = replay_station._mqtt_single_instance_preflight("localhost", 1883)
    assert not ok
    assert "multiple local MQTT-related listener processes detected" in reason


def test_preflight_passes_for_single_local_broker(monkeypatch) -> None:
    monkeypatch.setattr(replay_station, "_local_single_broker_pid", lambda host, port: (101, ""))
    monkeypatch.setattr(
        replay_station, "_local_listener_pids", lambda port: ({101}, "") if port == 9001 else (set(), "")
    )
    monkeypatch.setattr(replay_station, "_local_mqtt_related_pids", lambda: ({101}, ""))

    ok, reason = replay_station._mqtt_single_instance_preflight("localhost", 1883)
    assert ok
    assert reason == ""
