import json
import sys
import os
#from usr import User
# Modul Path anhängen
sys.path.append('/home/bb/bildschirmtext/server')

# Import der benötigten Module
from messaging import Messaging
from messaging import Message
from user import User
from user import User_UI

PATH_MESSAGES = "/home/bb/bildschirmtext/messages/"


# Beispielaufruf:
if __name__ == "__main__":
    # Ersetze 'data.json' durch den tatsächlichen Namen deiner Datei
    # Stelle sicher, dass die Datei im selben Verzeichnis liegt oder gib den vollständigen Pfad an.
#    parse_json_file_to_lines('/home/pi/bildschirmtext/messages/163163-1.messages')

# mein Text

    gelesen = False
    msg_anzahl = 0
    index = 0

    u = User()
    user_id = "163163"
    user_ext = "1"
    user_pw = "xxxxx"
    angemeldet = u.login(user_id,user_ext,user_pw)
    if not angemeldet:
        print("Fehler bei der Anmeldung")
        exit()
    # print("Angemeldet: " + str(angemeldet))
    user = u.get(user_id,user_ext)
#    print(user)

    # Abfrage ob neue Nachrichten vorliegen
    if user.messaging.has_new_messages():
        messages = user.messaging.select(False,0,1)
        msg_anzahl = len(messages)
        print("Anzahl Nachrichten: " + str(msg_anzahl))
        if msg_anzahl == 1 :
#            print(messages[0].body())
            nachricht = messages[0].body()
            from_user = messages[0].from_user_id()
            from_ext  = messages[0].from_user_ext()
            gelesen   = messages[0].gelesen()
#            print("Gelesen 2: " + str(gelesen))
            from_ext = from_ext.zfill(4)		# mit Nullen auffüllen
            # Nachricht parsen telex_nr ermitteln
            trennzeichen_index = nachricht.find('+')
            iTelex_To = "itelex_to:" + nachricht[:trennzeichen_index]
            iTelex_Kopf = nachricht[:trennzeichen_index].split()
            # bis zum + Zeichen
            if len(iTelex_Kopf) > 0:
                iTelex_To = "itelex_to:" + iTelex_Kopf[1]
                iTelex_Kopf = "btx mitteilung\r\nbei antwort bitte text beginnen mit:"
                iTelex_From = "btx " + from_user + " " + from_ext + "+"
                iTelex_Text = nachricht[trennzeichen_index+1:]
                # !!! Zufälligen Dateinamen noch erzeugen    
                with open('/home/bb/piTelex/BTX/Input/iTelex_20260121.txt', 'w', encoding="utf-8") as f:
                    f.write(iTelex_To + "=\r\n" + iTelex_Kopf + "\r\n" + iTelex_From + "\r\n\n" + iTelex_Text)
	        # Als gelesen markieren
                user.messaging.mark_as_read(messages[0].msg_index())
            else:
                print("Fehler Telex Nummer nicht gefunden")

