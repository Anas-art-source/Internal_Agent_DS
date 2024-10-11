from functools import wraps
from inspect import signature

def check_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = signature(func)
        bound_args = sig.bind_partial(*args, **kwargs)
        bound_args.apply_defaults()
        
        for name, param in sig.parameters.items():
            if name not in bound_args.arguments and param.default is param.empty:
                raise ValueError(f"Missing argument: {name}")
        
        return func(*args, **kwargs)
    
    return wrapper