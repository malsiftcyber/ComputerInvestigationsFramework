from setuptools import setup, find_packages

setup(
    name='cif-agent',
    version='0.1.0',
    description='Computer Investigations Framework Agent',
    author='CIF Team',
    py_modules=['agent'],
    install_requires=[
        'python-socketio==5.10.0',
        'psutil==5.9.6',
    ],
    # Optional Windows-specific dependencies
    extras_require={
        'windows': ['pywin32>=306'],
    },
    entry_points={
        'console_scripts': [
            'cif-agent=agent:main',
        ],
    },
)
