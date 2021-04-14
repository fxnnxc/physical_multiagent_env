from setuptools import setup

setup(
    name = "fxnnxc_follower",
    version ="0.1",
    description="gym multiagent environments for multiagent using pybullet",
    author = "fxnnxc",
    install_requires=[
        'pybullet>=3.0.8',
        'gym>=0.18.0',
        'numpy>=1.18.5'
    ]
)