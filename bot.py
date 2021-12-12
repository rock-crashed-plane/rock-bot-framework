"""

Simple bot framework for the Rock: Crashed Plane (fuzzem.com) MUD.

Beware THE UNKNOWN. Beware exhaustion.

Your bot could smack into walls until he runs out of turns.

Or die!

"""

from random import random, randint
import datefinder
import telnetlib
import datetime
import time
import sys
import re

#### Start Configuration ###############################

# You can either provide the username and password on the command line:
#
# python bot.py myusername mypassword
#
# Or you can hard code them into the script here, in the except clause.

try:
    user = sys.argv[1]
    password = sys.argv[2]
except:
    user = ''
    password = ''

# Take a breather if no npcs are in the room and hp below this percentage
hp_thresh = 70

# Default amount of time to sleep.
# Sleep commands are sprinkled throughout the code.
sleep_duration = .5

# Amount of cryl in room before loot is triggered.
loot_thresh = 250

#### End Configuration ###############################

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def sleep(duration=None):

    """

    If no duration is specified, sleep for sleep_duration in configuration.

    """

    if duration == None:
        time.sleep(sleep_duration)
    else:
        time.sleep(duration)

def random_sleep():
    rnd = random()*3

    if rnd > .5:
        sleep(rnd)
    else:
        sleep(.5)

def read():

    """

    Eagerly get text from rock.

    """

    return tn.read_very_eager().decode('ascii')

def send_command(command=None):

    """

    If no command is specified, retrive a room prompt by sending a newline.

    """

    if command == None:
        tn.write(''.encode('ascii') + b"\n")
    else:
        tn.write(command.encode('ascii') + b"\n")

    sleep()

    ansi_reply = read()
    plain_reply = ansi_escape.sub('', ansi_reply)

    return plain_reply, ansi_reply

def sc(command=None):

    if command == None:
        plain_reply, ansi_reply = send_command()
    else:
        plain_reply, ansi_reply = send_command(command)

    print(ansi_reply)

def login():

    """

    Login to the game with the user / password specified in the configuration.

    """

    sleep()

    plain_reply, ansi_reply = send_command('')

    if '[E]nter Realm' in plain_reply:
        plain_reply, ansi_reply = send_command('E')
        print(ansi_reply)

    if 'What is your fuzzem.com UserID' in plain_reply:
        plain_reply, ansi_reply = send_command(user)
        print(ansi_reply)

    if 'password' in plain_reply:
        plain_reply, ansi_reply = send_command(password)
        print(ansi_reply)

    sc()

    sleep()

def move(dir):

    plain_reply, ansi_reply = send_command(dir)
    print(ansi_reply)

def look():

    plain_reply, ansi_reply = send_command()
    print(ansi_reply)

def inv():

    sc('i')

def loot():

    """

    Gets cryl in room if over loot_thresh

    """

    plain_reply, ansi_reply = send_command()
    plain_reply = plain_reply.replace('\r\n','').replace('  ',' ').replace('  ',' ')
    plain_reply = plain_reply.split('cryl.')

    if len(plain_reply) > 1:

        plain_reply = plain_reply[0]
        plain_reply.strip()
        plain_reply = plain_reply.split(' ')
        plain_reply = [i for i in plain_reply if not i == '']

        try:
            cryl = int(plain_reply[-1])

            if cryl > loot_thresh:

                sc('loot')

        except:
            pass

def exit():

    sc('exit')

def get_prompt():

    """

    Gets the current prompt, ie:

    >904/1392 64% 0/0 5929 67 118>

    Note that there is a trailing space.

    If multiple prompts are in the reply text, returns the most recent prompt.

    """

    def gp():

        plain_reply, ansi_reply = send_command()
        plain_reply = plain_reply.split('\r\n')
        plain_reply = [i for i in plain_reply if len(i)]
        plain_reply = [i for i in plain_reply if i[0] == '>']

        if len(plain_reply):
            return plain_reply[-1]
        else:
            return False

    reply = gp()

    # Try until we get a prompt

    while not reply:

        reply = gp()

        print(reply)

    return reply

def cur_hp():

    """

    Returns an integer with your current number of hit points.

    """

    got_hp = False

    while not got_hp:

        try:

            reply = get_prompt()
            hp = int(reply.split(' ')[0].replace('>','').split('/')[0])
            got_hp = True

        except:

            continue

    return hp

def cur_hp_percent():
    """

    Returns an integer with your current percentage of hit points 

    """    

    got_hp_percent = False

    while not got_hp_percent:

        try:

            reply = get_prompt()
            hp_percent = int(reply.split(' ')[1].replace('%',''))
            got_hp_percent = True

        except:

            continue

    return hp_percent

def cur_turns():

    """

    Returns an integer with your current number of turns

    """

    got_turns = False

    while not got_turns:

        try:

            reply = get_prompt()
            turns = int(reply.split(' ')[3])
            got_turns = True

        except:

            continue

    return turns

def check_for_npcs():

    """

    Returns True if there are NPCs in the room, otherwise, returns False.

    """

    plain_reply, ansi_reply = send_command()

    npc_text = [row for row in plain_reply.split('\r\n') if 'NPCs in room' in row]

    if len(npc_text) == 0:
        return False
    else:
        return True

def check_for_npc(npc):

    plain_reply, ansi_reply = send_command()
    
    npc_text = [row for row in plain_reply.split('\r\n') if 'NPCs in room' in row]

    if len(npc_text) == 0:
        return False

    npc_text = npc_text[0]
    npcs = npc_text.split(':')[1:]

    npcs_clean = [npc.replace('.','').strip() for npc in npcs]

    for npc in npcs_clean:

        if npc in npcs_clean:

            return True

    return False

def rest():

    """

    Rest until HP is over hp_thresh set in the config.

    Will not rest if an NPC is in the room.

    Checks to see if an NPC has spawned between breathers.

    """

    if not check_for_npcs():

        hp_percent = cur_hp_percent()

        while hp_percent < hp_thresh:

            if not check_for_npcs():

                sc('rest')

                hp_percent = cur_hp_percent()

            else:

                break

            sleep()

def get_exits():

    got_exits = False

    while not got_exits:

        try:

            plain_reply, ansi_reply = send_command()

            exits = [row for row in plain_reply.split('\r\n') if ' lie' in row][-1]
            exits = exits.replace(', ',',').split(' ')[-1].replace('.','').split(',')

            got_exits = True

        except:

            continue

    return exits

def get_items_in_room():

    plain_reply, ansi_reply = send_command()
    plain_reply = plain_reply.split('\r\n')

    index = [idx for idx, s in enumerate(plain_reply) if 'Items in room:' in s]

    if len(index) > 0:

        # Get last occurence of Items in room:

        index = index[-1]

        return ''.join(plain_reply[index:])  \
                 .replace('  ','')           \
                 .split('.')[0]              \
                 .split(':')[1]              \
                 .strip()                    \
                 .replace(', ',',')          \
                 .split(',')

    else:
        return []

def get_all_item(item_name):

    for item in get_items_in_room():

        if item_name in item:

            sc('get ' + item)

def seconds_until_spawn(room):

    plain_reply, ansi_reply = send_command('spawntimes')
    plain_reply = plain_reply.split('\r\n')

    entry = [i for i in plain_reply if room in i][0]
    timstamp = entry.split('(')[0].strip().split(' ')[3]

    spawn = list(datefinder.find_dates(timstamp))[0]

    now = datetime.datetime.now()

    return (spawn - now).seconds

def kill_freresh():

    time_to_sleep = seconds_until_spawn('Dissolved Hallucination')

    def mins_left():
        return int(str(int(str(time_to_sleep).split('.')[0]) / 60).split('.')[0])

    while mins_left() > 0:
        print("Freresh spawns in " + str(mins_left()) + " minutes.")

        sleep(60)

        time_to_sleep -= 60

    sleep(time_to_sleep)

    s(); sleep(2)
    se();sleep(2)
    se();sleep(2)

    if not check_for_npc('Freresh'):
        return False

    sleep(5)
    sc('kill freresh')
    sleep(2)
    sc('get crank')
    sleep(2)

    nw();sleep(2)
    nw();sleep(2)
    n()

def kill_freresh_loop():

    while True:

        kill_freresh()


def kill_scientist():

    """

    Kill the first scientist in a room in the troitian lab.

    """

    plain_reply, ansi_reply = send_command()

    plain_reply = plain_reply.split('\r\n')

    killed = False

    for row in plain_reply:

        if 'NPCs in room' in row:

            first_npc = row.replace('.','').split(': ')[1].split(', ')[0]

            k = 'kill ' + first_npc
            plain_reply, ansi_reply = send_command(k)
            print(ansi_reply)

            if 'iridescent' in plain_reply:
                plain_reply, ansi_reply = send_command('get flask of iridescent liquid')
                print(ansi_reply)

            killed = True

    sleep()

    return killed

def kill_scientists():

    """

    Kill all scientists in a room in the troitian lab.

    Assumes you have enough HP to kill them all.

    """

    npcs = True

    while npcs:

        plain_reply, ansi_reply = send_command()
        plain_reply = plain_reply.split('\r\n')

        found_npcs = False

        for row in plain_reply:

            if 'NPCs in room' in row:
                found_npcs = True

        if found_npcs:
            kill_scientist()
        else:
            npcs = False

def troitian_lab_bot_tick():

    """

    Kill all NPCs in a room of the troitian lab, and rest.

    - Check that we have enough turns.
    - Rest until above the HP threshold set in the config.
    - Kill all scientists in the room.
    - Rest until above the HP threshold set in the config.

    If an NPC spawns while resting after fighting, the NPC will be ignored.

    """

    # If we are out of turns, exit the game.
    if cur_turns() < 100: exit()

    # Take a breather until hp over hp_thresh.
    re()

    # Kill all npcs (or die trying)
    kill_scientists()

    # Get cryl if there is more cryl than loot_thresh.
    loot()

    # Extra get iridescent vial
    get_all_item('iridescent')

    # Take a breather until hp over hp_thresh.
    re()

    # Look at the room and print the output.
    l()

def troitian_lab_bot_move_random_direction():

    exits = get_exits()

    if exits == ['west', 'southeast', 'northeast', 'east']:
        exits = ['southeast', 'northeast', 'east']

    random_direction  = exits[randint(0, len(exits) - 1)]

    move(random_direction)

def troitian_lab_bot_random():

    """

    Run laps around troitian laboratory taking random exits.

    Collects iridescent vials.

    Exits the game if you run out of turns.

    """

    while True:
        troitian_lab_bot_tick()
        troitian_lab_bot_move_random_direction()

def troitian_lab_bot_loop():

    """

    Run laps around troitian laboratory.

    Collects iridescent vials.

    Assumes you start in ne corner of lab.

    NOTE: If you run multiple characters in a loop, they will always end up
    in the same room, even if you start them in different rooms.

    Exits the game if you run out of turns.

    """

    while True:
        troitian_lab_bot_tick();sw()
        troitian_lab_bot_tick();s()
        troitian_lab_bot_tick();s()
        troitian_lab_bot_tick();sw()
        troitian_lab_bot_tick();ne()
        troitian_lab_bot_tick();nw()
        troitian_lab_bot_tick();sw()
        troitian_lab_bot_tick();n()
        troitian_lab_bot_tick();n()
        troitian_lab_bot_tick();s()
        troitian_lab_bot_tick();e()
        troitian_lab_bot_tick();n()
        troitian_lab_bot_tick();e()
        troitian_lab_bot_tick();ne()


"""

Aliases

You can use these (and the above functions) to play the game from your python
terminal (useful for testing your bot), and to make your code more legible.

"""

def ks():   kill_scientists()
def re():   rest()
def m(dir): move(dir)
def l():    look()

def u():  move('u')
def d():  move('d')
def n():  move('n')
def s():  move('s')
def e():  move('e')
def w():  move('w')
def ne(): move('ne')
def se(): move('se')
def nw(): move('nw')
def sw(): move('sw')

"""

Run the bot.

"""

# Establish a telnet connection
tn = telnetlib.Telnet("rock.fuzzem.com", port=4000)

# Log in with your provided username and password in the top configuration.
login()

# Run your bot
troitian_lab_bot_random()

