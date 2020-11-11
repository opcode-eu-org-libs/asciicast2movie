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
		blinkingCursor = None,
		lastFrameDuration = 3,
		renderOptions = {}
	):
	'''Convert asciicast frames data to moviepy video clip
	
	Parameters
	----------
	inputData : list of lists
	    asciicast data:
	        inputData[i][0] (float) is used as frame time,
	        inputData[i][-1] (string) is used as frame content
	        for frame i (no header)
	screen : pyte screen object
	    used as emulated terminal screen
	stream : pyte stream object
	    used as emulated terminal input stream
	blinkingCursor : float, optional
	    when set show blinking cursor with period = 2 * this value
	lastFrameDuration : float, optional
	    last frame duration time in seconds
	renderOptions : dict, optional
	    options passed to tty2img
	
	Returns
	-------
	    moviepy video clip
	'''
	clips = []
	nextFrameStartTimes = list( zip(*inputData[1:], [ inputData[-1][0] + lastFrameDuration ]) )[0]
	for frame, endTime in zip(inputData, nextFrameStartTimes):
		startTime = frame[0]
		cursorOptions, cursor = {}, 0
		
		# prepare current frame image clips
		stream.feed(frame[-1])
		while startTime < endTime:
			# blinking cursor support
			if blinkingCursor and (not screen.cursor.hidden):
				if cursor == 0:
					duration  = blinkingCursor/2
				else:
					duration  = blinkingCursor
				startTime += duration
				if cursor%2 == 0:
					cursorOptions = {'showCursor': True}
				else:
					cursorOptions = {'showCursor': False}
				cursor += 1
			else:
				duration  = endTime-startTime
				startTime = endTime
			# subframe rendering
			image = tty2img.tty2img(screen, **renderOptions, **cursorOptions)
			imageClip = mpy.ImageClip( numpy.array(image) ).set_duration( duration )
			clips.append(imageClip)
	
	return mpy.concatenate_videoclips(clips)

def asciicast2video(
		inputData,
		width = None,
		height = None,
		blinkingCursor = None,
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
	blinkingCursor : float, optional
	    when set show blinking cursor with period = 2 * this value
	lastFrameDuration : float, optional
	    last frame duration time in seconds
	renderOptions : dict, optional
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
	
	# convert input to list of list
	inputFrames = []
	for frame in inputData:
		if isinstance(frame, str):
			frame = json.loads(frame)
		inputFrames.append( (frame[0], frame[-1]) )
	
	# render frames
	return render_asciicast_frames(
		inputFrames, screen, stream, blinkingCursor, lastFrameDuration, renderOptions
	)

def main():
	import sys
	
	if len(sys.argv) != 3:
		print("USAGE: " + sys.argv[0] + " asciicast_file output_video_file")
		sys.exit(1)
	
	video = asciicast2video(sys.argv[1], blinkingCursor=0.5, renderOptions={'fontSize':19})
	video.write_videofile(sys.argv[2], fps=24)

if __name__ == "__main__":
	main()
