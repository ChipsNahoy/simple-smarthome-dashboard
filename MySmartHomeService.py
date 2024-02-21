import MySmartHomeDbStore as db
import configparser
import threading
import time

# Read Sensor.ini and return the value of the sensor reading
# Return 1/0
def read_sensor(category, variable):
    conf = configparser.ConfigParser()
    conf.read('Sensor.ini')                     ## You may need to change this to the complete directory instead of relative directory
    value = conf.getint(category, variable)
    return value


# Writes into Sensor.ini the updated value of the sensor reading
def update_sensor(category, variable, value):
    conf = configparser.ConfigParser()
    conf.read('Sensor.ini')                     ## You may need to change this to the complete directory instead of relative directory
    conf[category][variable] = str(value)
    with open('Sensor.ini','w') as new_file:    ## You may need to change this to the complete directory instead of relative directory
        conf.write(new_file)
    new_file.close()


# Take the room condition and edit based on the tool and the current condition
# r_list = [light, music, ac]
def change_condition(room, tool, editor):
    if tool == 'light':
        point = 0
    elif tool == 'music':
        point = 1
    else:
        point = 2
    r_list = list(check_rcond(room))[1:4]
    if r_list[point] == 'Off':
        r_list[point] = 'On'
    else:
        r_list[point] = 'Off'
    r_list.append(editor)
    db.room_condition(room, r_list)


# Similar to change_condition, but only edit to db if condition changes
def auto_condition(room, tool, param):
    if tool == 'light':
        point = 0
    elif tool == 'music':
        point = 1
    else:
        point = 2
    r_list = list(check_rcond(room))[1:4]
    if r_list[point] != param:
        r_list[point] = param
        r_list.append('Auto')
        db.room_condition(room, r_list)


# Change db for all rooms based on sensor reading and update time on Sensor.ini
def auto_sensor():
    while True:
        global stop_thread
        if stop_thread:
            break
        r_list = ['bedroom', 'kitchen', 'livingroom', 'bathroom']
        r_var = ['human_presence', 'light_condition_dark', 'temperature_high']

        hour = read_sensor('time', 'current_time')

        for i in r_list:
            cond_list = []
            if i == 'bathroom':
                for k in range(len(r_var) - 1):
                    val = read_sensor(i, r_var[k])
                    cond_list.append(val)
            else:
                for j in range(len(r_var)):
                    val = read_sensor(i, r_var[j])
                    cond_list.append(val)
            auto_room(i, hour, cond_list)
        hour += 1
        print(hour)

        update_sensor('time', 'current_time', hour % 24)
        time.sleep(2)


# Give specified room condition to auto_condition for different sensor readings
def auto_room(room, time, cond_list):
    if cond_list[0] and cond_list[1] and (time in range(6, 23)):  # Kalau ada orang dan gelap, lampu nyala
        auto_condition(room, 'light', 'On')
    else:
        auto_condition(room, 'light', 'Off')

    if cond_list[0] or (time in range(8, 12)):
        auto_condition(room, 'music', 'On')
    else:
        auto_condition(room, 'music', 'Off')

    if room != 'bathroom':
        if cond_list[0] and cond_list[2]:
            auto_condition(room, 'ac', 'On')
        else:
            auto_condition(room, 'ac', 'Off')

# Start threading only if there is no running threads
def start_threading():
    global t_num
    global thread_list
    if len(thread_list) == 0:
        my_thread = threading.Thread(target=auto_sensor, name='thread{}'.format(t_num))
        thread_list.append(my_thread)
        t_num += 1
        my_thread.start()

# Stop all threads
def stop_threading():
    global stop_thread
    global thread_list
    stop_thread = True
    for i in thread_list:
        i.join()
    thread_list = []
    stop_thread = False

# Change the current mode
# cond = 1 for Automatic, cond = 0 for Manual
def change_mode(cond):
    db.auto_stat(cond)

# Change the current Guest mode
# cond = 1 for On, cond = 0 for Off
def change_guest_mode(cond,editor):
    db.guest_stat(cond,editor)

# Check for name and pw in db
# Return (login_stat, role)
# login_stat = 1 if successful, otherwise 0
def login(name, pw):
    return db.check_user(name, pw)

# Insert email, pw, and editor username to admin history
def change_pass(email, pw, editor_un):
    db.update_new_pass(email, pw, editor_un)

# Returns list of last input to room db
def check_rcond(room):
    return db.get_room_cond(room)

# Returns 1 or 0 depending on the condition of the tool in the room
def check_tool(room, tool):
    t_list = check_rcond(room)
    if tool == 'music':
        return ret_val(t_list[2])
    elif tool == 'ac':
        return ret_val(t_list[3])
    else:
        return ret_val(t_list[1])

# Change string to binary
def ret_val(v):
    if v == 'On':
        return 1
    else:
        return 0

stop_thread = False  # stop condition for threads
t_num = 0            # for thread names
thread_list = []     # for thread management