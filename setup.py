from setuptools import find_packages, setup

# https://github.com/secondsun/chip8
# https://johnearnest.github.io/Octo/

setup(
    name='chip8',
    version='0.0.1',
    description=u"CHIP-8",
    long_description="",
    keywords='',
    author=u"Matthie Honel",
    author_email='matthieu.honel@free.fr',
    url='https://bitbucket.org/adnow/adnow_python_lib',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    test_suite='tests.chip8',
    tests_require=[
        'mock',
        'timeout-decorator'
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