'''
rendering pyte terminal emulator screen as image

Should be imported as a module and contains functions:
  * tty2img - convert pyte screen to PIL image

Requires:
  * PIL (https://pypi.org/project/Pillow/) image library
  * pyte (https://pypi.org/project/pyte/) VTXXX terminal emulator

Copyright © 2020, Robert Ryszard Paciorek <rrp@opcode.eu.org>, MIT licence
'''

from PIL import Image, ImageDraw, ImageFont
import pyte

def tty2img(
		screen,
		fgDefaultColor = '#00ff00',
		bgDefaultColor = 'black',
		fontName            = 'DejaVuSansMono.ttf',
		boldFontName        = 'DejaVuSansMono-Bold.ttf',
		italicsFontName     = 'DejaVuSansMono-Oblique.ttf',
		boldItalicsFontName = 'DejaVuSansMono-BoldOblique.ttf',
		fontSize     = 17,
		lineSpace    = 0,
		marginSize   = 5,
		antialiasing = 0,
		showCursor   = False
	):
	'''Render pyte screen as PIL image
	
	Parameters
	----------
	screen : pyte.Screen
	    with terminal state to render
	fgDefaultColor : str, optional
	    default foreground (e.g. text) color for rendered screen
	bgDefaultColor : str, optional
	    default background color for rendered screen
	fontName : str, optional
	boldFontName : str, optional
	italicsFontName : str, optional
	boldItalicsFontName : str, optional
	    font filepath or filename (in default font location) for:
	        * standard font (fontName)
	        * bold font (boldFontName)
	        * italics font (italicsFontName)
	        * bold+italics font (boldItalicsFontName)
	    should be used monospace font from this same family
	    (for all chars and all font variants char width should be the same)
	fontSize : int, optional
	    font size to use
	lineSpace : int, optional
	    extra space between lines in pixels
	marginSize : int, optional
	    margin size (left = right = top = bottom) for rendered screen
	antialiasing : int, optional
	    antialiasing level, when greater than 1 rendered image
	    will be antialiasing times greater ans scale down
	showCursor
	    when true (and screen.cursor.hidden is false) mark cursor position
	    by reverse foreground background color on it
	
	Returns
	-------
	    PIL.Image
	        with rendered terminal screen
	'''
	
	if antialiasing > 1:
		lineSpace    = lineSpace * antialiasing
		marginSize   = marginSize * antialiasing
		fontSize     = fontSize * antialiasing
	
	# font settings
	normalFont      = ImageFont.truetype(fontName, fontSize)
	boldFont        = ImageFont.truetype(boldFontName, fontSize)
	italicsFont     = ImageFont.truetype(italicsFontName, fontSize)
	boldItalicsFont = ImageFont.truetype(boldItalicsFontName, fontSize)
	
	# calculate single char and image size
	charWidth, _ = normalFont.getsize('X')
	charHeight   = sum(normalFont.getmetrics()) + lineSpace
	imgWidth     = charWidth  * screen.columns + 2*marginSize
	imgHeight    = charHeight * screen.lines + 2*marginSize
	
	# create image object
	image = Image.new('RGBA', (imgWidth, imgHeight), bgDefaultColor)
	draw = ImageDraw.Draw(image)
	
	# cursor settings
	showCursor = showCursor and (not screen.cursor.hidden)
	
	# draw full screen to image
	for line in screen.buffer:
		# process all characters in line
		for char in screen.buffer[line]:
			cData = screen.buffer[line][char]
			point = (char*charWidth + marginSize, line*charHeight + marginSize)
			
			# set colors and draw background
			bgColor = cData.bg if cData.bg != 'default' else bgDefaultColor
			fgColor = cData.fg if cData.fg != 'default' else fgDefaultColor
			
			if cData.reverse:
				bgColor, fgColor = fgColor, bgColor
			
			if showCursor and line == screen.cursor.y and char == screen.cursor.x:
				bgColor, fgColor = fgColor, bgColor
			
			if bgColor != bgDefaultColor:
				draw.rectangle((point, (point[0] + charWidth, point[1] + charHeight)), fill=bgColor)
			
			# set font (bold / italics)
			if cData.bold and cData.italics:
				font = boldItalicsFont
			elif cData.bold:
				font = boldFont
			elif cData.italics:
				font = italicsFont
			else:
				font = normalFont
			
			# draw underscore and strikethrough
			if cData.underscore:
				draw.line(((point[0], point[1] + charHeight-1), (point[0] + charWidth, point[1] + charHeight-1)), fill=fgColor)
				
			if cData.strikethrough:
				draw.line(((point[0], point[1] + charHeight//2), (point[0] + charWidth, point[1] + charHeight//2)), fill=fgColor)
			
			# draw text
			draw.text(point, cData.data, fill=fgColor, font=font)
		
		# draw cursor when it is out of text range
		if showCursor and line == screen.cursor.y and (not screen.cursor.x in screen.buffer[line]):
			point = (screen.cursor.x*charWidth + marginSize, line*charHeight + marginSize)
			draw.rectangle((point, (point[0] + charWidth, point[1] + charHeight)), fill=fgDefaultColor)
	
	# return image
	if antialiasing > 1:
		return image.resize((imgWidth//antialiasing, imgHeight//antialiasing), Image.ANTIALIAS)
	else:
		return image
