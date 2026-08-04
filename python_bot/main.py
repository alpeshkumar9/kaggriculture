"""
Official Kaggle Environments Entrypoint for Kaggriculture
"""
from agent import agent

def my_agent(observation, configuration=None):
    return agent(observation, configuration)
