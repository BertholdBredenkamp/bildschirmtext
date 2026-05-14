# ETB Benutzer Liste
# Bre 30.03.2026
#
import os
import sys
import json
import time
import re
import pprint

from pathlib import Path
from cept import Cept
from util import Util

PATH_USERS = "../users/"
PATH_STATS = "../stats/"


class ETB_UI:
	def line():
		data_cept = bytearray()
		data_cept.extend(Cept.set_left_g3())
		data_cept.extend(Cept.set_fg_color(15))
		data_cept.extend(Cept.repeat("Q", 40))
		data_cept.extend(Cept.set_fg_color(7))
		data_cept.extend(Cept.set_left_g0())
		return data_cept

	def create_title(title):
		data_cept = bytearray(Cept.set_cursor(2, 1))
		data_cept.extend(Cept.set_palette(1))
		data_cept.extend(Cept.set_screen_bg_color_simple(4))
		data_cept.extend(
			b'\x1b\x28\x40'           # load G0 into G0
			b'\x0f'                   # G0 into left charset
		)
		data_cept.extend(Cept.parallel_mode())
		data_cept.extend(Cept.set_palette(0))
		data_cept.extend(Cept.code_9e())
		data_cept.extend(b'\n\r')
		data_cept.extend(Cept.set_line_bg_color_simple(3))
		data_cept.extend(b'\n')
		data_cept.extend(Cept.set_line_bg_color_simple(3))
		data_cept.extend(Cept.set_palette(1))
		data_cept.extend(Cept.double_height())
		data_cept.extend(b'\r')
		data_cept.extend(Cept.set_fg_color_simple(7))
		data_cept.extend(Cept.from_str(title))
		data_cept.extend(b'\n\r')
		data_cept.extend(Cept.set_palette(0))
		data_cept.extend(Cept.normal_size())
		data_cept.extend(Cept.code_9e())
		data_cept.extend(Cept.set_fg_color_simple(7))
		return data_cept

	def create_title2(title):
		data_cept = bytearray(Cept.set_cursor(2, 1))
		data_cept.extend(Cept.set_palette(1))
		data_cept.extend(Cept.set_screen_bg_color_simple(4))
		data_cept.extend(
			b'\x1b\x28\x40'           # load G0 into G0
			b'\x0f'                   # G0 into left charset
		)
		data_cept.extend(Cept.parallel_mode())
		data_cept.extend(Cept.set_palette(0))
		data_cept.extend(Cept.code_9e())
		data_cept.extend(Cept.set_line_bg_color_simple(4))
		data_cept.extend(b'\n')
		data_cept.extend(Cept.set_line_bg_color_simple(4))
		data_cept.extend(Cept.set_palette(1))
		data_cept.extend(Cept.double_height())
		data_cept.extend(b'\r')
		data_cept.extend(Cept.from_str(title))
		data_cept.extend(b'\n\r')
		data_cept.extend(Cept.set_palette(0))
		data_cept.extend(Cept.normal_size())
		data_cept.extend(Cept.code_9e())
		data_cept.extend(Cept.set_fg_color_simple(7))
		return data_cept

	def footer(left, right):
		data_cept = bytearray()
		data_cept.extend(Cept.set_cursor(23, 1))
		data_cept.extend(Cept.set_palette(0))
		data_cept.extend(Cept.set_line_bg_color_simple(4))
		data_cept.extend(Cept.from_str(left))
		if right:
			data_cept.extend(Cept.set_cursor(23, 41 - len(right)))
			data_cept.extend(Cept.from_str(right))
		return data_cept
#
# Es passen 4 Einträge auf eine Seite
#
	def create_user_list(seite):

# Dateien einlesen
		user_name = []
		user_itelex = []
		user_id = []
		files = [f for f in Path(PATH_USERS).iterdir() if f.is_file()]
		for file in files:
#			sys.stderr.write(" Files: " + pprint.pformat(file.name) + "\n")
# Inhalt in eine Struktur schreiben und nach Namen sortieren
			if file.name != "0-1.user":
				with open(file) as f1:
					user_eintrag = json.load(f1)	
				if user_eintrag.get("last_name") == None:
					user_name.append("")
				else:
					user_name.append(user_eintrag.get("last_name"))
				if user_eintrag.get("itelex") == None:
					user_itelex.append("")
				else:
					user_itelex.append(user_eintrag.get("itelex"))
				file_user_part = file.name.split(".")
				if file_user_part[0] == None:
					user_id.append("")
				else:
					user_id.append(file_user_part[0])

		user_count = len(user_name)
		sys.stderr.write("Bre Anzahl User Daten " + pprint.pformat(user_count) + "\n")

		meta = {
			"publisher_name": "!BTX",
			"include": "a",
			"clear_screen": True,
			"links": {
				"0": "0",
				"#": "3001188" + chr(ord('a') + seite + 1)
			},
			"publisher_color": 7
		}

		sys.stderr.write("Bre ETB Meta 2: " + pprint.pformat(seite) + "\n")

		data_cept = bytearray()
		data_cept.extend(ETB_UI.create_title("BTX Benutzer Liste"))
		data_cept.extend(b"\r\n")
		if user_count > seite * 4 + 0:
			data_cept.extend(Cept.from_str("Name: " + user_name[seite * 4 + 0]))
			data_cept.extend(b"\r\n")
			data_cept.extend(Cept.from_str("Teilnehmernummer: " + user_id[seite * 4 + 0]))
			data_cept.extend(b"\r\n")
			data_cept.extend(Cept.from_str("iTelex: " + user_itelex[seite * 4 + 0]))
			data_cept.extend(b"\r\n")
			data_cept.extend(ETB_UI.line())
		if user_count > seite * 4 + 1:
			data_cept.extend(Cept.from_str("Name: " + user_name[seite * 4 + 1]))
			data_cept.extend(b"\r\n")
			data_cept.extend(Cept.from_str("Teilnehmernummer: " + user_id[seite * 4 + 1]))
			data_cept.extend(b"\r\n")
			data_cept.extend(Cept.from_str("iTelex: " + user_itelex[seite * 4 + 1]))
			data_cept.extend(b"\r\n")
			data_cept.extend(ETB_UI.line())
		if user_count > seite * 4 + 2:
			data_cept.extend(Cept.from_str("Name: " + user_name[seite * 4 + 2]))
			data_cept.extend(b"\r\n")
			data_cept.extend(Cept.from_str("Teilnehmernummer: " + user_id[seite * 4 + 2]))
			data_cept.extend(b"\r\n")
			data_cept.extend(Cept.from_str("iTelex: " + user_itelex[seite * 4 + 2]))
			data_cept.extend(b"\r\n")
			data_cept.extend(ETB_UI.line())
		if user_count > seite * 4 + 3:
			data_cept.extend(Cept.from_str("Name: " + user_name[seite * 4 + 3]))
			data_cept.extend(b"\r\n")
			data_cept.extend(Cept.from_str("Teilnehmernummer: " + user_id[seite * 4 + 3]))
			data_cept.extend(b"\r\n")
			data_cept.extend(Cept.from_str("iTelex: " + user_itelex[seite * 4 + 3]))
			data_cept.extend(b"\r\n")
			data_cept.extend(ETB_UI.line())
		# Sind noch einträge für die nächste Seite vorhanden?
		if (seite + 1) * 4 > user_count:
			data_cept.extend(ETB_UI.footer("0 Zurück", None))
		else:
			data_cept.extend(ETB_UI.footer("0 Zurück", "# Weiter"))

		return (meta, data_cept)
#
	def create_page(pagenumber, basedir):
#		sys.stderr.write("Bre ETB 2 Seite: " + pprint.pformat(pagenumber) + "\n")

		if pagenumber   == "3001188a":
#			sys.stderr.write("Bre ETB 2: " + pprint.pformat(pagenumber) + "\n")
			return ETB_UI.create_user_list(0)
		elif pagenumber == "3001188b":
			return ETB_UI.create_user_list(1)
		elif pagenumber == "3001188c":
			return ETB_UI.create_user_list(2)
		elif pagenumber == "3001188d":
			return ETB_UI.create_user_list(3)


		else:
#			sys.stderr.write("Bre ETB 5: " + pprint.pformat(pagenumber) + "\n")
			return None
