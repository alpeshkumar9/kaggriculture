"""
Official Kaggle Environments Entrypoint for Kaggriculture
"""
import sys
import os

dir_path = os.path.dirname(os.path.abspath(__file__))
if dir_path not in sys.path:
    sys.path.insert(0, dir_path)

from agent import agent

def my_agent(observation, configuration=None):
    return agent(observation, configuration)
