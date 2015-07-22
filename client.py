import remote
import os
import sys
import json
import getopt
from server_credentials import aliases


def list_remote_nbs(hostname, username=None, password=None, ipython_profile='default'):
    if hostname in aliases:
        hostname, username, password = aliases[hostname]
    with remote.Ssh_Connect(hostname, username, password) as ssh:
        remote_command = 'python .ipython/nb_manager/server.py check -u%s' % ipython_profile
        #print remote_command
        output=ssh.execute(remote_command, printit=False)
        try:
            servers = eval(output[1])
        except:
            print "Unable to complete transaction:"
            print '\n'.join(output[1:])
    if len(servers) > 0:
        print "Found existing notebook servers on %s." % hostname
        for i, server in enumerate(servers):
            print "   #%s: %s from %s (pid=%s)" % (i, server['url'], server['notebook_dir'], server['pid'])
        return servers
    else:
        print "No notebook servers are running on %s." % hostname


def connect_to_nb(hostname, username=None, password=None, port=7000, directory=None, ipython_profile='default'):
    if hostname in aliases:
        hostname, username, password = aliases[hostname]
    servers = list_remote_nbs(hostname, username, password, ipython_profile)
    new_connection = True
    if servers is not None:
        print "Would you like to connect to one of these? Enter notebook # to tunnel to existing notebook, enter 'n' to create and tunnel to a new notebook."
        user_input = raw_input()
        try:
            choice = servers[int(user_input)]
            print "Joining notebook on port %s" % choice['port']
            new_connection = False
            share_nb_port(hostname, username, choice['port'])
        except:
            if user_input in ('n', 'N', 'new', 'New'):
                print "Creating new notebook."
            else:
                print "Invalid input. Exiting notebook manager."
                new_connection = False
    if new_connection:
        created_port = launch_remote(
            hostname, username, password, port=port, directory=directory, ipython_profile=ipython_profile)
        share_nb_port(hostname, username, created_port)


def share_nb_port(hostname, username=None, port=7000):
    if hostname in aliases:
        hostname, username, password = aliases[hostname]
    local_command = "ssh %s@%s -f -N -L %s:127.0.0.1:%s" % (
        username, hostname, port, port)
    #print local_command
    os.system(local_command)


def launch_remote(hostname, username=None, password=None, port=7000, directory=None, ipython_profile=None):
    if hostname in aliases:
        hostname, username, password = aliases[hostname]
    with remote.Ssh_Connect(hostname, username, password) as ssh:
        remote_command = "python .ipython/nb_manager/server.py launch -p%s -d%s -u%s" % (
            port, directory, ipython_profile)
        #print remote_command
        output = ssh.execute(remote_command)
        port = "unknown"
        for o in output:
            try:
                port = int(o.strip())
            except:
                pass
        print "Launching remote notebook on port %s." % port
        return port


def clear_port(port_number):
    "Clearing the following ports:"
    remote.kill_processes_by_port(port_number)


def get_list_remote_ports(hostname, username, password, ipython_profile="proile_default"):
    servers = list_remote_nbs(hostname, username, password, ipython_profile)
    if servers is not None:
        return [server['port'] for server in servers]
    return []


def shut_down_local_tunnels(hostname, username=None, password=None, ipython_profile="proile_default"):
    if hostname in aliases:
        hostname, username, password = aliases[hostname]
    ports = get_list_remote_ports(
        hostname, username, password, ipython_profile)
    for p in ports:
        clear_port(p)
    if len(ports) > 0:
        print "Shut down local tunneling through the following ports: %s" % ', '.join([str(p) for p in ports])
    else:
        print "No open tunnels to %s identified" % hostname


def shut_down_remote_nbs(hostname, username=None, password=None, ipython_profile=None):
    if hostname in aliases:
        hostname, username, password = aliases[hostname]
    with remote.Ssh_Connect(hostname, username, password) as ssh:
        remote_command = "python .ipython/nb_manager/server.py killall -u%s" % ipython_profile
        #print remote_command
        output = ssh.execute(remote_command)
        print "Shutting down all remote notebooks on %s." % hostname
        for o in output:
            if len(o) > 0 and o[0] == '[' and isinstance(eval(o), list):
                ports = eval(o)
        return ports


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Must provide server connections (hostname, username, password) or a recognized connection alias."
        raise ValueError
    args = []
    if sys.argv[1] in aliases:
        hostname, username, password = aliases[sys.argv[1]]
        status = sys.argv[2]
        if len(sys.argv) > 3:
            args, unnamed = getopt.getopt(sys.argv[3:], 'p:d:u:')
    else:
        hostname = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]
        status = sys.argv[4]
        if len(sys.argv) > 5:
            args, unnamed = getopt.getopt(sys.argv[5:], 'p:d:u:')
    initial_port = 7100
    directory = None
    ipython_profile = 'default'
    for a, arg in args:
        if a == "-p":
            initial_port = arg
        if a == "-d":
            directory = arg
        if a == '-u':
            ipython_profile = arg
    if status == 'connect':
        connect_to_nb(hostname, username, password, port=initial_port,
                      directory=directory, ipython_profile=ipython_profile)
    elif status == 'view':
        list_remote_nbs(
            hostname, username, password, ipython_profile=ipython_profile)
    elif status == 'clear':
        shut_down_local_tunnels(
            hostname, username, password, ipython_profile=ipython_profile)
    elif status == 'shutdown':
        ports_to_clear = shut_down_remote_nbs(
            hostname, username, password, ipython_profile=ipython_profile)
        for p in ports_to_clear:
            clear_port(p)
    else:
        "Please provide a valid client operation (connect, view, clear, shutdown)."
