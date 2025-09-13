
from abc import ABC, abstractmethod
class BaseAgent(ABC):
    @abstractmethod
    def create_graph(self):
        pass
    @abstractmethod
    def run(self):
        pass