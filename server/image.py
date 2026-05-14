from PIL import Image
import pprint
import math
import sys
from cept import Cept
import urllib.request

PIXEL_ASPECT_RATIO = 0.92
#PIXEL_ASPECT_RATIO = 0.80

class Image_UI:
	palette = None
	drcs = None
	chars = None

	def compress(drcs_block):
		if drcs_block == bytearray(b'@@@@@@@@@@'):
			drcs_block = bytearray(b'\x20')
		elif drcs_block == bytearray(b'\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f'):
			drcs_block = bytearray(b'\x2f')
		else:
			y1 = 0
			max = 10
			while True:
				l = 0
				for y2 in range(y1 + 1, max):
					if drcs_block[y2] != drcs_block[y1]:
						break
					l += 1
				if l:
					drcs_block = drcs_block[:y1 + 1] + bytes([0x20 + l]) + drcs_block[y1 + l + 1:]
					y1 += 1
					max -= l - 1
				y1 += 1
				if y1 == max:
					break
		return drcs_block

	def __init__(self, url, colors = 16, drcs_start = 0x21):
		if url is None:
			return None
		sys.stderr.write("URL: " + pprint.pformat(url) + "\n")
		if url.startswith("http://") or url.startswith("https://"):
			image = Image.open(urllib.request.urlopen(url))
		else:
			image = Image.open(url)
		image.load()
		(width, height) = image.size
		sys.stderr.write("mode: " + image.mode + ", resolution: " + str(width) + "*" + str(height) + "\n")

		is_grayscale = image.mode == "L" or image.mode == "LA"

		# 4 shades of gray instead of 16, but double resolution
		# disabled, PIL doesn't select good base colors
#		if is_grayscale:
#			colors = 4
		# TODO: calling ImageMagick might give better results:
		# e.g. $ convert in.jpg -resize 54x80\! -dither FloydSteinberg -colors 16 out.png

		sys.stderr.write("target colors: " + str(colors) + "\n")

		num_drcs = 0x7f - drcs_start
		if colors == 16:
			num_drcs = int(num_drcs / 2)

		# calculate character resolution
		exact_res_x = math.sqrt(num_drcs * width / height)
		exact_res_y = math.sqrt(num_drcs * height / width)
		aspect_ratio = width / height / PIXEL_ASPECT_RATIO

#		sys.stderr.write("exact char resolution: " + str(exact_res_x) + "*" + str(exact_res_y) + "\n")

		res_x_1 = math.floor(exact_res_x)
		res_y_1 = math.floor(num_drcs / res_x_1)
		error_1 = abs(1 - (aspect_ratio / (res_x_1 / res_y_1)))
		res_x_2 = math.ceil(exact_res_x)
		res_y_2 = math.floor(num_drcs / res_x_2)
		error_2 = abs(1 - (aspect_ratio / (res_x_2 / res_y_2)))
		res_y_3 = math.floor(exact_res_y)
		res_x_3 = math.floor(num_drcs / res_y_3)
		error_3 = abs(1 - (aspect_ratio / (res_x_3 / res_y_3)))
		res_y_4 = math.ceil(exact_res_y)
		res_x_4 = math.floor(num_drcs / res_y_4)
		error_4 = abs(1 - (aspect_ratio / (res_x_4 / res_y_4)))

#		sys.stderr.write("char resolution 1: " + str(res_x_1) + "*" + str(res_y_1) + ", error: " + str(error_1) + "\n")
#		sys.stderr.write("char resolution 2: " + str(res_x_2) + "*" + str(res_y_2) + ", error: " + str(error_2) + "\n")
#		sys.stderr.write("char resolution 3: " + str(res_x_3) + "*" + str(res_y_3) + ", error: " + str(error_3) + "\n")
#		sys.stderr.write("char resolution 4: " + str(res_x_4) + "*" + str(res_y_4) + ", error: " + str(error_4) + "\n")

		res_x = res_x_1
		res_y = res_y_1
		error = error_1
		if error_2 < error:
			res_x = res_x_2
			res_y = res_y_2
			error = error_2
		if error_3 < error:
			res_x = res_x_3
			res_y = res_y_3
			error = error_3
		if error_4 < error:
			res_x = res_x_4
			res_y = res_y_4
			error = error_4

		sys.stderr.write("char resolution:   " + str(res_x) + "*" + str(res_y) + ", error: " + str(error) + "\n")

		# remove alpha
		if image.mode == "RGBA" or image.mode == "LA":
			background = Image.new("RGB", image.size, (255, 255, 255))
			index = 3 if image.mode == "RGBA" else 1
			background.paste(image, mask=image.split()[index])
			image = background

		# resample
		image = image.resize((res_x * 6, res_y * 10), resample = Image.ANTIALIAS)

		# convert to custom colors
		image = image.quantize(colors = colors, method = 0)
#		image = image.convert(mode = "P", colors = colors, dither = Image.FLOYDSTEINBERG, palette = Image.ADAPTIVE)

		image.save("/tmp/x.png")

		# create array with palette
		p = image.getpalette()
		self.palette = []
		for i in range(0, colors):
			r = p[i * 3]
			g = p[i * 3 + 1]
			b = p[i * 3 + 2]
			self.palette.append("#{:02x}{:02x}{:02x}".format(r,g,b))

#		sys.stderr.write("self.palette: " + pprint.pformat(self.palette) + "\n")

		# create drcs
		self.drcs = bytearray()

		if colors == 4:
			num_bits = 2
		elif colors == 16:
			num_bits = 4

		for base_y in range(0, res_y * 10, 10):
			for base_x in range(0, res_x * 6, 6):
				for bitno in range(0, num_bits):
					self.drcs.extend([0x30 + bitno])
					drcs_block = bytearray()
					for y in range(0, 10):
						byte = 0
						for x in range(0, 6):
							byte <<= 1
							byte |= (image.getpixel((base_x + x, base_y + y)) >> bitno) & 1
						byte |= 0x40
						drcs_block.append(byte)

					# compression
					drcs_block = Image_UI.compress(drcs_block)

#					sys.stderr.write("drcs_block: " + pprint.pformat(drcs_block) + "\n")
					self.drcs.extend(drcs_block)

		sys.stderr.write("DRCs compressed " + str(40 * res_x * res_y) + " down to " + str(len(self.drcs)) + "\n")

		drcs_header = bytearray()
		if colors == 4:
			drcs_header.extend(b'\x1f\x23\x20\x4b\x42') # start defining 6x10 @ 4c
		elif colors == 16:
			drcs_header.extend(b'\x1f\x23\x20\x4b\x44') # start defining 6x10 @ 16c
		else:
			error()
		drcs_header.extend([0x1f, 0x23, drcs_start])

		# prepend
		self.drcs[0:0] = drcs_header

		# append
		if colors == 4:
			# set colors to 16, 17, 18, 19
			self.drcs.extend(b'\x1f\x26\x20\x22\x20\x35\x40')
			self.drcs.extend(b'\x1f\x26\x30\x50')
			self.drcs.extend(b'\x1f\x26\x31\x51')
			self.drcs.extend(b'\x1f\x26\x32\x52')
			self.drcs.extend(b'\x1f\x26\x33\x53')

		# create characters to print
		if colors == 16:
			step = 2
		else:
			step = 1
		self.chars = []
		for y in range(0, res_y):
			l = bytearray()
			for x in range(0, res_x):
				l.append(drcs_start + (y * res_x + x) * step)
			self.chars.append(l)


	def create_cept_from_image(filename):
		colors = 16
		drcs_start = 0x21
		if filename is None:
			return None
		sys.stderr.write("Filename 2: " + pprint.pformat(filename) + "\n")
#		if :
		image = Image.open(filename)
#		else:
#			image = Image.open(url)
		image.load()
		(width, height) = image.size
		sys.stderr.write("mode: " + image.mode + ", resolution: " + str(width) + "*" + str(height) + "\n")

		is_grayscale = image.mode == "L" or image.mode == "LA"

		# 4 shades of gray instead of 16, but double resolution
		# disabled, PIL doesn't select good base colors
#		if is_grayscale:
#			colors = 4
		# TODO: calling ImageMagick might give better results:
		# e.g. $ convert in.jpg -resize 54x80\! -dither FloydSteinberg -colors 16 out.png

		sys.stderr.write("target colors: " + str(colors) + "\n")

		num_drcs = 0x7f - drcs_start
		if colors == 16:
			num_drcs = int(num_drcs / 2)

		# calculate character resolution
		exact_res_x = math.sqrt(num_drcs * width / height)
		exact_res_y = math.sqrt(num_drcs * height / width)
		aspect_ratio = width / height / PIXEL_ASPECT_RATIO

#		sys.stderr.write("exact char resolution: " + str(exact_res_x) + "*" + str(exact_res_y) + "\n")

		res_x_1 = math.floor(exact_res_x)
		res_y_1 = math.floor(num_drcs / res_x_1)
		error_1 = abs(1 - (aspect_ratio / (res_x_1 / res_y_1)))
		res_x_2 = math.ceil(exact_res_x)
		res_y_2 = math.floor(num_drcs / res_x_2)
		error_2 = abs(1 - (aspect_ratio / (res_x_2 / res_y_2)))
		res_y_3 = math.floor(exact_res_y)
		res_x_3 = math.floor(num_drcs / res_y_3)
		error_3 = abs(1 - (aspect_ratio / (res_x_3 / res_y_3)))
		res_y_4 = math.ceil(exact_res_y)
		res_x_4 = math.floor(num_drcs / res_y_4)
		error_4 = abs(1 - (aspect_ratio / (res_x_4 / res_y_4)))

#		sys.stderr.write("char resolution 1: " + str(res_x_1) + "*" + str(res_y_1) + ", error: " + str(error_1) + "\n")
#		sys.stderr.write("char resolution 2: " + str(res_x_2) + "*" + str(res_y_2) + ", error: " + str(error_2) + "\n")
#		sys.stderr.write("char resolution 3: " + str(res_x_3) + "*" + str(res_y_3) + ", error: " + str(error_3) + "\n")
#		sys.stderr.write("char resolution 4: " + str(res_x_4) + "*" + str(res_y_4) + ", error: " + str(error_4) + "\n")

		res_x = res_x_1
		res_y = res_y_1
		error = error_1
		if error_2 < error:
			res_x = res_x_2
			res_y = res_y_2
			error = error_2
		if error_3 < error:
			res_x = res_x_3
			res_y = res_y_3
			error = error_3
		if error_4 < error:
			res_x = res_x_4
			res_y = res_y_4
			error = error_4

		sys.stderr.write("char resolution:   " + str(res_x) + "*" + str(res_y) + ", error: " + str(error) + "\n")

		# remove alpha
		if image.mode == "RGBA" or image.mode == "LA":
			background = Image.new("RGB", image.size, (255, 255, 255))
			index = 3 if image.mode == "RGBA" else 1
			background.paste(image, mask=image.split()[index])
			image = background

		# resample
		image = image.resize((res_x * 6, res_y * 10), resample = Image.ANTIALIAS)

		# convert to custom colors
		image = image.quantize(colors = colors, method = 0)
#		image = image.convert(mode = "P", colors = colors, dither = Image.FLOYDSTEINBERG, palette = Image.ADAPTIVE)

		image.save("/tmp/x.png")

		# create array with palette
		p = image.getpalette()
		palette = []
		for i in range(0, colors):
			r = p[i * 3]
			g = p[i * 3 + 1]
			b = p[i * 3 + 2]
			palette.append("#{:02x}{:02x}{:02x}".format(r,g,b))

#		sys.stderr.write("self.palette: " + pprint.pformat(self.palette) + "\n")

		# create drcs
		drcs = bytearray()

		if colors == 4:
			num_bits = 2
		elif colors == 16:
			num_bits = 4

		for base_y in range(0, res_y * 10, 10):
			for base_x in range(0, res_x * 6, 6):
				for bitno in range(0, num_bits):
					drcs.extend([0x30 + bitno])
					drcs_block = bytearray()
					for y in range(0, 10):
						byte = 0
						for x in range(0, 6):
							byte <<= 1
							byte |= (image.getpixel((base_x + x, base_y + y)) >> bitno) & 1
						byte |= 0x40
						drcs_block.append(byte)

					# compression
					drcs_block = Image_UI.compress(drcs_block)

#					sys.stderr.write("drcs_block: " + pprint.pformat(drcs_block) + "\n")
					drcs.extend(drcs_block)

		sys.stderr.write("DRCs compressed " + str(40 * res_x * res_y) + " down to " + str(len(drcs)) + "\n")

		drcs_header = bytearray()
		if colors == 4:
			drcs_header.extend(b'\x1f\x23\x20\x4b\x42') # start defining 6x10 @ 4c
		elif colors == 16:
			drcs_header.extend(b'\x1f\x23\x20\x4b\x44') # start defining 6x10 @ 16c
		else:
			error()
		drcs_header.extend([0x1f, 0x23, drcs_start])

		# prepend
		drcs[0:0] = drcs_header

		# append
		if colors == 4:
			# set colors to 16, 17, 18, 19
			drcs.extend(b'\x1f\x26\x20\x22\x20\x35\x40')
			drcs.extend(b'\x1f\x26\x30\x50')
			drcs.extend(b'\x1f\x26\x31\x51')
			drcs.extend(b'\x1f\x26\x32\x52')
			drcs.extend(b'\x1f\x26\x33\x53')

		# create characters to print
		if colors == 16:
			step = 2
		else:
			step = 1
		chars = []
		for y in range(0, res_y):
			l = bytearray()
			for x in range(0, res_x):
				l.append(drcs_start + (y * res_x + x) * step)
			chars.append(l)
		return palette, drcs, chars







	def create_image_page():
#		filename = "/Users/mist/Desktop/RGB_24bits_palette_sample_image.jpg"
#		filename = "/Users/mist/Desktop/Lenna_(test_image).png"
#		filename = "/Users/mist/Desktop/Wikipedia_logo_593.jpg"
#		filename = "/Users/mist/Desktop/220px-C64c_system.jpg"
#		filename = "/home/bb/bildschirmtext/FuBK-Testbild.png"
#		filename = "/home/bb/bildschirmtext/Nixdorf_Logo.png"
		filename = "/home/bb/bildschirmtext/HNF_Logo.png"


		sys.stderr.write("Dateiname:  " + pprint.pformat(filename) + "\n")
		try:
			(palette, drcs, chars) = Image_UI.create_cept_from_image(filename)
		except Exception as err:
			sys.stderr.write("Fehler:  " + pprint.pformat(err) + "\n")
			
		data_cept = bytearray()
		data_cept.extend(Cept.define_palette(palette))
		data_cept.extend(drcs)
		data_cept.extend(Cept.parallel_mode())
		data_cept.extend(Cept.set_cursor(2, 1))
		data_cept.extend(Cept.set_screen_bg_color(6))
		data_cept.extend(Cept.set_line_bg_color_simple(4))
		data_cept.extend(Cept.set_palette(0))
#		data_cept.extend(Cept.from_str("Berthold's Test Oben Zeile 3"))
#		data_cept.extend(b'\n\r')
		data_cept.extend(Cept.set_line_bg_color_simple(4))
		data_cept.extend(Cept.set_cursor(3, 1))
		data_cept.extend(Cept.set_line_bg_color_simple(4))

		data_cept.extend(Cept.set_cursor(2, 1))
		data_cept.extend(Cept.double_height())
		data_cept.extend(b'\r')
		data_cept.extend(Cept.from_str("Berthold's Test Oben Zeile 4"))
#		data_cept.extend(b'\n\r')
#		data_cept.extend(Cept.from_str("Berthold's Test Oben Zeile 5"))
		data_cept.extend(Cept.set_cursor(4, 1))
		data_cept.extend(Cept.normal_size())
		data_cept.extend(Cept.set_palette(1))
		data_cept.extend(Cept.set_line_bg_color_simple(4))
		data_cept.extend(Cept.set_cursor(4, 1))
		data_cept.extend(Cept.from_str("Zeile 5"))
		data_cept.extend(b'\n\r')
		data_cept.extend(Cept.set_line_bg_color_simple(2))
		data_cept.extend(Cept.from_str("Zeile 6"))
#		data_cept.extend(Cept.set_line_bg_color_simple(4))
		data_cept.extend(b'\n\r')

		data_cept.extend(Cept.set_palette(0))


		data_cept.extend(Cept.set_cursor(7, 1))
		data_cept.extend(Cept.load_g0_drcs())
		for l in chars:
			data_cept.extend(l)
			data_cept.extend(b'\r\n')
		data_cept.extend(b'\x1b\x28\x40\x0f')
		data_cept.extend(Cept.set_palette(0))
		data_cept.extend(Cept.set_cursor(14, 1))
		data_cept.extend(Cept.set_line_bg_color_simple(0))
#		data_cept.extend(Cept.set_palette(0))
		data_cept.extend(Cept.from_str("Berthold's Test Hintergrund 0 schwarz"))
		data_cept.extend(b'\n\r')

		data_cept.extend(Cept.set_line_bg_color_simple(1))
		data_cept.extend(Cept.set_fg_color_simple(3))
		data_cept.extend(Cept.set_cursor(15, 1))

		data_cept.extend(Cept.from_str("Berthold's Test FG 3 Hintergrund 1 rot"))
		data_cept.extend(b'\n\r')

		data_cept.extend(Cept.set_line_bg_color_simple(2))
#		data_cept.extend(Cept.set_palette(0))
		data_cept.extend(Cept.from_str("Berthold's Test Hintergrund 2 grün"))
		data_cept.extend(b'\n\r')
		data_cept.extend(Cept.set_line_bg_color_simple(3))
#		data_cept.extend(Cept.set_palette(3))
		data_cept.extend(Cept.from_str("Berthold's Test Hintergrund 3 gelb"))
		data_cept.extend(b'\n\r')
		data_cept.extend(Cept.set_line_bg_color_simple(4))
#		data_cept.extend(Cept.set_palette(3))
		data_cept.extend(Cept.from_str("Berthold's Test Hintergrund 4 blau"))
		data_cept.extend(b'\n\r')
		data_cept.extend(Cept.set_line_bg_color_simple(5))
#		data_cept.extend(Cept.set_palette(4))
		data_cept.extend(Cept.from_str("Berthold's Test Hintergrund 5 magenta"))
		data_cept.extend(b'\n\r')
		data_cept.extend(Cept.set_line_bg_color_simple(6))
#		data_cept.extend(Cept.set_palette(4))
		data_cept.extend(Cept.from_str("Berthold's Test Hintergrund 6 hellblau"))
		data_cept.extend(b'\n\r')
		data_cept.extend(Cept.set_line_bg_color_simple(7))
		data_cept.extend(Cept.set_fg_color_simple(0))
#		data_cept.extend(Cept.set_palette(4))
		data_cept.extend(Cept.set_cursor(21, 1))
		data_cept.extend(Cept.from_str("Berthold's Test FG 0 Hintergrund 7 weiss"))

		data_cept.extend(Cept.set_cursor(23, 1))
		data_cept.extend(Cept.from_str("0 - Übersicht"))


		meta = {
			"clear_screen": True,
			"links": {
				"0": "0"
			},
			"publisher_name": "!BTX",
			"publisher_color": 3
		}

		return (meta, data_cept)

	def create_page(pageid):
		if pageid == "666a":
			return Image_UI.create_image_page()
		else:
			return None
