import os
import json
import sys
import getopt
import subprocess


def fetch_nb_server_data(profile='default', printit=True):
    homedir = execute_local_shell('echo $HOME').strip()
    homedir = os.path.join(homedir, '.ipython/profile_%s/security/' % profile)
    nbservers = [os.path.join(homedir, f)
                 for f in os.listdir(homedir) if f[:8] == 'nbserver']
    nb_data = []
    for f in nbservers:
        with open(f) as j:
            j = json.load(j)
            try:
                pid = j['pid']
            except:
                pid = int(f[f.index('-') + 1:-5])
                j['pid'] = pid
            nb_data.append(j)
    if printit:
        for n in nb_data:
            print '\n'.join(
                ['url: %s' % n['url'], 'pid: %s' % pid, 'port: %s' % n['port'], 'notebook_dir: %s' % n['notebook_dir'], 'hostname: %s' % n['hostname'], '\n'
                 ])
    return nb_data


def execute_local_shell(command):
    stream = os.popen(command)
    output = stream.read()
    stream.close()
    return output


def check_port_is_free(port):
    if len(execute_local_shell("lsof -i :%s | grep LISTEN" % port)) == 0:
        return True
    return False


def kill_nb(nb_pid, profile='default'):
    os.system("kill %s" % nb_pid)
    os.system("rm ~/.ipython/%s/security/nbserver-%s.json" % (profile, nb_pid))


def create_nb_on_port(port=7000, directory=None, profile=None):
    if check_port_is_free(port):
        initial_dir = os.getcwd()
        if directory is not None:
            try:
                os.chdir(directory)
            except:
                pass
        subprocess.Popen(
            ["ipython", "notebook", '--port', '%s' % port, '--profile', profile], stdout=None, shell=False)
        os.chdir(initial_dir)
        return True
    else:
        return False


def delete_all_nb_servers(port_exceptions=None, profile='default'):
    servers = fetch_nb_server_data(printit=False)
    if servers is not None:
        if port_exceptions is None:
            port_exceptions = []
        ports_to_free = []
        for server in servers:
            if server['port'] not in port_exceptions:
                ports_to_free.append(server['port'])
                kill_nb(server['pid'], profile=profile)
        return ports_to_free
    else:
        print "No notebook servers are running on %s." % hostname
    return []


def create_new_nb(port=7000, directory=None, profile=None):
    connected = False
    port = port - 1
    while not connected:
        port += 1
        connected = create_nb_on_port(port, directory, profile)
    return port

if __name__ == '__main__':
    status = sys.argv[1]
    if len(sys.argv) > 2:
        args, unnamed = getopt.getopt(sys.argv[2:], 'p:d:u:')
    else:
        args = []
    initial_port = 7100
    directory = None
    ipython_profile = 'default'
    for a, arg in args:
        if a == "-p":
            initial_port = int(arg)
        if a == "-d":
            if arg == 'None':
                directory = None
            else:
                directory = arg
        if a == '-u':
            ipython_profile = arg
    if status == 'launch':
        result = create_new_nb(
            port=initial_port, directory=directory, profile=ipython_profile)
    elif status == 'check':
        result = fetch_nb_server_data(
            profile=ipython_profile, printit=False)
    elif status == 'killall':
        result = delete_all_nb_servers(
            port_exceptions=None, profile=ipython_profile)
    print result
