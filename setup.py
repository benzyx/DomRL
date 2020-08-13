from setuptools import setup, find_packages

setup(
    name="DomRL",
    version="0.1",
    description='Dominion simulation framework tailored to building agents that have the exact information set as '
                'humans in online play.',
    packages=find_packages(),
    license='MIT',
    install_requires=['numpy'],
)