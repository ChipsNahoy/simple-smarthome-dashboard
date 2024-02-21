import mysql.connector


class Database:
    def __init__(self):
        self.utama = mysql.connector.connect(
            host="localhost",
            user="root",
            password="XXX",                     ## Change this to your db's password
            database="MySmartHome"
        )
        self.c = self.utama.cursor()


def reset():
    utama = mysql.connector.connect(
        host="localhost",
        user="root",
        password="XXX"                          ## Change this to your db's password
    )

    c = utama.cursor()
    c.execute("drop database MySmartHome")
    c.execute("create database MySmartHome")


def create_table():
    db = Database()

    db.c.execute("""create table users(
               id        int auto_increment,
               username  varchar(100) not null,
               password  varchar(100) not null,
               email    varchar(100) not null,
               role		enum("parent", "child", "guest", "admin") not null,
               primary key(id)
          )""")

    db.c.execute('''create table role_access(  
               id                  int auto_increment,
               role                enum("parent", "child", "guest", "admin", "auto")	not null,
               change_light        enum("yes", "no")   not null,
               change_music        enum("yes", "no")   not null,
               change_ac           enum("yes", "no")   not null,
               change_guest_mode   enum("yes", "no")   not null,
               change_auto_mode    enum("yes", "no")   not null,
               primary key(id)
          )''')

    db.c.execute("""create table auto_mode(
               id        int auto_increment,
               mode      enum('On', 'Off') not null,
               time      timestamp default current_timestamp,
               editor    varchar(100) not null default 'admin',
               primary key(id)
     )""")

    db.c.execute("""create table guest_mode(
               id        int auto_increment,
               mode      enum('On', 'Off') not null,
               editor    varchar(100) not null default 'admin',
               time      timestamp default current_timestamp,
               primary key(id)
     )""")

    db.c.execute("""create table bathroom (
               id        int auto_increment,
               light	enum('On', 'Off') not null,
               music	enum('On', 'Off') not null,
               editor    varchar(100) not null default 'auto',
               time      timestamp default current_timestamp,
               primary key(id)
     )""")

    db.c.execute("""create table bedroom (
               id        int auto_increment,
               light     enum('On', 'Off') not null,
               music	enum('On', 'Off') not null,
               ac        enum('On', 'Off') not null,
               editor    varchar(100) not null default 'auto',
               time      timestamp default current_timestamp,
               primary key(id)
     )""")

    db.c.execute("""create table kitchen (
               id        int auto_increment,
               light     enum('On', 'Off') not null,
               music	enum('On', 'Off') not null,
               ac        enum('On', 'Off') not null,
               editor    varchar(100) not null default 'auto',
               time      timestamp default current_timestamp,
               primary key(id)
     )""")

    db.c.execute("""create table livingroom (
               id        int auto_increment,
               light     enum('On', 'Off') not null,
               music	enum('On', 'Off') not null,
               ac        enum('On', 'Off') not null,
               editor    varchar(100) not null default 'auto',
               time      timestamp default current_timestamp,
               primary key(id)
     )""")

    db.c.execute("""create table admin_history (
                   id        int auto_increment,
                   email     varchar(100) not null,
                   last_pw   varchar(100) not null,
                   new_pw    varchar(100) not null,
                   editor    varchar(100) not null default 'admin',
                   time      timestamp default current_timestamp,
                   primary key(id)
         )""")

    db.utama.commit()
    db.utama.close()


def check_user(username, password):
    db = Database()
    db.c.execute('''select * from users where binary username = ("%s") and password = ("%s")''' % (username, password))
    data = db.c.fetchone()

    if not data:
        login_stat = 0
        role = None
    else:
        login_stat = 1
        role = data[4]

    db.utama.commit()
    db.utama.close()

    return login_stat, role


def update_new_pass(email, password, editor_un):
    db = Database()
    db.c.execute('''select * from users where binary email = ("%s")''' % email)
    data = db.c.fetchone()
    db.c.execute('''insert into admin_history (email, last_pw, new_pw, editor) values ("%s", "%s", "%s", "%s")'''
                 % (email, data[2], password, editor_un))
    db.c.execute('''update users
                set password = '{}' where binary email = '{}' '''.format(password, email))
    db.utama.commit()
    db.utama.close()


def room_condition(room, tool_stat):
    db = Database()
    light = tool_stat[0]
    music = tool_stat[1]
    editor = tool_stat[-1]
    if room != "bathroom":
        ac = tool_stat[2]
        update = '''insert into %s (light, music, ac, editor) values ("%s", "%s", "%s", "%s")''' \
                 % (room, light, music, ac, editor)
    else:
        update = '''insert into %s (light, music, editor) values ("%s", "%s", "%s")''' \
                 % (room, light, music, editor)

    db.c.execute(update)
    db.utama.commit()
    db.utama.close()


def auto_stat(condition):
    db = Database()
    if condition:
        condition = 'On'
    else:
        condition = 'Off'
    db.c.execute('''insert into auto_mode (mode) values ("%s")''' % condition)
    db.utama.commit()
    db.utama.close()


def guest_stat(condition, editor):
    db = Database()
    if condition:
        condition = 'On'
    else:
        condition = 'Off'
    db.c.execute('''insert into guest_mode (mode,editor) values ("%s", "%s")''' % (condition,editor))
    db.utama.commit()
    db.utama.close()


def default_condition():
    db = Database()

    tool_stat = ["off", "off", "off", "admin"]
    room_condition("bedroom", tool_stat)

    tool_stat = ["off", "off", "off", "admin"]
    room_condition("kitchen", tool_stat)

    tool_stat = ["off", "off", "off", "admin"]
    room_condition("livingroom", tool_stat)

    tool_stat = ["off", "off", "admin"]
    room_condition("bathroom", tool_stat)

    auto_stat(0)
    guest_stat(0, "admin")

    db.utama.commit()
    db.utama.close()


def insert_user(name, email, pw, role):
    db = Database()
    db.c.execute('''insert into users (username, email, password, role) values ("%s", "%s", "%s", "%s")''' % (
        name, email, pw, role))
    db.utama.commit()
    db.utama.close()


def insert_role_access(role, change_light, change_music, change_ac, change_guest_mode, change_auto_mode):
    db = Database()
    db.c.execute(
        '''insert into role_access(role, change_light, change_music, change_ac, change_guest_mode, change_auto_mode)
        values ("%s", "%s", "%s", "%s", "%s", "%s")'''
        % (role, change_light, change_music, change_ac, change_guest_mode, change_auto_mode))
    db.utama.commit()
    db.utama.close()


def get_room_cond(room):
    db = Database()
    db.c.execute('''select * from %s order by id desc limit 1''' % room)
    return db.c.fetchone()


reset()
create_table()
insert_user('parent', 'parent@gmail.com', 'parent', 'parent')
insert_user('child', 'child@gmail.com', 'child', 'child')
insert_user('admin', 'admin@gmail.com', 'admin', 'admin')
insert_user('guest', 'guest@gmail.com', 'guest', 'guest')

insert_role_access('parent', 'yes', 'yes', 'yes', 'yes', 'yes')
insert_role_access('child', 'yes', 'yes', 'yes', 'no', 'no')
insert_role_access('admin', 'no', 'no', 'no', 'no', 'no')
insert_role_access('guest', 'yes', 'yes', 'yes', 'yes', 'no')
insert_role_access('guest', 'no', 'no', 'no', 'no', 'no')

default_condition()
