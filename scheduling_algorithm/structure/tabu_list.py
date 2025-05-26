from collections import deque
from typing import Tuple

class TabuList:
    def __init__(self, size: int = 50):
        self.size = size
        self.tabu_moves = deque(maxlen=size)
    
    def __str__(self):
        return f"TabuList(size={self.size}, tabu_moves={list(self.tabu_moves)})"
    
    def __contains__(self, move: Tuple[int, int]):
        return move in self.tabu_moves
    
    def add(self, move: Tuple[int, int]):
        self.tabu_moves.append(move)
    
    def clear(self):
        self.tabu_moves.clear()
    
    def is_tabu(self, move: Tuple[int, int]):
        """Check if a move is in the tabu list."""
        return move in self.tabu_moves
    
    def configure(self, size: int):
        self.size = size
        self.tabu_moves = deque(maxlen=size)
        return self