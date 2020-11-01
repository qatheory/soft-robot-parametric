# import file path to environment
import sys
import os
from pathlib import Path
from optimizer.optimize import optimize

transpose_file = Path("transpose_output.csv")
if transpose_file.is_file():
    open('transpose_output.csv', 'w').close()
optimize(10)
