# list obv. is just a typical import
from src._internal.configs import ModuleExecutionContext

# means that all that can be `import` (__all__) is in this list.
__all__ = ["ModuleExecutionContext"]

# Putting it together, it's sassing "lets import thing, but it's __all__ than can imported
# I found it in the docs and thought it could be cool