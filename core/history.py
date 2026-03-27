"""
撤销重做管理
"""
import copy

class HistoryManager:
    def __init__(self):
        self.history = []
        self.current_step = -1

    def push(self, state):
        """保存状态，如果是新的操作，则清除之后的所有重做历史"""
        # 深拷贝状态以确保独立
        cloned_state = copy.deepcopy(state)
        
        # 截断之后的状态（因为产生了新的分支）
        self.history = self.history[:self.current_step + 1]
        
        self.history.append(cloned_state)
        self.current_step += 1

    def undo(self):
        """撤销操作"""
        if self.current_step > 0:
            self.current_step -= 1
            return copy.deepcopy(self.history[self.current_step])
        return None

    def redo(self):
        """重做操作"""
        if self.current_step < len(self.history) - 1:
            self.current_step += 1
            return copy.deepcopy(self.history[self.current_step])
        return None

    def can_undo(self):
        return self.current_step > 0

    def can_redo(self):
        return self.current_step < len(self.history) - 1

    def clear(self):
        self.history.clear()
        self.current_step = -1
