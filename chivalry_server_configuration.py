# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 14:06:23 2017

@author: MrFDA
"""

import os,sys,json,re,shutil,zipfile,urllib2,random,subprocess,platform
from optparse import OptionParser
from tempfile import mkdtemp

def parseOpts(argv):
    description = 'Configure Chivalry dedicated server'
    parser = OptionParser(description)
    parser.add_option('-c', '--conf', dest='jason_conf',
        metavar = 'FILE', action='store', default = None,
        help='jason configuration file')
    parser.add_option('-m', '--maps', dest='map_list',
        metavar = 'FILE', action='store',
        default = 'MapList.txt',
        help='File containing the list of maps (default : MapList.txt)')
    parser.add_option('-s', '--skip', dest='skip_update',
        metavar = 'ATTR', action='store',
        default = 'F',
        help='Should the update of the server be skipped ? (default : F)')
    return parser, parser.parse_args(argv)


def execute(cmd,shell=False): #stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running#answer-4418193
    process = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() is not None:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
        return output
#    else:
#        raise subprocess.ProcessException(cmd, exitCode, output)


def json_load(fname):
    with open(fname,'r') as f:
        s = f.read()
    s = s.replace("\\", "\\\\")
    data = json.loads(s)
    return data

def load_maps(path):
    maps = []
    with open(path, 'r') as f:
            for ln in f:
                ln = ln.strip()
                if not (ln=='' or ln[0]==";"):
                    maps.append(ln)
    return maps

def map_filter(map_list,map_types):
    available_map_types = ['TO', 'LTS', 'CTF', 'Duel', 'FFA', 'KOTH', 'TD']
    type_filter = []
    for e in map_types:
        f = e.strip()
        if f in available_map_types:
            type_filter.append('AOC' + f)
    type_filter = tuple(type_filter)
    maps = [x for x in map_list if x.startswith(type_filter)]
    return maps
    
def map_exclude(map_list,exclude_list):
    maps = []
    for e in map_list:
        if e not in exclude_list:
            maps.append(e)
    return maps

def ini_parser(path):
    data = {}
    activeKey = ''
    with open(path, 'r') as f:
        for ln in f:
            ln = ln.strip()
            if not (ln=='' or ln[0]==";"):
                if ln[0]=='[':
                    keyName = ln[1:-1]
                    activeKey = keyName
                    data[keyName]={}
                else:
                    if not activeKey=='':
                        option = re.split(r'=',ln,1)
                        option_name = option[0]
                        option_value = option[1]
                        if not option_name in data[activeKey]:
                            data[activeKey][option_name] = [option_value]
                        else:
                            data[activeKey][option_name].append(option_value)
    return data

def write_unparsed(data,fname):
    with open(fname,'wb') as f:
        for i,section in enumerate(data):
            if i==0:
                f.write('[' + section + ']\n')
            else:
                f.write('\n[' + section + ']\n')
            for option in data[section]:
                if isinstance(data[section][option],basestring):
                    f.write(option + '=' + data[section][option] + '\n')
                else:
                    for value in data[section][option]:
                        f.write(option + '=' + value + '\n')


def file_download(url,path=''): # http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python#answer-22776
    file_name = url.split('/')[-1]
    file_name = os.path.join(path,file_name)
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
    
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
    
    f.close()
    return file_name

def int_control(int_as_string,min_value,max_value):
    x = int(int_as_string)
    if x<min_value:
        x=min_value
    if x>max_value:
        x=max_value
    x=str(x)
    return x

def install_steamcmd(path):
    url = 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip'
    tmp_dir = mkdtemp()
    fname = file_download(url,tmp_dir)
    with zipfile.ZipFile(fname,"r") as zip_ref:
        zip_ref.extractall(path)
    shutil.rmtree(tmp_dir)
    cmd = os.path.join(path,"steamcmd.exe" + " +quit")
    execute(cmd)
    

def install_validate_server(cmd_path,srv_dir,app_nb=220070):
    cmd = '"' + os.path.join(cmd_path,"steamcmd.exe") + '" +login anonymous +force_install_dir ./' + srv_dir + '/ +app_update ' + str(app_nb) + ' validate +quit'
    execute(cmd)

def server_launch(udk_fname,rand_map):
    cmd = udk_fname + ' ' + rand_map + '?steamsockets -seekfreeloadingserver'
    execute(cmd)

def main():
    parser, (options, args) = parseOpts(sys.argv)
    
    print "Welcome in MrFDA's quick server configuration script"
    
    if options.jason_conf:
        conf_fname = os.path.normpath(options.jason_conf)
    else:
        conf_fname = 'ServerConfig.json'
    if os.path.exists(conf_fname):
        param = json_load(conf_fname)
    else:
        print "Error: %s not found"%(conf_fname)
        raise ValueError("The file containing parmameters doesn't exist (or you misspelled its name)")
    
    if options.map_list:
        map_list_fname = os.path.normpath(options.map_list)
    else:
        map_list_fname = 'MapList.txt'
    if os.path.exists(map_list_fname):
        map_list = load_maps(map_list_fname)
    else:
        print "Error: %s not found"%(map_list_fname)
        raise ValueError("The file containing the list of maps doesn't exist (or you mispelled its name)")
    
    if options.skip_update:
        skip_update = options.skip_update
    else:
        skip_update= 'F'
    if skip_update=='T':
        skip_update = True
    else:
        skip_update = False

    param['SteamCMD'] = os.path.normpath(param['SteamCMD'])
    param['ServerDir'] = os.path.normpath(param['ServerDir'])
    param['GoreLevel'] = int_control(param['GoreLevel'],0,2)
    param['MaxPlayers'] = int_control(param['MaxPlayers'],1,64)
    if param['bAutoBalance'] not in ['true','false']:
        param['bAutoBalance'] = 'true'
    maps = map_filter(map_list,param['MapTypes'])
    maps = map_exclude(maps,param['MapExclude'])
    if len(maps)<1:
        raise ValueError("At least one map should be selected, verify the types of maps you entered and the maps you excluded")
    random.shuffle(maps)
    
    srv_path =  os.path.join(param['SteamCMD'],param['ServerDir'])
    archi = platform.architecture()[0]
    if archi=='32bit':
        udk_fname = os.path.join(srv_path,'Binaries','Win32','UDK.exe')
    elif archi=='64bit':
        udk_fname = os.path.join(srv_path,'Binaries','Win64','UDK.exe')
    else:
        raise ValueError("It seems that your not using a 32 of 64 bit system")
    config_path = os.path.join(srv_path,'UDKGame','Config')
    pcserver_fname = os.path.join(config_path,'PCServer-UDKGame.ini')
    pcserver_bkup_fname = os.path.join(config_path,'PCServer-UDKGame_backup.ini')
    
    if not os.path.exists(os.path.join(param['SteamCMD'],'steamcmd.exe')):
        print 'SteamCMD not found: downloading and installing it'
        install_steamcmd(param['SteamCMD'])
    
    if not os.path.exists(udk_fname):
        print 'Downloading and installing the dedicated server'
        install_validate_server(param['SteamCMD'],param['ServerDir'])
    else:
        if not skip_update:
            print 'Updating the dedicated server'
            install_validate_server(param['SteamCMD'],param['ServerDir'])
    
    if not os.path.exists(pcserver_bkup_fname):
        print 'Creating a backup of the existing configuration file'
        shutil.copy2(pcserver_fname,pcserver_bkup_fname)
    
    print 'Reading configuration file'
    config = ini_parser(pcserver_fname)
    
    print 'Upgrading configuration file'
    config['Engine.GameReplicationInfo']['ServerName'] = param['ServerName']
    config['Engine.AccessControl']['GamePassword'] = param['GamePassword']
    config['Engine.AccessControl']['AdminPassword'] = param['AdminPassword']
    config['Engine.GameInfo']['MaxPlayers'] = param['MaxPlayers']
    config['Engine.GameInfo']['GoreLevel'] = param['GoreLevel']
    config['AOC.AOCGame']['bAutoBalance'] = param['bAutoBalance']
    config['AOC.AOCGame']['Maplist'] = maps
    write_unparsed(config,pcserver_fname)
    
    print 'Launching the server'    
    server_launch(udk_fname,random.choice(maps))

if __name__ == '__main__' :
    if platform.system()=="Windows":
        main()
    else:
        print 'This script is intended to be used on Windows platform only'