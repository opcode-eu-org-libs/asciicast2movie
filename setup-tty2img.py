import setuptools
import tty2img

setuptools.setup(
    name="tty2img",
    py_modules=["tty2img"],
    version="0.2.0",
    author="Robert Paciorek",
    author_email="robert@opcode.eu.org",
    description="rendering pyte terminal emulator screen as image",
    long_description=tty2img.__doc__,
    long_description_content_type="text/plain",
    keywords='asciicast video movie mp4 tty pyte moviepy',
    install_requires=[
        'pyte',
        'pillow'
    ],
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
