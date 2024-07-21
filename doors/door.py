from typing import Self
from abc import ABC, abstractmethod

class DoorHost(ABC):
    @abstractmethod
    def load_state(self: Self, short_name: str) -> str:
        pass

    @abstractmethod
    def store_state(self: Self, short_name: str, state: str) -> None:
        pass
    
    @abstractmethod
    def print_local(self: Self, sender_short_name : str, data: str) -> None:
        pass

    @abstractmethod
    def send_remote_command(self: Self, sender_short_name: str, recipient_short_name : str, data: str) -> None:
        pass

    @abstractmethod
    def exit_door(self: Self, short_name: str) -> None:
        pass

class Door(ABC):
    @abstractmethod
    def try_process_local_command(host: DoorHost, sender_short_name : str, data: str) -> bool:
        pass

    @abstractmethod
    def try_process_remote_command(host: DoorHost, sender_short_name: str, recipient_short_name : str,  data: str) -> bool:
        pass