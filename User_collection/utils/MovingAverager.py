from typing import List, Union
import numpy as np


def moving_average(data: np.ndarray, window: int):
    padding_num = int(np.floor(window / 2))
    start_padding = data[:padding_num].mean().repeat(padding_num)
    end_padding = data[len(data)-padding_num:].mean().repeat(padding_num)

    values = np.concatenate([start_padding, data, end_padding])

    ret = np.cumsum(values, dtype=float)
    ret[window:] = ret[window:] - ret[:-window]
    return ret[window - 1:] / window


class MovingAverager:
    def __init__(self, windows: Union[List[int], int]):
        if isinstance(windows, List):
            self.windows = windows
        elif isinstance(windows, int):
            self.windows = [windows]
        self.max_window = max(self.windows)
    
    def execute(self, data):
        assert len(data) >= self.max_window
        
        result = np.zeros(len(data))

        for window in self.windows:
            result += moving_average(data=data, window=window)
        result /= len(self.windows)

        return result
