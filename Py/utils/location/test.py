import os

print(os.getcwd())
print(os.path.dirname(__file__))
print(os.path.dirname(os.path.dirname(__file__)))
print(os.path.abspath(__file__))

if False:
    import sys
    sys.path.append(os.path.dirname(__file__) + '/../../../')
    import AutoCarousell