import os
import pxssh
import pysftp

################################
# #####  Connections    #######
################################

class Ssh_Connect():

    '''ssh connection context manager'''

    def __init__(self, hostname, username, password):
        self.ssh = pxssh.pxssh()
        self.hostname = hostname
        self.username = username
        self.password = password

    def __enter__(self):
        self.ssh.login(self.hostname, self.username, self.password)
        return self

    def __exit__(self, type, value, traceback):
        self.ssh.logout()

    def execute(self, command, printit=True):
        printit=True
        self.ssh.sendline(command)
        self.ssh.prompt()
        output=self.ssh.before
        if printit:
            return output.split('\n')

    def run(self, filepath, language='bash'):
        self.execute('%s %s' % (language, filepath))


class Sftp_Connect():

    '''sftp connection context manager'''

    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password

    def __enter__(self):
        self.sftp = pysftp.Connection(
            host=self.hostname, username=self.username, password=self.password)
        print "%s signing in from %s" % (self.username, os.getcwd())
        print "connected to %s in %s" % (self.hostname, self.sftp.execute('pwd')[0])
        return self

    def __exit__(self, type, value, traceback):
        self.sftp.close()

    def execute(self, command, printit=True):
        if printit:
            print self.sftp.execute(command)
        else:
            self.sftp.execute(command)
            

    def get(self, path):
        filename = os.path.basename(path)
        print "fetching %s from %s to %s on local" % (path, os.path.join(os.getcwd(), filename), self.hostname)
        self.sftp.get(path)

    def put(self, path, put_directory=None):
        cwd = self.sftp.execute('pwd')[0]
        if put_directory is not None:
            self.sftp.execute('cd %s' % put_directory)
        filename = os.path.basename(path)
        print "putting %s to %s at %s" % (os.path.abspath(path), os.path.join(self.sftp.execute('pwd')[0], filename), self.hostname)
        self.sftp.put(path)
        self.sftp.execute('cd %s' % cwd)


def shell_wrapper(hostname, username, password, print_command, execution_command):
    if hostname is None:
        print execute_local_shell(print_command)
        output = execute_local_shell(execution_command)
    else:
        with Ssh_Connect(hostname, username, password) as ssh:
            ssh.execute(print_command)
            output = ssh.execute(execution_command)
    return output

################################
# ##### Misc Operations #######
################################

def kill_all_ipython(hostname=None, username=None, password=None):
    print_command = "lsof -i|grep ipython"
    execution_command = "lsof -i|grep ipython| awk '{print $2}'| xargs kill -9"
    output = shell_wrapper(
        hostname, username, password, print_command, execution_command)


def kill_all_processes_by_name(process_name, hostname=None, username=None, password=None):
    print_command = "ps ax| grep %s" % process_name
    execution_command = "ps ax| grep %s | awk '{print $1}'| xargs kill -9" % process_name
    output = shell_wrapper(
        hostname, username, password, print_command, execution_command)


def kill_processes_by_port(port_number, hostname=None, username=None, password=None):
    print_command = "lsof -i:%s | grep LISTEN" % port_number
    execution_command = "lsof -i TCP:%s | grep LISTEN | awk '{print $2}' | xargs kill -9" % port_number
    output = shell_wrapper(
        hostname, username, password, print_command, execution_command)


def execute_local_shell(command):
    stream = os.popen(command)
    output = stream.read()
    stream.close()
    return output
