# SUCHE Stichwort Liste
# Bre 13.05.2026
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
import sqlite3
from typing import Optional, Union

class SUCHE_STICHWORT_DB:
    
    def search_index_by_keyword(
        db_path: str, table_name: str, column_name: str, keyword: str
        ) -> Optional[Union[int, str]]:
        """
        Sucht ein Stichwort in einer SQLite-Datenbank und gibt den Index (rowid/id) zurück.
        Abfrage auf max 8 Zeilen begrenzt

        Args:
            db_path: Pfad zur SQLite-Datenbankdatei.
            table_name: Name der Tabelle.
            column_name: Name der Spalte, in der gesucht wird.
            keyword: Das zu suchende Stichwort.

        Returns:
            Die Ergebnisliste oder None, falls nichts gefunden wurde.
        """
        try:
            # Verbindung zur Datenbank herstellen
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # SQL-Query mit Platzhalter (?) gegen SQL-Injection
            # Wir suchen nach der btx_nr
            query = f"SELECT suchtext, btx_nr FROM {table_name} WHERE {column_name} LIKE ?"
            
            # 'LIKE' ermöglicht Teilsuche. Für exakte Suche '=' verwenden.
            # '%?%' bedeutet, dass das Stichwort irgendwo im Text vorkommen kann.
            cursor.execute(query, (f"%{keyword}%",))
            result = cursor.fetchmany(8)

            conn.close()
            if len(result) > 0:
                return result
            else:
                return None

        except sqlite3.Error as e:
            print(f"Datenbankfehler: {e}")
            return None

#     

class SUCHE_STICHWORT_UI:
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
# Es werden maximal 16 Zeilen angezeigt
#
	def create_liste_suche_stichwort(found_pageids):

		sys.stderr.write("Bre Anzahl User Daten " + pprint.pformat(len(found_pageids)) + "\n")

		links = {
		    "0": "0",
		}
		i = 10
		for row in found_pageids:
			links[str(i + 1)] = row[1]
			i +=1
		

		meta = {
			"publisher_name": "!BTX",
			"clear_screen": True,
			"links": links,
			"publisher_color": 7
		}

#		sys.stderr.write("Bre Suche Meta 2: " + pprint.pformat(seite) + "\n")

		data_cept = bytearray()
		data_cept.extend(SUCHE_STICHWORT_UI.create_title("Stichworte gefunden"))
		data_cept.extend(b"\r\n")
		intZaehler = 1
		for row in found_pageids:
			sys.stderr.write("Bre Suche Anzahl User Daten " + pprint.pformat(row) + "\n")
			zeile = row[0].ljust(25, ".")
			zeile = zeile + " *" + row[1] + "#"
			zeilenlaenge = len(zeile) + 2
			zeile = zeile + " ".ljust(40 - zeilenlaenge,".")
			zeile = zeile + str(10 + intZaehler)
			data_cept.extend(Cept.from_str(zeile + "\n"))
			intZaehler += 1

		data_cept.extend(SUCHE_STICHWORT_UI.footer("0 Zurück", None))

		return (meta, data_cept)
#
	def create_page(found_pageids):
		sys.stderr.write("Bre Suche 3 Länge: " + pprint.pformat(len(found_pageids)) + "\n")

		return SUCHE_STICHWORT_UI.create_liste_suche_stichwort(found_pageids)
