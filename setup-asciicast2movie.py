import setuptools
import asciicast2movie

setuptools.setup(
    name="asciicast2movie",
    py_modules=["asciicast2movie"],
    version="0.3.0",
    author="Robert Paciorek",
    author_email="robert@opcode.eu.org",
    description="generate movie (video clip) from asciicast",
    long_description=asciicast2movie.__doc__,
    long_description_content_type="text/plain",
    keywords='asciicast video movie mp4 tty pyte moviepy',
    install_requires=[
        'tty2img',
        'moviepy'
    ],
    entry_points={
        'console_scripts': [
            'asciicast2movie=asciicast2movie:main',
        ],
    },
    license='MIT',
    url="https://bitbucket.org/OpCode-eu-org/asciicast2movie/",
    project_urls={
        'GitHub': 'https://github.com/opcode-eu-org-libs/asciicast2movie/'
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
