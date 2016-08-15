from setuptools import find_packages, setup
from chip8.setup_commands import commands as setup_commands
# https://github.com/secondsun/chip8
# https://johnearnest.github.io/Octo/


setup(
    name='chip8',
    version='0.0.1',
    description=u"CHIP-8",
    long_description="",
    keywords='',
    author=u"Matthieu Honel",
    author_email='matthieu.honel@free.fr',
    url='https://github.com/ocus/py-chip8',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    cmdclass=setup_commands,
    install_requires=[
        # 'pillow'
    ],
    test_suite='tests.chip8_test_suite',
    tests_require=[
        'mock',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
    ]
)
