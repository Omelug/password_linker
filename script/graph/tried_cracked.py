import sys
import matplotlib.pyplot as plt

# Ensure the plot is displayed inline in the Jupyter notebook
#%matplotlib inline

__author__ = 'Omelug'
__date__ = '2024'
__description__ = """Show grap from x\ty values"""

__in_format__ = {"x_T_y": True}
__out_format__ = {}

def run(args,config=None):
    x_values = []
    y_values = []

    for line in sys.stdin:
        x, y = line.strip().split('\t')
        x_values.append(float(x))
        y_values.append(float(y))

    plt.plot(x_values, y_values, marker='o', linestyle='-')

    plt.ylabel('Cracked')
    plt.xlabel('Tried')
    plt.title('Efficency')

    plt.show()