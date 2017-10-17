
import logging
from miniboa import TelnetServer
from mush_commands import process_command,hide_player
from world import get_world
from player import *

IDLE_TIMEOUT = 300


WELCOME_MSG=[
    "\n*****************************************************************",
    "\n**                                                             **",
    "\n**                 ~~ Welcome to PyMud ~~                      **",
    "\n**                                                             **",
    "\n**     CREATE <Char Name> <Password> to create a character     **",
    "\n**   CONNECT <Char Name> <Password> to connect to a character  **",
    "\n**                                                             **",
    "\n*****************************************************************\n"]



_telnet_server = None


def on_connect(client):

    logging.info("Opened connection to {}".format(client.addrport()))


    get_player_manager().add_connection(client)

    client.send("Connecting from {}\n".format(client.addrport()))

    for line in WELCOME_MSG:
        client.send(line)

def on_disconnect(client):

    logging.info("Lost connection to {}".format(client.addrport()))
    for e in get_player_manager().get_connected_players():
        if e.client == client:
            hide_player(e.dbref)
            get_player_manager().remove_connection(e)
            return


def kick_idle():
   
    # Who hasn't been typing?
    for player in get_player_manager().get_connected_players():
        client = player.get_client()
        if client.idle() > IDLE_TIMEOUT:
            logging.info("Kicking idle lobby client from {}".format(client.addrport()))
            client.active = False


def process_clients():
    for player in get_player_manager().get_connected_players():
        client = player.get_client()
        if client.active and client.cmd_ready:
            msg = client.get_command()
            logging.info("{} says '{}'".format(client.addrport(), msg))
            process_command(player,msg)


def update_clients():

    _telnet_server.poll()
    kick_idle()
    process_clients()



def init_clients():

    global _telnet_server
    _telnet_server = TelnetServer(
        port=7777,
        address='',
        on_connect=on_connect,
        on_disconnect=on_disconnect,
        timeout = .05
        )

    logging.info("Listening for connections on port {}. CTRL-C to break.".format(_telnet_server.port))



