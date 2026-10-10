"""Mocked process inventory: launchers belong to this run; other Python stops."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import explore_b0_sample_check as sample_check


@pytest.mark.parametrize("processes,stops,chain", [
    ([dict(ProcessId=101, ParentProcessId=100, Name="python.exe"),
      dict(ProcessId=100, ParentProcessId=90, Name="python.exe")], False, [101, 100]),
    ([dict(ProcessId=101, ParentProcessId=100, Name="python.exe"),
      dict(ProcessId=100, ParentProcessId=90, Name="python.exe"),
      dict(ProcessId=777, ParentProcessId=700, Name="pythonw.exe")], True, None),
    ([], False, []),
])
def test_process_inventory(monkeypatch, processes, stops, chain):
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")
    monkeypatch.setattr(sample_check.time, "sleep", lambda _: None)
    monkeypatch.setattr(sample_check.os, "getpid", lambda: 101)

    def power_status(pointer):
        pointer._obj.ACLineStatus = 1
        return 1

    monkeypatch.setattr(sample_check.ctypes.windll.kernel32, "GetSystemPowerStatus", power_status)

    def check_output(command, **kwargs):
        if command[0] == "powershell":
            assert "Get-CimInstance Win32_Process" in command[-1]
            assert command[-1].endswith("exit 0")
            return json.dumps(processes)
        if "--query-compute-apps=pid,process_name" in command:
            return ""
        return "600, 6144, 3"

    monkeypatch.setattr(sample_check.subprocess, "check_output", check_output)
    if stops:
        with pytest.raises(RuntimeError, match="777.*700.*pythonw.exe"):
            sample_check.gpu_preflight()
    else:
        result = sample_check.gpu_preflight()
        assert [p["ProcessId"] for p in result["this_run_chain"]] == chain
        assert result["other_python_processes"] == []


@pytest.mark.parametrize("memory,utilization,stops", [(600, 3, False), (2000, 3, True), (600, 40, False)])
def test_wddm_desktop_apps_and_resource_gate(monkeypatch, memory, utilization, stops):
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")
    monkeypatch.setattr(sample_check.time, "sleep", lambda _: None)
    monkeypatch.setattr(sample_check.os, "getpid", lambda: 101)
    samples = []

    def power_status(pointer):
        pointer._obj.ACLineStatus = 1
        return 1

    monkeypatch.setattr(sample_check.ctypes.windll.kernel32, "GetSystemPowerStatus", power_status)

    def check_output(command, **kwargs):
        assert kwargs["encoding"] == "utf-8" and kwargs["errors"] == "replace"
        if command[0] == "powershell":
            return "[]"
        if "--query-compute-apps=pid,process_name" in command:
            return "123, explorer.exe\n456, Discord.exe"
        samples.append(1)
        return f"{memory}, 6144, {utilization}"

    monkeypatch.setattr(sample_check.subprocess, "check_output", check_output)
    if stops:
        with pytest.raises(RuntimeError, match="GPU preflight") as error:
            sample_check.gpu_preflight()
        result = error.value.preflight
    else:
        result = sample_check.gpu_preflight()
    assert len(samples) == 5
    assert len(result["gpu_samples"]) == 5
    assert result["max_memory_used_mib"] == memory
    assert result["mean_utilization_gpu_percent"] == utilization
    assert result["utilization_record_only"] is True
    assert "Discord.exe" in result["gpu_compute_processes"]
