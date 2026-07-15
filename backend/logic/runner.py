# backend/logic/runner.py
# batch/scraper.py をバックグラウンドのサブプロセスとして起動し、状態を管理する
import os
import subprocess
import sys
import threading

# backend/ をルートとする
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_lock = threading.Lock()
_state = {
    "running": False,
    "completed": False,
    "success": False,
    "log": [],
}


# サブプロセスを実行し、出力を1行ずつ状態に蓄積する
def _run():
    process = subprocess.Popen(
        [sys.executable, "batch/scraper.py"],
        cwd=BACKEND_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    for line in process.stdout:
        with _lock:
            _state["log"].append(line.rstrip())
            _state["log"] = _state["log"][-200:]

    process.wait()

    with _lock:
        _state["running"] = False
        _state["completed"] = True
        _state["success"] = process.returncode == 0


# スクレイプを開始する。既に実行中なら何もせずFalseを返す
def start_scrape() -> bool:
    with _lock:
        if _state["running"]:
            return False
        _state["running"] = True
        _state["completed"] = False
        _state["success"] = False
        _state["log"] = []

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return True


# 現在の状態を返す
def get_status() -> dict:
    with _lock:
        return {
            "running": _state["running"],
            "completed": _state["completed"],
            "success": _state["success"],
            "log": _state["log"][-50:],
        }