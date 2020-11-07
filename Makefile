all: asciicast2movie tty2img

asciicast2movie:
	@rm -rf build
	python3 setup-asciicast2movie.py sdist bdist_wheel

tty2img:
	@rm -rf build
	python3 setup-tty2img.py sdist bdist_wheel

clean:
	rm -rf  __pycache__ build asciicast2movie.egg-info tty2img.egg-info

clean-full: clean
	rm -rf  dist

upload:
	twine upload dist/*
