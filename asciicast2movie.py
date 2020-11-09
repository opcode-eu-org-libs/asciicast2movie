#!/usr/bin/env python3

'''
generate movie (video clip) from asciicast

Can be used as command line tool for convert asciicast file to video files:
  asciicast2movie.py input_asciicast_file.cast output_video_file.mp4

Can be also imported as a module and contains functions:
  * asciicast2video - convert asciicast data to moviepy video clip

Requires:
  * pyte (https://pypi.org/project/pyte/) VTXXX terminal emulator
  * tty2img (https://pypi.org/project/tty2img/) lib for rendering pyte screen as image
  * moviepy (https://pypi.org/project/moviepy/) video editing library
  * numpy (https://pypi.org/project/numpy/) array computing (for moviepy)

Copyright © 2020, Robert Ryszard Paciorek <rrp@opcode.eu.org>, MIT licence
'''

import pyte
import tty2img
import moviepy.editor as mpy
import numpy
import io, json

def render_asciicast_frames(
		inputData,
		screen,
		stream,
		startFrameTime = 0,
		lastFrameDuration = 3,
		renderOptions = {}
	):
	'''Convert asciicast frames data to moviepy video clip
	
	Parameters
	----------
	inputData
	    asciicast data in multiple formats
	      * list of strings ->
	          each string is used as asciicast frame json (no header)
	      * list of lists ->
	          inputData[i][0] (float) is used as frame time,
	          inputData[i][-1] (string) is used as frame content
	          for frame i (no header)
	screen : pyte screen object
	    used as emulated terminal screen
	stream : pyte stream object
	    used as emulated terminal input stream
	startFrameTime : float, optional
	    asciicast start time for first frame
	lastFrameDuration : float, optional
	    last frame duration time in seconds
	renderOptions
	    options passed to tty2img
	
	Returns
	-------
	    moviepy video clip
	'''
	clips = []
	last_time = startFrameTime
	for frame in inputData:
		# get frame info
		if isinstance(frame, str):
			frame = json.loads(frame)
		# set previous frame duration
		if len(clips) > 0:
			clips[-1] = clips[-1].set_duration(frame[0]-last_time)
		last_time = frame[0]
		# prepare current frame image clip
		stream.feed(frame[-1])
		image = tty2img.tty2img(screen, **renderOptions)
		imageClip = mpy.ImageClip( numpy.array(image) )
		clips.append(imageClip)
	
	clips[-1] = clips[-1].set_duration(lastFrameDuration)
	return mpy.concatenate_videoclips(clips)

def asciicast2video(
		inputData,
		width = None,
		height = None,
		lastFrameDuration = 3,
		renderOptions = {}
	):
	'''Convert asciicast data to moviepy video clip
	
	Parameters
	----------
	inputData
	    asciicast data in multiple formats
	      * one line string ->
	          path to asciicast file (with first line as header) to open
	      * multiline string ->
	          content of asciicast file (with first line as header)
	      * list of strings ->
	          each string is used as asciicast frame json (no header)
	      * list of lists ->
	          inputData[i][0] (float) is used as frame time,
	          inputData[i][-1] (string) is used as frame content
	          for frame i (no header)
	width : float, optional
	height : float, optional
	    terminal screen width and height,
	    when set used instead of values from asciicast header
	    must be set when inputData don't contain header
	    (is list of string or list of lists)
	lastFrameDuration : float, optional
	    last frame duration time in seconds
	renderOptions
	    options passed to tty2img
	
	Returns
	-------
	    moviepy video clip
	'''
	
	if isinstance(inputData, str):
		if '\n' in inputData:
			inputData = io.StringIO(inputData)
		else:
			inputData = open(inputData, 'r')
	
	# when not set width and height, read its from first line
	if not width or not height:
		if isinstance(inputData, list):
			raise BaseException("when inputData is list width and height must be set in args")
		settings = json.loads(inputData.readline())
		width  = settings['width']
		height = settings['height']
	
	# create VT100 terminal emulator
	screen = pyte.Screen(width, height)
	stream = pyte.Stream(screen)
	
	# render frames
	return render_asciicast_frames(
		inputData, screen, stream, lastFrameDuration=lastFrameDuration, renderOptions=renderOptions
	)

def main():
	import sys
	
	if len(sys.argv) != 3:
		print("USAGE: " + sys.argv[0] + " asciicast_file output_video_file")
		sys.exit(1)
	
	video = asciicast2video(sys.argv[1], renderOptions={'fontSize':19})
	video.write_videofile(sys.argv[2], fps=24)

if __name__ == "__main__":
	main()
