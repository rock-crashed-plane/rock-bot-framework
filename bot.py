#!/usr/local/bin/python3.10

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


# Print lots of helpful debugging messages
debug = False


# Flush colored text output more frequently
flush = True

    
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

def send_command(command = None):

    """

    If no command is specified, retrive a room prompt by sending a newline.

    """

    if command == None:
        tn.write(''.encode('ascii') + b'\n')
    else:
        tn.write(command.encode('ascii') + b'\n')

def c(command = None):

    if command == None:
        send_command()
    else:
        send_command(command)

def read_until(text = '> ', timeout = 10):

    ansi_reply = tn.read_until(str.encode(text)).decode('utf-8')

    plain_reply = ansi_escape.sub('', ansi_reply)

    return plain_reply, ansi_reply

def login():

    """

    Login to the game with the user / password specified in the configuration.

    """

    send_command('E')

    plain_reply, ansi_reply = read_until()
    _ = tn.read_very_eager()

    print(ansi_reply)

    send_command(user)

    plain_reply, ansi_reply = read_until()
    _ = tn.read_very_eager()

    print(ansi_reply)

    send_command(password)

    plain_reply, ansi_reply = read_until()
    _ = tn.read_very_eager()

    print(ansi_reply)

def move(dir):

    _ = tn.read_very_eager()

    c(dir)

    plain_reply, ansi_reply = read_until()

    _ = tn.read_very_eager()

    print(ansi_reply)

    while 'exhausted' in plain_reply:

        print('Exhausted')

        sleep(.5)

        _ = tn.read_very_eager()

        c(dir)

        plain_reply, ansi_reply = read_until()

        _ = ansi_escape.sub('', tn.read_very_eager().decode('ascii'))

    reply = plain_reply

    for exit_condition in ['turns', 'You disintegrate into the ether']:

        if exit_condition in reply:

            _ = tn.read_very_eager()

            print(ansi_reply)

            print("Exit condition: " + exit_condition)

            exit()

            plain_reply, ansi_reply = read_until()

            _ = tn.read_very_eager()

            print(ansi_reply)

            sys.exit()

def exit():

    c('exit')

def get_prompt(text=None):

    """

    Gets the current prompt, ie:

    >904/1392 64% 0/0 5929 67 118>

    Note that there is a trailing space.

    If multiple prompts are in the reply text, returns the most recent prompt.

    """

    def gp(text=None):

        if text == None:

            _ = tn.read_very_eager()

            c()

            plain_reply, ansi_reply = read_until()

        else:

            plain_reply = text

        plain_reply = plain_reply.split('\r\n')
        plain_reply = [i for i in plain_reply if len(i)]
        plain_reply = [i for i in plain_reply if i[0] == '>']

        if len(plain_reply):
            return plain_reply[-1]
        else:
            return False

    if text == None:
        reply = gp(text)
    else:
        reply = gp()

    while not reply:

        reply = gp()

    return reply

def cur_hp_percent(text=None):

    """

    Returns an integer with your current percentage of hit points 

    """

    got_hp_percent = False

    while not got_hp_percent:

        try:

            if text == None:
                reply = get_prompt()
            else:
                reply = text

            hp_percent = int(reply.split(' ')[1].replace('%',''))

            got_hp_percent = True

        except:

            continue

    return hp_percent

def check_for_npcs():

    """

    Returns True if there are NPCs in the room, otherwise, returns False.

    """

    _ = tn.read_very_eager()

    c()

    plain_reply, ansi_reply = read_until()

    npc_text = [row for row in plain_reply.split('\r\n') if 'NPCs in room' in row]

    if len(npc_text) == 0:
        return False
    else:
        return True

def rest():

    """

    Rest until HP is over hp_thresh set in the config.

    Will not rest if an NPC is in the room.

    Checks to see if an NPC has spawned between breathers.

    """

    if not check_for_npcs():

        while cur_hp_percent() < hp_thresh:

            if not check_for_npcs():

                c('rest')

                hp_percent = cur_hp_percent()

            else:

                break

    sleep(.5)

def get_exits(text):

    text = text.split('\r\n')

    for row in text:

        if 'An exit lies to the' in row:

            row = row.split('An exit lies to the ')[1].strip().replace('.','')

            return [row]

        if 'Exits lie to the' in row:

            row = row.split('Exits lie to the ')[-1].replace(', ',',').replace('.','').split(',')

            return row

def get_room():

    _ = tn.read_very_eager()
    c()
    plain_reply, ansi_reply = read_until()
    _ = tn.read_very_eager()

    return plain_reply

def troitian_in_room():

    possible_npcs = ['Skilled Scientist', 'Expert Chemist', 'Troitian Physicist']

    if debug: print("********************<TROITIAN_IN_ROOM()>*********************")

    room_text = get_room()

    if 'No lifeforms here' in room_text:
        return False

    if debug: print("ROOM TEXT: " + room_text)
    
    first_troitian = False

    for troitian in possible_npcs:

        if troitian in room_text:

            first_troitian = troitian

            break

    if debug: print("FIRST_TROITIAN: " + str(first_troitian))
    if debug: print("********************</TROITIAN_IN_ROOM()>*********************")

    return first_troitian

debug = False

def troitian_lab_bot():

    sl = .7

    while True:

        room_text = get_room()

        if debug:

            print("********************<ROOM TEXT>*********************")
            print(room_text)
            print("********************</ROOM TEXT>********************")

        if 'irid' in room_text:

            if debug: print("********************<GET IRID>********************")

            _ = tn.read_very_eager()

            c('get irid')

            plain_reply, ansi_reply = read_until()
            _ = tn.read_very_eager()

            print(ansi_reply)

            if flush: sys.stdout.flush()

            sleep(sl)

            if debug: print("********************</GET IRID>********************")

        if debug: print("********************<GET ROOM TITLE>********************")

        room_title = room_text.split('\r\n')[0].strip()

        if debug: print("ROOM TITLE: " + room_title)
        if debug: print("********************</GET ROOM TITLE>********************")


        match room_title:

            case 'Troitian Base, Sterile Hallway':
                  
                  e()
                  sleep(sl)


        if debug: print("********************<GET EXITS>********************")

        exits = get_exits(room_text)

        if debug: print("ROOM EXITS: " + str(exits))
        if debug: print("********************</GET EXITS>********************")

        match exits:

            case ['southwest']:

                  sw()
                  sleep(sl)

            case ['west', 'south', 'northeast']:

                  s()
                  sleep(sl)

            case ['north', 'south']:

                  s()
                  sleep(sl)

            case ['northwest', 'southwest', 'north']:

                  sw()
                  sleep(sl)

            case ['northeast']:

                  ne()
                  sleep(sl)

                  nw()
                  sleep(sl)

            case ['west', 'southwest', 'north', 'southeast']:

                  sw()
                  sleep(sl)

            case ['northwest', 'north', 'northeast']:

                  n()
                  sleep(sl)

            case ['west', 'north', 'south', 'east']:

                  n()
                  sleep(sl)

            case ['southwest', 'south']:

                  s()
                  sleep(sl)

                  e()
                  sleep(sl)

                  n()
                  sleep(sl)

            case ['south', 'east']:

                  e()
                  sleep(sl)

                  ne()
                  sleep(sl)

        if debug: print("********************<FIRST CURRENT TROITIAN>********************")

        current_troitian = troitian_in_room()

        if debug: print("CURRENT TROITIAN: " + str(current_troitian))

        if debug: print("********************</FIRST CURRENT TROITIAN>********************")

        if debug: print("********************<WHILE KILL TROITIAN>********************")

        while current_troitian:

            if debug: print("********************<INNER KILL TROITIAN>********************")

            _ = tn.read_very_eager()

            c('k ' + current_troitian)

            current_troitian = False

            plain_reply, ansi_reply = read_until()
            _ = tn.read_very_eager()

            print(ansi_reply)

            if flush: sys.stdout.flush()

            sleep(sl)

            if debug: print("********************</INNER KILL TROITIAN>********************")

            if debug: print("********************<INNER CURRENT TROITIAN>********************")

            current_troitian = troitian_in_room()

            if debug: print("CURRENT TROITIAN: " + str(current_troitian))
            if debug: print("********************</INNER CURRENT TROITIAN>********************")

            if 'irid' in plain_reply:

                if debug: print("********************<IRID DROP>********************")

                _ = tn.read_very_eager()

                c('get irid')

                plain_reply, ansi_reply = read_until()
                _ = tn.read_very_eager()

                print(ansi_reply)

                if flush: sys.stdout.flush()

                sleep(sl)
  
                if debug: print("********************</IRID DROP>********************")

        if debug: print("********************</WHILE KILL TROITIAN>********************")

        if debug: print("********************<CHECK REST>********************")

        if cur_hp_percent() < 70:

                  if debug: print("********************<REST>********************")

                  re()

                  if debug: print("********************</REST>********************")

        if debug: print("********************</CHECK REST>********************")


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

tn = telnetlib.Telnet("rock.fuzzem.com", port=4000)

login()

troitian_lab_bot()
