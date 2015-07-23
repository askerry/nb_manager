# nb_manager
tool kit for managing remote notebooks and port tunneling

###Components
- client.py
- server.py
- remote.py
- server_credentials.py

###Usage
##### view all active notebooks
python nb_manager/client.py aliasname view
##### connect to a new or existing notebook
python nb_manager/client.py aliasname connect
##### connect to notebook with specified port from specific directory
python nb_manager/client.py aliasname connect -p7000 -dProjects/cragcrunch 
##### shutdown all remote notebooks and clear their local ports
python nb_manager/client.py aliasname shutdown 
##### clear all local ports used by ssh tunels
python nb_manager/client.py aliasname clear

###Setup

- nb_manager needs to be installed on the local and remote machines
- on the remote server, nb_manager should be installed in an .ipython directory in the home directory
  - ssh myname@server.mit.edu
  - cd ~/.ipython
  - git clone https://github.com/askerry/nb_manager.git
- on the local server, install anywhere on python path
  - in the nb_manager directory, create a file called server_credentials.py
  - in this file, define a dictionary called aliases containing connection credentials for remote machines:
  - e.g. aliases = {'alias1':[hostname1, username1,password1], 'alias2':[hostname2, username2, password2]}
  
