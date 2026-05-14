import sys
import re
import pprint
import urllib.parse
import urllib.request
import feedparser

from bs4 import BeautifulSoup

from cept import Cept
from cept import Cept_page_from_HTML
from cept import Unscii
from util import Util


class RSS_UI:

	feed = None
	html = ""
	page = None
	def create_article_page(sheet_number):
		is_first_page = sheet_number == 0
		sys.stderr.write("Erste Seite " + pprint.pformat(is_first_page) + "\n")

		title = ""
		title1 = "News der Tagesschau"
		RSS_UI.feed = None
		sys.stderr.write("UI.feed " + pprint.pformat(type(RSS_UI.feed)) + "\n")

		if not RSS_UI.feed:
#			RSS_UI.feed = feedparser.parse("https://www.pagetable.com/?feed=rss2")
#			RSS_UI.feed = feedparser.parse("https://rss.sueddeutsche.de/rss/Eilmeldungen")
			RSS_UI.feed = feedparser.parse("https://www.tagesschau.de/index~rss2.xml")
			sys.stderr.write("RSS gelesen\n")

#		entry = RSS_UI.feed["entries"][6]	# 6. Eintrag in der Liste der Beiträge
		sys.stderr.write("Anzahl Einträge : " + pprint.pformat(len(RSS_UI.feed["entries"])) + "\n")
		intAnzahlEintraege = len(RSS_UI.feed["entries"])
		sys.stderr.write("Anzahl Einträge 2 : " + pprint.pformat(intAnzahlEintraege) + "\n")
		try:
			if intAnzahlEintraege > 11 and sheet_number == 0:
				sys.stderr.write("Anzahl Einträge 3 : " + pprint.pformat(intAnzahlEintraege) + "\n")
				intEintrag = 0
				RSS_UI.html = ""
				sys.stderr.write("UI.html Len " + pprint.pformat(len(RSS_UI.html)) + "\n")

				soup = None
				while(intEintrag < 11):
#					sys.stderr.write("Anzahl Einträge 4 : " + pprint.pformat(intEintrag) + "\n")
					entry = RSS_UI.feed["entries"][intEintrag]	# 6. Eintrag in der Liste der Beiträge
					title = entry.title
					RSS_UI.html = RSS_UI.html + "<b>" + title[:39] + "</b>\n" + entry.description + "\n"
#				html = html + RSS_UI.feed["title"][intEintrag]
					RSS_UI.html = RSS_UI.html + "\n.......................................\n"
#				sys.stderr.write("HTML 5: " + pprint.pformat(type(html)) + "\n")
#				html = html + RSS_UI.feed["entries"][intEintrag]
#				html = html + "<br>"
					intEintrag += 1
#				sys.stderr.write("HTML 3: " + pprint.pformat(html) + "\n")
				sys.stderr.write("HTML Laenge: " + pprint.pformat(len(RSS_UI.html)) + "\n")
				soup = BeautifulSoup(RSS_UI.html, 'html.parser')
#		sys.stderr.write(soup)
				RSS_UI.page = None
				sys.stderr.write("UI.page 1: " + pprint.pformat(type(RSS_UI.page)) + "\n")
				sys.stderr.write("UI.page Soup 1: " + pprint.pformat(type(soup)) + "\n")

				RSS_UI.page = Cept_page_from_HTML()
				RSS_UI.page.lines_cept = []

				sys.stderr.write("UI.page 2: " + pprint.pformat(type(RSS_UI.page)) + "\n")

				RSS_UI.page.soup = soup
# Bre				RSS_UI.page.article_prefix = "XXX"
				RSS_UI.page.insert_html_tags(soup.children)
			else:
				sys.stderr.write("HTML 2: " + pprint.pformat(len(RSS_UI.html)) + "\n")
    
#		sys.stderr.write("HTML : " + pprint.pformat(html) + "\n")
# Bre - Auf maximale Seiten begrenzen
#		if (sheet_number < 10):
#			entry = RSS_UI.feed["entries"][sheet_number]
#		sys.stderr.write("RSS Entries" + pprint.pformat(title) + "\n")
#		title = entry.title
#		sys.stderr.write("Titel : " + pprint.pformat(title) + "\n")
#		html = entry.description

		except Exception as err:
			sys.stderr.write("Fehler: " + pprint.pformat(err) + "\n")

		sys.stderr.write("Anzahl Seiten : " +  pprint.pformat(RSS_UI.page.number_of_sheets()) + "\n")

		meta = {
			"clear_screen": True,
			"links": {
				"0": "0",
                                "8": "6502"
			},
			"publisher_color": 0
		}
		meta["clear_screen"] = is_first_page

#		data_cept = None
		data_cept = bytearray()
		data_cept.extend(Cept.parallel_mode())
		sys.stderr.write("Sheet2: " + pprint.pformat(sheet_number) + "\n")
# Bre Immer Kopf ausgeben ??
		if is_first_page:
#		if 1 == 1:

			data_cept.extend(Cept.set_screen_bg_color(7))
			data_cept.extend(Cept.set_cursor(2, 1))
			data_cept.extend(Cept.set_line_bg_color(0))
			data_cept.extend(b'\n')
			data_cept.extend(Cept.set_line_bg_color(0))
			data_cept.extend(Cept.double_height())
			data_cept.extend(Cept.set_fg_color(7))
			data_cept.extend(Cept.from_str(title1[:39]))
			data_cept.extend(b'\r\n')
			data_cept.extend(Cept.normal_size())
			data_cept.extend(b'\n')

		# print navigation
		# * on sheet 0, so we don't have to print it again on later sheets
		# * on the last sheet, because it doesn't show the "#" text
		# * on the second last sheet, because navigating back from the last one needs to show "#" again

		try:

			sys.stderr.write("Sheet12: " + pprint.pformat(sheet_number) + "\n")

			if sheet_number == 0 or sheet_number >= RSS_UI.page.number_of_sheets() - 2:
#			if 1 == 1:
				sys.stderr.write("Sheet10: " + pprint.pformat(sheet_number) + "\n")
				data_cept.extend(Cept.set_cursor(23, 1))
				data_cept.extend(Cept.set_line_bg_color(0))
				data_cept.extend(Cept.set_fg_color(7))
				data_cept.extend(Cept.from_str("0 < Back"))
				s = "# > Next"
				data_cept.extend(Cept.set_cursor(23, 41 - len(s)))
				if sheet_number >= RSS_UI.page.number_of_sheets() - 1:
					data_cept.extend(Cept.repeat(" ", len(s)))
				else:
					data_cept.extend(Cept.from_str(s))

			data_cept.extend(Cept.set_cursor(5, 1))

		# add text
			sys.stderr.write("Sheet 11: " + pprint.pformat(sheet_number) + "\n")
			if sheet_number > RSS_UI.page.number_of_sheets() - 2:
	    			sys.stderr.write("Sheet 13: " + pprint.pformat(sheet_number) + "\n")
			else:
				data_cept.extend(RSS_UI.page.cept_for_sheet(sheet_number))

		except Exception as err:
			sys.stderr.write("Fehler 2: " + pprint.pformat(err) + "\n")

		sys.stderr.write("Meta: " + pprint.pformat(meta) + "\n")


		return (meta, data_cept)

	def create_page(pageid, basedir):
		if pageid.startswith("6502"):
			sys.stderr.write("Page ID: " + pprint.pformat(pageid) + "\n")
			sys.stderr.write("BaseDir: " + pprint.pformat(basedir) + "\n")

			sys.stderr.write("Sheet1 Nr: " + pprint.pformat(ord(pageid[-1])) + "\n")

			return RSS_UI.create_article_page(ord(pageid[-1]) - ord("a"))

		else:
			return None


