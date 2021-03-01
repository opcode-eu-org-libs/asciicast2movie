'''
rendering pyte terminal emulator screen as image

Should be imported as a module and contains functions:
  * tty2img - convert pyte screen to PIL image

Requires:
  * PIL (https://pypi.org/project/Pillow/) image library
  * pyte (https://pypi.org/project/pyte/) VTXXX terminal emulator
  * fclist (https://pypi.org/project/fclist-cffi/) fontconfig wrapper
    (optional, for support fallback fonts)
  * freetype (https://pypi.org/project/freetype-py/) freetype wrapper
    (optional, for support fallback fonts)

Copyright © 2020-2021, Robert Ryszard Paciorek <rrp@opcode.eu.org>,
                       MIT licence
'''

from PIL import Image, ImageDraw, ImageFont, ImageColor
import pyte

try:
  import fclist
  import freetype
except ModuleNotFoundError:
  freetype = None

def tty2img(
		screen,
		fgDefaultColor = '#00ff00',
		bgDefaultColor = 'black',
		fontName            = 'DejaVuSansMono.ttf',
		boldFontName        = 'DejaVuSansMono-Bold.ttf',
		italicsFontName     = 'DejaVuSansMono-Oblique.ttf',
		boldItalicsFontName = 'DejaVuSansMono-BoldOblique.ttf',
		fallbackFonts       = ['DroidSansFallback', 'Symbola'],
		fontSize     = 17,
		lineSpace    = 0,
		marginSize   = 5,
		antialiasing = 0,
		showCursor   = False,
		logFunction  = None
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
	fallbackFonts : list of strings
	    fonts families to use when normal font don't have glyph for
	    rendered character (require fclist module)
	fontSize : int, optional
	    font size to use
	lineSpace : int, optional
	    extra space between lines in pixels
	marginSize : int, optional
	    margin size (left = right = top = bottom) for rendered screen
	antialiasing : int, optional
	    antialiasing level, when greater than 1 rendered image
	    will be antialiasing times greater ans scale down
	showCursor : bool, optional
	    when true (and screen.cursor.hidden is false) mark cursor position
	    by reverse foreground background color on it
	logFunction : function
	    function used to print some info and warnings,
	    e.g. set to print for printing to stdout
	
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
	normalFont      = [ ImageFont.truetype(fontName, fontSize), None ]
	boldFont        = [ ImageFont.truetype(boldFontName, fontSize), None ]
	italicsFont     = [ ImageFont.truetype(italicsFontName, fontSize), None ]
	boldItalicsFont = [ ImageFont.truetype(boldItalicsFontName, fontSize), None ]
	
	if freetype:
		normalFont[1]      = freetype.Face(normalFont[0].path)
		boldFont[1]        = freetype.Face(boldFont[0].path)
		italicsFont[1]     = freetype.Face(italicsFont[0].path)
		boldItalicsFont[1] = freetype.Face(boldItalicsFont[0].path)
	
	# calculate single char and image size
	charWidth, _ = normalFont[0].getsize('X')
	charHeight   = sum(normalFont[0].getmetrics()) + lineSpace
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
		point = [marginSize, line*charHeight + marginSize]
		for char in screen.buffer[line]:
			cData = screen.buffer[line][char]
			
			# check for empty char (bug in pyte?)
			if cData.data == "":
				continue
			
			# set colors and draw background
			bgColor = cData.bg if cData.bg != 'default' else bgDefaultColor
			fgColor = cData.fg if cData.fg != 'default' else fgDefaultColor
			
			if cData.reverse:
				bgColor, fgColor = fgColor, bgColor
			
			if showCursor and line == screen.cursor.y and char == screen.cursor.x:
				bgColor, fgColor = fgColor, bgColor
			
			bgColor = _convertColor(bgColor)
			fgColor = _convertColor(fgColor)
			
			if bgColor != bgDefaultColor:
				draw.rectangle( ((point[0], point[1]), (point[0] + charWidth, point[1] + charHeight)), fill=bgColor )
			
			# set font (bold / italics)
			if cData.bold and cData.italics:
				font = boldItalicsFont
			elif cData.bold:
				font = boldFont
			elif cData.italics:
				font = italicsFont
			else:
				font = normalFont
			
			# does font have this char?
			extraWidth = 0
			if freetype and not font[1].get_char_index(cData.data):
				foundFont = False
				for fname in fallbackFonts:
					for ff in fclist.fclist(family=fname, charset=hex(ord(cData.data))):
						foundFont = True
						font = [ ImageFont.truetype(ff.file, fontSize), None ]
						extraWidth = max(0, font[0].getsize(cData.data)[0] - charWidth)
						break
					if foundFont:
						break
				else:
					if logFunction:
						logFunction("Missing glyph for " + hex(ord(cData.data)) + " Unicode symbols (" + cData.data + ")")
			
			# draw underscore and strikethrough
			if cData.underscore:
				draw.line(((point[0], point[1] + charHeight-1), (point[0] + charWidth, point[1] + charHeight-1)), fill=fgColor)
				
			if cData.strikethrough:
				draw.line(((point[0], point[1] + charHeight//2), (point[0] + charWidth, point[1] + charHeight//2)), fill=fgColor)
			
			# draw text
			draw.text(point, cData.data, fill=fgColor, font=font[0])
			
			# update next char position
			point[0] += charWidth + extraWidth
		
		# draw cursor when it is out of text range
		if showCursor and line == screen.cursor.y and (not screen.cursor.x in screen.buffer[line]):
			point[0] += (screen.cursor.x - char - 1) * charWidth
			draw.rectangle( ((point[0], point[1]), (point[0] + charWidth, point[1] + charHeight)), fill=fgDefaultColor )
	
	# return image
	if antialiasing > 1:
		return image.resize((imgWidth//antialiasing, imgHeight//antialiasing), Image.ANTIALIAS)
	else:
		return image

def _convertColor(color):
	if color[0] != "#" and not color in ImageColor.colormap:
		return "#" + color
	return color
