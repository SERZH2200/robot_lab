from dataclasses import dataclass

from language.runtime.environment import Environment


@dataclass
class Frame:
    function_name: str
    environment: Environment
