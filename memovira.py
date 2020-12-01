import sqlite3
import json

conn = sqlite3.connect('dbmemovira.sqlite3')
c = conn.cursor()

with open("rooms.json", "r") as json_rooms:
    room_data = json.load(json_rooms)


class Avatar(object):
    def __init__(self):
        self.curroom = "main"
        self.firstvisit = True
    def checkvisit(self):
        if self.firstvisit:
            self.firstvisit = False
            return True
        return False
    def set_curroom(self, newroom):
        self.curroom = newroom
        self.firstvisit = True
    def get_curroom(self):
        return self.curroom


def add_entries(entry):
    try:
        c.execute('INSERT INTO "{}" VALUES (?, ?)'.replace("{}", avatar.curroom), (entry, 0))
        conn.commit()
    except sqlite3.OperationalError as error:
        print(error)


def change_curroom(room):
    if room in room_data["rooms"]:
        avatar.set_curroom(room)
    else:
        print("No such room")


def change_roomdesc(newdesc):
    try:
        room_data["rooms"][avatar.get_curroom()]["desc"] = newdesc
    
        with open("rooms.json", "w") as f:
            json.dump(room_data, f)
    except KeyError:
        print("No such room!!")


def change_prio(args):
    args_list_str = args.split( )

    if len(args_list_str) == 1:
        print("Nog enough arguments!")
        return None
    elif len(args_list_str) > 2:
        print("Stop argueing!")
        return None

    args_list_int = [int(arg) for arg in args.split( ) if arg.isdigit()]

    if len(args_list_int) != 2:
        print("Only integers please!")
        return None

    c.execute('Update "{}" set priority = (?) where rowid = (?)'.replace("{}", avatar.get_curroom()), (args_list_int[1], get_rowid(args_list_int[0])))
    conn.commit()


def create_room(room):
    room_data["rooms"][room] = {"desc": "", "exits": [], "parent": ""}
    room_data["rooms"][room]["desc"] = room
    room_data["rooms"][room]["exits"].append(avatar.get_curroom())
    room_data["rooms"][room]["parent"] = avatar.get_curroom()
    room_data["rooms"][avatar.get_curroom()]["exits"].append(room)

    with open("rooms.json", "w") as f:
        json.dump(room_data, f)


def create_roomtable(roomname):
    c.execute('CREATE TABLE IF NOT EXISTS "{}" (synopsis text, priority integer)'.replace("{}", roomname))
    c.execute('CREATE TABLE IF NOT EXISTS "{}" (synopsis text, priority integer)'.replace("{}", roomname + " RIP"))
    conn.commit()


def delete_entry(id):
    try:
        rowid = get_rowid(int(id))
        c.execute('DELETE from "{}" where rowid = (?)'.replace("{}", avatar.curroom), rowid)
        conn.commit()
    except sqlite3.Error as error:
        print("Failed to delete record from sqlite table", error)
    except ValueError as error:
        if rowid != None:
            print("Please enter an integer")


def destroy_room(room):
    if room == "room":
        room = avatar.get_curroom()

    if avatar.get_curroom() == room:
        avatar.set_curroom(room_data["rooms"][room]["parent"])

    room_data["rooms"][room_data["rooms"][room]["parent"]]["exits"].remove(room)
    room_data["rooms"].pop(room, None)

    with open("rooms.json", "w") as f:
        json.dump(room_data, f)


def destroy_roomtable(table):
    if table == "room":
        table = avatar.get_curroom()

    try:
        c.execute('DROP TABLE "{}"'.replace("{}", table))
        conn.commit()
    except sqlite3.OperationalError as error:
        print(error)


def get_rowid(query):
    try:
        c.execute('SELECT rowid from "{}"'.replace("{}", avatar.curroom))
        rows = c.fetchall()
        return str(rows[query-1][0])
    except sqlite3.OperationalError as error: 
        print(error)
    except IndexError as error:
        print("Hmmz.. can't find that one!")


def list_rooms():
    print(sorted([*room_data["rooms"]])) 


def list_tablerooms():
    c.execute('SELECT name from sqlite_master where type= "table"')
    all_tablerooms = [table[0] for table in c.fetchall() if table[0] in room_data["rooms"]]
    print(all_tablerooms)


def look(auto=False):
    if auto == False or avatar.checkvisit():
        try:
            print(room_data["rooms"][avatar.curroom]["desc"])
            print("Exits are: " + str(room_data["rooms"][avatar.curroom]["exits"]))
        except KeyError:
            print("No such room!!")


def show_commands():
    print("Available commands: add, chroomdesc, chprio, create, createbranch, delete, destroy, exit, go, help, listrooms, listtablerooms, look, sortbyprio, view")


def sort_prio():
    try:
        c.execute('SELECT * FROM "{}" ORDER BY priority DESC'.replace("{}", avatar.get_curroom()))
        rows = c.fetchall()
        for index, row in enumerate(rows):
            print(str(index+1) + " - " + row[0] + " & " + str(row[1]))
    except sqlite3.OperationalError as error:
        print(error)


def view_entries():
    try:
        c.execute('SELECT * FROM "{}"'.replace("{}", avatar.curroom))
        rows = c.fetchall()
        for index, row in enumerate(rows):
            print(str(index+1) + " - " + row[0] + " & " + str(row[1]))
    except sqlite3.OperationalError as error:
        print(error)


avatar = Avatar()  
    
while True:
    look(auto=True)

    cmd = input("------------------------------\n")
    command = [seg.lstrip() for seg in cmd.lstrip().split(" ", 1) if seg.lstrip() != ""]

    try:
        if command[0] == "add":
            add_entries(command[1])
        elif command[0] == "chroomdesc":
            change_roomdesc(command[1])
        elif command[0] == "chprio":
            change_prio(command[1])
        elif command[0] == "create":
            create_room(command[1])
            create_roomtable(command[1])
        elif command[0] == "createbranch":
            print(room_data)
            create_room(command[1])
        elif command[0] == "delete":
            delete_entry(command[1])
        elif command[0] == "destroy":
            destroy_roomtable(command[1])
            destroy_room(command[1])
        elif command[0] == "exit":
            conn.close()
            break
        elif command[0] == "go": 
            change_curroom(command[1])
        elif command[0] == "help":
            show_commands()
        elif command[0] == "listrooms":
            list_rooms()
        elif command[0] == "listtablerooms":
            list_tablerooms()
        elif command[0] == "look":
            look()
        elif command[0] == "sortbyprio":
            sort_prio()
        elif command[0] == "view":
            view_entries()
        else:
            print("Command not recognised")
    except IndexError as error:
        print("Pretty please provide an argument <3")