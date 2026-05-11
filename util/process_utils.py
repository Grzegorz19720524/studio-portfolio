import os
import sys
import shutil
import signal
import subprocess
from typing import Any


def run(
    cmd: list[str],
    cwd: str | None = None,
    env: dict | None = None,
    timeout: float | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=cwd, env=env, timeout=timeout,
        check=check, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def run_shell(
    cmd: str,
    cwd: str | None = None,
    timeout: float | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, shell=True, cwd=cwd, timeout=timeout,
        check=check, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def get_output(cmd: list[str] | str, shell: bool = False, cwd: str | None = None) -> str:
    result = subprocess.run(
        cmd, shell=shell, cwd=cwd, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def run_bg(cmd: list[str] | str, shell: bool = False, cwd: str | None = None) -> subprocess.Popen:
    return subprocess.Popen(cmd, shell=shell, cwd=cwd,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_piped(commands: list[list[str]], cwd: str | None = None) -> str:
    procs = []
    for i, cmd in enumerate(commands):
        stdin = procs[-1].stdout if procs else None
        p = subprocess.Popen(cmd, stdin=stdin, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=cwd)
        procs.append(p)
    stdout, _ = procs[-1].communicate()
    for p in procs[:-1]:
        p.wait()
    return stdout.decode().strip()


def which(name: str) -> str | None:
    return shutil.which(name)


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def get_pid() -> int:
    return os.getpid()


def pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def cpu_count() -> int:
    return os.cpu_count() or 1


def python_version() -> str:
    return sys.version.split()[0]


def platform_info() -> dict[str, str]:
    import platform
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": python_version(),
    }


def kill(pid: int, sig: int = signal.SIGTERM) -> None:
    os.kill(pid, sig)


def env_var(name: str, default: Any = None) -> Any:
    return os.environ.get(name, default)


def set_env_var(name: str, value: str) -> None:
    os.environ[name] = value


def all_env_vars() -> dict[str, str]:
    return dict(os.environ)


if __name__ == "__main__":
    print("get_pid():        ", get_pid())
    print("cpu_count():      ", cpu_count())
    print("python_version(): ", python_version())
    print("platform_info():  ", platform_info())
    print()
    print("which('python'):  ", which("python"))
    print("command_exists('git'):", command_exists("git"))
    print("command_exists('xyz'):", command_exists("xyz"))
    print()
    result = run(["python", "--version"])
    print("run(['python','--version']):")
    print("  stdout:", result.stdout.strip())
    print("  returncode:", result.returncode)
    print()
    output = get_output(["python", "-c", "print('hello from subprocess')"])
    print("get_output:", output)
    print()
    print("pid_exists(get_pid()):", pid_exists(get_pid()))
    print("pid_exists(99999999): ", pid_exists(99999999))
    print()
    print("env_var('PATH')[:40]:", env_var("PATH", "")[:40] + "...")
