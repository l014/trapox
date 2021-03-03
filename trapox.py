#!/usr/bin/python3.9
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import os,requests,json,sys,urllib.request,socket,subprocess,shlex,time 
import threading,random   


#   generate traffic to url(s) 
#   using public proxys list from proxysan.io

#           curl reminders
#           -L / --location set to -1 to follow all redericts
#           -x, --proxy [protocol://]host[:port] 



# returns a proxy ip:port:type
def Proxy():
    url = 'https://www.proxyscan.io/api/proxy?level=anonymous&ping=100&format=json'
    try:
        resp = requests.get(url)
        jstr = json.dumps(resp.json())
        resp = json.loads(jstr)
        ipv4 = resp[0]['Ip'].strip()
        stype = str(resp[0]['Type'][0]).strip()
        port = str(resp[0]['Port']).strip()
        proxy=str(ipv4)+":"+str(port)
        return [proxy,stype]
    except:
        return 1

# make request     
def proxReq(plist,url,ua,ptype):
    # if socks4/5 set --socks5-hostname gets proxy to resolv hostname
    ua=ua.replace('"','') # clean ua

    for proxy in plist:
        if 'socks5' in ptype:
            run = 'curl -X GET -L -1 -i --connect-timeout 400 --max-time 450 --socks5-hostname -x "' + ptype.lower() +'://' + proxy + '" -H "user-agent:' + ua + '" "' + url + '"'
        if 'socks4' in ptype:
            run = 'curl -X GET -L -1 -i --connect-timeout 400 --max-time 450 --socks4-hostname -x "' + ptype.lower() +'://' + proxy + '" -H "user-agent:' + ua + '" "' + url + '"'
        if 'socks4' not in ptype or 'socks5' not in ptype: # http / https should resolve hostname o_O
            run = 'curl -X GET -L -1 -i --connect-timeout 400 --max-time 450  -x "' + ptype.lower() +'://' + proxy + '" -H "user-agent:' + ua + '" "' + url + '"'
        args = shlex.split(run)
        try:
            subprocess.Popen(args)
        except:
            print('err.req ') 
        time.sleep(1)


def setup(plist,ptype,threads):

    urls=[''] # set url's
    
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    
    with open(plist) as f:
        plist = f.readlines()        
    
    plist = [ x.strip() for x in plist ]     
    print('[+] number of proxys in list: ', len(plist))
       
    # splitting the list in parts for threading
    n=int(len(plist)/threads)
    plist = [plist[i * n:(i + 1) * n] for i in range((len(plist) + n - 1) // n )] 
    
    # list to hold started threads
    tlist=[]
    for t in range(0,threads):
        # Get Random User Agent String.
        ua = user_agent_rotator.get_random_user_agent()
        print("[+] Starting thread ", t+1)
        url = random.choice(urls)
        thread=threading.Thread(None,proxReq,None,(plist[t],url,ua,ptype))
        thread.start()
        
    print('\n\n'+'#'*70)
    print('\n[+] First list finished')
    time.sleep(3)


def wait(dp):
    print('[i] waiting for download ..\n')
    time.sleep(4)
    checkDownload(dp)
    
    
def checkDownload(dp):
        if dp is None:  # subproc not finished  sleep()
            wait(dp)
        print('[+] download done')
        
                    
def banner():
    os.system('clear')
    banner = '''
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMNNmdddhhhhhdddmNNMMMMMMMMMMMMMM
    MMMMMMMMMMmmhhhhhdddddhddhhhhhhhdmMMMMMMMMMMM
    MMMMMMMMmhyhhhhdNMMMMMMMNNmhhhhhhhhdNMMMMMMMM
    MMMMMMmhhhhhhhdMMMMMMMNdhhhhhhhhhhhhhhmMMMMMM
    MMMMMdhhhhhhhdNMMMMMMMdhhhhhhhhhhhhhhhhmMMMMM
    MMMNhhhhhhhhhmMMMMMMMMMmdhhhhhhhhhhhhhhhdNMMM
    mMNhhhhhhhhhmMMMMMMMMMMMMNmhhhhhhhhhhhhhhdMMM
    dMmhhhhhhhhhMMMMMMMMMMMMMMMNhhhhhhhhhhhhhhNMM
    MNhhhhhhhhhhMMMMMMMMMMMMMMMMdhhhhhhhhhhhhhmMM
    MNhhhhhhhhhhmMMMMMMMMMMMMMMMNhhhhhhhhhhhhhhNM
    MNhhhhhhhhhhhmMMMMMMMMMMMMMMMmhhhhhhhhhhhhhNM
    MNhhhhhhhhhhhhmMMMMMMMMMMMMMMNhhhhhhhhhhhhmMM
    MMdhhhhhhhhhhhhmMMMMMMMMMMMMMMdhhhhhhhhhhhNMM
    MMNhhhhhhhhhhhhhdMMmhdmNMMMMMMmhhhhhhhhhhdMMM
    MMMNhhhhhhhhhhhhhNNdhhhhhdNMMMMNdhhhhhhhdNMMM
    MMMMMhhhhhhhhhhhdmhhhhhhhhNmMMMMMNhhhhhhMMMMM
    MMMMMMmhhhhhhddmNhhhhhhdddNmhmNMMMdhhhmMMMMMM
    MMMMMMMMmhhhdddmmmmhhhhhhdddhhhhdhhdNMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    '''
    print(banner)
    print('\n\ttrapox beta\n\t')

def main():
    banner()
    psUrl = 'https://www.proxyscan.io/download?type='
    proxylists=['socks5','https','socks4','http']
    threads=input('[?] set number of threads\n>')
    threads=int(threads)
    
    
    for plist in proxylists:
        print('[+] downloading proxylist type ', plist)
        psUrl+=plist
        dp = subprocess.Popen(['wget','--show-progress', '-q', '-O', plist, psUrl]) 
        if dp is None:  # subproc not finished  sleep()
            wait(dp)
        else:
            print('[+] download done')
            ptype=str(plist)
            if ptype == 'https':
                ptype = 'http'
            time.sleep(2)
            print('[i] checking file: ', plist)
            #fc = subprocess.Popen(['type', plist]) # if exists continue
            setup(plist,ptype,threads)
            

if __name__ == '__main__':
    main()    
    
    
    
