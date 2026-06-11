import numpy as np
import cec2017.functions as cec_functions


class CEC2017Benchmark:
    def __init__(self, func_id, dimension):
        self.func_id = func_id
        self.dimension = dimension
        self.lower_bound = -100.0
        self.upper_bound = 100.0
        
        func_map = {
            1: cec_functions.f1,
            3: cec_functions.f3,
            5: cec_functions.f5,
            9: cec_functions.f9,
            10: cec_functions.f10,
            15: cec_functions.f15,
            20: cec_functions.f20,
            23: cec_functions.f23,
            28: cec_functions.f28,
        }
        
        if func_id not in func_map:
            raise ValueError(f"Function F{func_id} not supported. Use: {list(func_map.keys())}")
        
        self.func = func_map[func_id]
        self.func_name = f"F{func_id}"
    
    def evaluate(self, x):
        x = np.atleast_2d(x)
        return self.func(x)[0]
    
    def evaluate_batch(self, X):
        X = np.atleast_2d(X)
        return self.func(X)
    
    def __call__(self, x):
        return self.evaluate(x)


def get_cec2017_functions():
    return [1, 3, 5, 9, 10, 15, 20, 23, 28]


def create_benchmark(func_id, dimension):
    return CEC2017Benchmark(func_id, dimension)
