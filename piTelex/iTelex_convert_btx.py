import json
import sys
import os
import glob
import time
#from usr import User

PATH_MESSAGES = "/home/bb/bildschirmtext/messages/"
PATH_OUTPUT = "/home/bb/piTelex/BTX/Output/"
PATH_ARCHIVE = "/home/bb/piTelex/archive/"
PATH_BTX_ARCHIVE = "/home/bb/piTelex/BTX/Archive/"


def parse_json_file_to_lines(filename):
    """
    Liest eine JSON-Datei Zeile für Zeile ein und gibt jedes gültige JSON-Objekt
    als formatierten String auf einer neuen Zeile aus.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Entferne führende/nachfolgende Leerzeichen und Zeilenumbrüche
                stripped_line = line.strip()
                if not stripped_line:
                    continue # Leere Zeilen überspringen

                try:
                    # Versuche, die Zeile als JSON zu parsen
                    json_object = json.loads(stripped_line)
                    
                    # Gib das geparste Objekt als gut lesbaren JSON-String aus
                    # indent=4 macht es formatiert und leichter lesbar
                    formatted_json = json.dumps(json_object, indent=4, ensure_ascii=False)
                    print(f"--- Zeile {line_num} ---")
                    print(formatted_json)

		    # 
                    f = open(filename, 'r')
                    dict = json.load(f)
                    m = dict["messages"][0]

                    nachricht = m['body']
                    from_user = m["from_user_id"]
	
                    print(type(nachricht))
                    trennzeichen_index = nachricht.find('=')
                    iTelex_To = "itelex_to:" + nachricht[:trennzeichen_index]
                    iTelex_From = "btx_from:" + m["from_user_id"]
                    iTelex_Text = nachricht[trennzeichen_index+1:]
                
                    file = open('/home/bb/piTelex/BTX/Input/iTelex_20260121.txt', 'w')
                    print(file.write(iTelex_From + "\r\n" + iTelex_To + "\r\n" + iTelex_Text))
                    file.close()


                    print(" - Datei einlesen: ")
#                    trennzeichen_index = nachricht.find(':')
                    zeilennummer = 0
                    with open('/home/bb/piTelex/BTX/Input/iTelex_20260121.txt') as file:
                        for line in file:
                           zeilennummer += 1
                           trennzeichen_index = line.find(':')
                           if line[:trennzeichen_index] == "itelex_to":
                                print(" -- " + line)
                                iTelex_Nr = line[trennzeichen_index + 1:]
                           print(str(zeilennummer) + " - " + line.rstrip())

                    print(iTelex_Nr)

                    # Nachricht als gelesen markieren
                    

                    # text = nachricht[trennzeichen_index+1:]
                    # print(nachricht)
                    # print(from_user)
                    # print(iTelex_To)
                    # print(text)
                    #body = message_dict[0]['body']
                    #print(body)
                    # body_dict = json.loads(nachricht)
                    # body  = body_dict('body')
                    # print(body)

                    
                except json.JSONDecodeError as e:
                    print(f"Fehler beim Parsen von Zeile {line_num}: {e}", file=sys.stderr)
                    print(f"  Inhalt: {stripped_line}", file=sys.stderr)
                    
    except FileNotFoundError:
        print(f"Fehler: Datei '{filename}' wurde nicht gefunden.", file=sys.stderr)
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}", file=sys.stderr)

class User():
    user_id = "163163"
    ext = "1"



class Messaging:
    user = None
    dict = None

#    user_id = "720674"
#    user_ext = "1"

    def __int__(self, u):
        self.user = u

    def dict_filename(user_id, ext):
        return PATH_MESSAGES + user_id + "-" + ext + ".messages"

    def load_dict(user_id, ext):
        filename = Messaging.dict_filename(user_id, ext)
        print("Message Datei: " + filename)
        if not os.path.isfile(filename):
            sys.stderr.write("messages file not found \n")
            dict = { "messages": [] }
        else:
            with open(filename) as f:
                dict = json.load(f)
                return dict


    def save_dict(user_id, ext, dict):
        with open(Messaging.dict_filename(user_id, ext), 'w') as f:
            json.dump(dict, f)

    def save(self):
        Messaging.save_dict("163163","1", self.dict)

    def load(self):
        self.dict = Messaging.load_dict("163163", "1")

    def mark_as_read(self, index):
        self.load()
        if not self.dict["messages"][index].get("read", False):
            self.dict["messages"][index]["read"] = True
            self.save()

    # Löscht einen Eintrag aus der Liste
    def removekey(self, index):
        r = dict(self)
        del r[index]
             

    def send(self, itelex_nr, itelex_ext, user_id, ext, body):
        dict = Messaging.load_dict(user_id,ext)
        dict["messages"].append(
            {
                "from_user_id": itelex_nr,
                "from_ext": itelex_ext,
                "personal_data": False,
                "timestamp": time.time(),
                "body": body
            },
        )
        Messaging.save_dict(user_id, ext, dict)
        print("Nachricht gespeichert")


# Beispielaufruf:
if __name__ == "__main__":
    # Ersetze 'data.json' durch den tatsächlichen Namen deiner Datei
    # Stelle sicher, dass die Datei im selben Verzeichnis liegt oder gib den vollständigen Pfad an.
#    parse_json_file_to_lines('/home/pi/bildschirmtext/messages/100289-1.messages')

# mein Text

    # Datei im Verzeichnis finden
    path = PATH_ARCHIVE + '*.txt'
    print(path)
#    path = PATH_OUTPUT + '*"from btx"*.txt'
#    print(path)
    txt_files = glob.glob(path)
    if len(txt_files) == 0:
        exit()
#    print(txt_files)
    btx_file_path = ""
    for item in txt_files:
#        print(item)
        if "msg from" in item:
            print(item)
            print("Gefunden")
            btx_file_path = item
    # Datei einlesen
    if len(btx_file_path) > 0:
        with open(btx_file_path,'r', encoding='utf-8') as f:
            inhalt = f.read()
            print(inhalt)
    else:
        exit()
    zeilennummer = 0
    trenner = ':'
    btx_text = ''
    telex_nr = ""
    body_start = False
    body_text = ''
    btx_nr = ""
    ext = ""
    with open(btx_file_path,'r', encoding='utf-8') as f:
        for zeile in f:
            zeilennummer += 1
            print(str(zeilennummer) + " - " + zeile.strip())
            zeile = zeile.replace('<','')
            zeile = zeile.replace('>','')
            print(zeile)
            zeilen_elemente = zeile.split()
            # Fremde iTelex-Nr finden, nicht GW Nr 
            if len(zeilen_elemente) > 0:
                if zeilen_elemente[0].isdigit() and len(telex_nr) == 0:
                    telex_nr = zeilen_elemente[0]
                    if int(telex_nr) != 163163:
                        print("Telex_Nr: " + telex_nr)
                    else:
                        print("Telex_Nr nicht gefunden")
                        telex_nr = ""
            # BTX Teilnehmernummer suchen und merken
            zeilen_ende_index = zeile.find('+')
            print("Zeilen Ende : " + str(zeilen_ende_index))
            zeile = zeile.strip(" ")
            if zeilen_ende_index > 0:
                zeile = zeile[:zeilen_ende_index]
                zeilen_elemente = zeile.split()
                if zeilen_elemente[0] == 'btx':
                    btx_nr = zeilen_elemente[1]
                    if btx_nr.isdigit():
                        if len(zeilen_elemente) > 2:
                            ext = zeilen_elemente[2]
                    else:
                        btx_nr = ""
                    if ext.isdigit():
                        ext = str(int(ext))
                    else:
                        ext = "1"

                if len(btx_nr) > 0 and len(ext) > 0:
            	    print("BTX-Nr2: " + btx_nr + " - " + ext)
            	    body_start = True
            	    zeile = ""            

#            trennzeichen_index = zeile.find(':')
#            ext_pos_index = zeile.find('-')
#            print("Trennzeichen 1: " + str(trennzeichen_index) + ' - ' + str(ext_pos_index))
#            # btx: am Anfang der Zeile , BU ZI vorher entfernen
#            if trennzeichen_index > 0:
#               btx_text = zeile[:trennzeichen_index]
#               print("BTX Text: " + btx_text)
#               if btx_text == 'btx':
#                   print('BTX Zeile: ')
#            # Es müssen - und = in einer Zeile vorkomen
#            print("Test : " + btx_text)
#            
#            if trennzeichen_index > 0 and ext_pos_index > 0:
#                btx_nr = zeile[trennzeichen_index+1:]
#                trennzeichen_index = btx_nr.find('-')
#                btx_nr = btx_nr[:trennzeichen_index]
#                print("BTX-Nr: " + btx_nr)
#                extpos = zeile.find('-')
#                if extpos:
#                    ext = zeile[extpos + 1:]
#                    extpos = ext.find('=')
#                    ext = ext[:extpos]
#                    print("Ext: " + ext)
#                    # endepos = zeile.find('=')
#                    # ext = ext[:endepos]
#                    print("BTX: " + btx_nr + "-" + ext)
#                    body_start = True
#                    zeile = ''

            if body_start:
                body_text = body_text + zeile
         # restlicher Text in die Nachricht schreiben
                print(body_text)
            
    # BTX Mitbenutzernummer -xxxx 

    print("btx_nr: " + btx_nr + " - ext: " + ext)
    text_kopf = "itelex mitteilung\nbei antwort bitte text beginnen mit:\ntelex " + telex_nr + "+\n"
    print("iTelex_nr: " + telex_nr)
    print(body_text) 


    # Datei ins BTX einsortieren


    # user = btx_nr + ext
    

    user = User()
    user.user_id = btx_nr
    user.ext = ext
    itelex_nr = "163163"
    itelex_ext = "1"
    ms = Messaging()
    print ("User: " + user.user_id + " " + user.ext)
    if len(btx_nr) > 0 and len(ext) > 0:
#        ms.load()
        ms.send(itelex_nr, itelex_ext, btx_nr, ext, text_kopf + body_text)
        os.rename(btx_file_path,PATH_BTX_ARCHIVE+os.path.basename(btx_file_path))
    else:
        print("Fehler beim Übertragen!")

    # Wenn Datei übertragen dann Datei löschen

