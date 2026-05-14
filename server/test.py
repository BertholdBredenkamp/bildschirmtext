#
#

from rss import RSS_UI
from etb import ETB_UI
from messaging import Messaging
from messaging import Messaging_UI
from user import User

def main():
    print("Programm startet")
    # Hauptlogik hier
    user = User()
    print(dir(user))
    print("\n")
#    print(len(user.messaging))
#    print(dir(user.messaging))
    user.user_id = "720672"
    user.ext = "1"
    pageid = "3001188c"
    basedir = "../data/"
    PATH_MESSAGES = "../messages/"
    user.messaging = Messaging(user)
    ret = Messaging_UI.messaging_create_list(user, True)
    print(ret)

if __name__ == "__main__":
    main()

