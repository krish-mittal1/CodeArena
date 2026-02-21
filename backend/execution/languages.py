from __future__ import annotations

"""
Language configuration — Docker images, compile/run commands, file extensions.
"""

from dataclasses import dataclass
from backend.core.constants import Language


@dataclass
class LanguageConfig:
    image: str
    file_extension: str
    compile_cmd: str | None
    run_cmd: str
    needs_compilation: bool = False


LANGUAGE_CONFIGS: dict[str, LanguageConfig] = {
    Language.PYTHON: LanguageConfig(
        image="codearena-runner-python",
        file_extension=".py",
        compile_cmd=None,
        run_cmd="python3 /sandbox/code.py",
    ),

    # ✅ FIXED C++ CONFIG
    Language.CPP: LanguageConfig(
        image="codearena-runner-cpp",
        file_extension=".cpp",
        compile_cmd=(
            "g++ -O2 -std=gnu++17 -Wall -Wextra "
            "-DONLINE_JUDGE -o /sandbox/solution /sandbox/code.cpp"
        ),
        run_cmd="/sandbox/solution",
        needs_compilation=True,
    ),

    Language.JAVA: LanguageConfig(
        image="codearena-runner-java",
        file_extension=".java",
        compile_cmd="javac /sandbox/Solution.java -d /sandbox",
        run_cmd="java -cp /sandbox Solution",
        needs_compilation=True,
    ),

    Language.JAVASCRIPT: LanguageConfig(
        image="codearena-runner-node",
        file_extension=".js",
        compile_cmd=None,
        run_cmd="node /sandbox/code.js",
    ),
}


def get_language_config(language: str) -> LanguageConfig:
    config = LANGUAGE_CONFIGS.get(language)
    if not config:
        raise ValueError(f"Unsupported language: {language}")
    return config