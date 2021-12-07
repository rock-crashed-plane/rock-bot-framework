"""

Simple bot framework for the Rock: Crashed Plane (fuzzem.com) MUD.

It supports running laps while killing NPCs, collecting loot, etc, in a loop.

This framework has no mapping ability.

Make sure the character starts in the right room.

Beware THE UNKNOWN. Beware exhaustion.

Your bot could smack into walls until he runs out of turns.

Or die!

"""

import telnetlib
import time

#### Start Configuration ###############################

user = ''
password = ''

# Take a breather if no npcs are in the room and hp below this threshold.
hp_thresh = 1200

# Default amount of time to sleep.
# Sleep commands are sprinkled throughout the code.
sleep_duration = .5

# Amount of cryl in room before loot is triggered.
loot_thresh = 250

#### End Configuration ###############################

def sleep(duration=None):

    """

    If no duration is specified, sleep for sleep_duration in configuration.

    """

    if duration == None:
        time.sleep(sleep_duration)
    else:
        time.sleep(sleep_duration)

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
    return read()

def login():

    """

    Login to the game with the user / password specified in the configuration.

    """

    time.sleep(2)

    reply = read()

    if '[E]nter Realm' in reply:
        reply = send_command('E')
        print(reply)

    if 'What is your fuzzem.com UserID' in reply:
        reply = send_command(user)
        print(reply)

    if 'password' in reply:
        reply = send_command(password)
        print(reply)

    time.sleep(3)

def kill_scientist():

    """

    Kill the first scientist in a room in the troitian lab.

    """

    reply = send_command()
    reply = reply.split('\r\n')

    killed = False

    for row in reply:

        if 'NPCs in room' in row:

            first_npc = row.replace('.','').split(': ')[1].split(', ')[0]

            k = 'kill ' + first_npc
            reply = send_command(k)
            print(reply)

            if 'flask of iridescent liquid' in reply:
                reply = send_command('get flask of iridescent liquid')
                print(reply)

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

        reply = send_command()
        reply = reply.split('\r\n')

        found_npcs = False
        for row in reply:
            if 'NPCs in room' in row:
                found_npcs = True

        if found_npcs:
            kill_scientist()
        else:
            npcs = False

def move(dir):

    reply = send_command(dir)
    print(reply)

def look():

    reply = send_command()
    print(reply)
    return reply

def inv():

    reply = send_command('i')
    print(reply)

def loot():

    """
    Gets cryl in room if over loot_thresh
    """

    reply = send_command()
    reply = reply.replace('\r\n','').replace('  ',' ').replace('  ',' ')
    reply = reply.split('cryl.')

    if len(reply) > 1:
        reply = reply[0]
        reply.strip()
        reply = reply.split(' ')
        reply = [i for i in reply if not i == '']
        cryl = int(reply[-1])

        if cryl > loot_thresh:

            reply = send_command('loot')
            print(reply)

def exit():

    reply = send_command('exit')
    print(reply)

def get_prompt():

    """

    Gets the current prompt, ie:

    >904/1392 64% 0/0 5929 67 118>

    Note that there is a trailing space.

    If multiple prompts are in the reply text, returns the most recent prompt.

    """

    def gp():

        reply = send_command()
        reply = reply.split('\r\n')
        reply = [i for i in reply if len(i)]
        reply = [i for i in reply if i[0] == '>']

        if len(reply):
            return reply[-1]
        else:
            return False

    reply = gp()

    # Try a second time if needed.
    if not reply:
        reply = gp()

    return reply

def cur_hp():

    """

    Returns an integer with your current number of turns.

    """

    reply = get_prompt()
    hp = int(reply.split(' ')[0].replace('>','').split('/')[0])
    return hp

def cur_turns():

    """

    Returns an integer with your current number of turns

    """

    reply = get_prompt()
    turns = int(reply.split(' ')[3])
    return turns

def check_for_npcs():

    """

    Returns True if there are NPCs in the room, otherwise, returns False.

    """

    reply = send_command()
    
    npc_text = [row for row in reply.split('\r\n') if 'NPCs in room' in row]

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

        hp = cur_hp()

        while hp < hp_thresh:

            if not check_for_npcs():

                reply = send_command('rest')
                print(reply)

                hp = cur_hp()

            else:
                break

            sleep()

    sleep()

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

    # Take a breather until hp over hp_thresh.
    re()

    # Look at the room and print the output.
    l()

def troitian_lab_bot():

    """

    Run laps around troitian laboratory.

    Collects iridescent vials.

    Assumes you start in ne corner of lab.

    Exits the game if you run out of turns.

    """

    def tick():
        troitian_lab_bot_tick()

    while True:
        tick();sw()
        tick();s()
        tick();s()
        tick();sw()
        tick();ne()
        tick();nw()
        tick();sw()
        tick();nw()
        tick();ne()
        tick();s()
        tick();e()
        tick();n()
        tick();e()
        tick();ne()

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
troitian_lab_bot()

