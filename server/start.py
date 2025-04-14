import subprocess
import os
import json
import random
import requests
import time
import Colors
class trx_status():
    def __init__(self):
        self.fail = 1
        self.success = 2
        self.pending = 0
trx_status_code = trx_status()
def main():
    f=open('server_info.json','r')
    info = json.load(f)
    f.close()
    f = open('server-conf.json','r')
    frs = f.read()
    config = json.loads(frs)
    f.close()
    hostname = config['hostname']
    if 'addr' not in config:
        exit('config address not found')
    elif config['addr'] == None or config['addr'] == "":
        exit('config address not found')
    for c in config:
        o = str(f" * {c}: {config[c]}")
        print(f'{o}')
    def check_p(l):
        try:
            r = requests.get(l)
            if r.status_code == 200:
                return True
            else:
                return False
        except:
            return False
    pending_transaction_dir = "files/pending.json"
    addresses_dir = "files/addresses.json"
    pool_dir = "files/pool_list.json"
    verified_dir = "files/verified.json"
    transaction_dir = "files/transactions.json"
    fpl = open(pool_dir,'r')
    jpl = json.load(fpl)
    fpl.close()
    def gen_id():
        l = 16
        keys = "1234567890abcdefghijklmnopqrstuvwxyz"
        output = ''.join(random.choices(keys,k=l))
        return output
    if info['id'] == None or not('id' in info) or info['id'] == "":
        info['id'] = gen_id()
        fw = open('server_info.json','w')
        json.dump(info,fw)
        fw.close()
    if config['is_pool'] == True:
        jpl[info['id']] = {'hostname':config['hostname'],'time':int(time.time() * 1000)}
    def update(i):
        jt = {}
        try:
            f = open(transaction_dir,'r')
            jt = json.load(f)
            f.close()
        except:
            pass
        ja = {}
        try:
            f = open(addresses_dir,'r')
            ja = json.load(f)
            f.close()
        except:pass
        jl = {}
        try:
            f = open(pool_dir,'r')
            jl = json.load(f)
            f.close()
        except:pass
        ld = f'{i}/pool_info'
        rd = requests.get(ld)
        if rd.status_code == 200:
            d = json.loads(rd.text)
            print(" * Syncing....")
            if 'pool_list' in d:
                nl = d['pool_list']
                for p in nl:
                    if p in jl:
                        if nl[p]['time'] > jl[p]['time']:
                            jl[p] = nl[p]
                        else:pass
                    else:
                        jl[p] = nl[p]
            if 'addresses' in d:
                na = d['addresses']
                faucet_addr = "py00000000000000000000000000000000000000000000000000000000000000000"
                for a in na:
                    if a in ja:
                        for t in na[a]['trx_h']:
                            if t in jt:
                                if na[a]['trx_h'][t]['time'] > jt[t]['time']:
                                    jt[t] = na[a]['trx_h'][t]
                                else:pass
                            else:
                                jt[t] = na[a]['trx_h'][t]
                            if t in ja[a]['trx_h']:
                                if na[a]['trx_h'][t]['time'] > ja[a]['trx_h'][t]['time']:
                                    ja[a]['trx_h'][t] = na[a]['trx_h'][t]
                                else:
                                    pass
                            else:
                                ja[a]['trx_h'][t] = na[a]['trx_h'][t]
                    else:
                        ja[a] = na[a]
                    ja[a]['balance'] = 0
                    for t in ja[a]['trx_h']:
                        if ja[a]['trx_h'][t]['from'] == faucet_addr:
                            ja[a]['balance'] = ja[a]['balance'] + ja[a]['trx_h'][t]["amount"]
                        elif ja[a]['trx_h'][t]['from'] == a:
                            if ja[a]['trx_h'][t]['status'] == trx_status_code.success:
                                ja[a]['balance'] = ja[a]['balance'] - ja[a]['trx_h'][t]['total']
                        else:
                            if ja[a]['trx_h'][t]['status'] == trx_status_code.success:
                                ja[a]['balance'] = ja[a]['balance'] + ja[a]['trx_h'][t]["amount"]
                        ja[a]['time'] = ja[a]['trx_h'][t]['time']
            f = open(transaction_dir,'w')
            json.dump(jt,f)
            f.close()
            f = open(addresses_dir,'w')
            json.dump(ja,f)
            f.close()
            f = open(pool_dir,'w')
            json.dump(jpl,f)
            f.close()
        else:
            pass
    if info['id'] in jpl:
        jpl.pop(info['id'])
    ch = []
    found = False
    if len(jpl) > 0:
        pl = []
        for x in jpl:
            pl.append(x)
        pool = random.choice(pl)
        pool_hostname = jpl[pool]['hostname']
        while not(check_p(pool_hostname)):
            if len(ch) >= len(jpl):
                print(f' * Pool Not Found')
                found = False
                break
            else:
                found = True
            if not(pool in ch):
                ch.append(ch)
            pool = random.choice(pl)
            pool_hostname = jpl[pool]['hostname']
        if check_p(pool_hostname):
            data_J = {'id':info['id'],'hostname':config['hostname'],'is_pool':config['is_pool'],'port':config['port']}
            data_s = json.dumps(data_J)
            l = f'{pool_hostname}/init?d={data_s}'
            rj = requests.get(pool_hostname)
            if rj.status_code ==200:
                d = json.loads(rj.text)
                jpl[d['id']] = {'hostname':config['pool'],'time':int(time.time() * 1000)}
            r=requests.get(l)
            d = {}
            if r.status_code == 200:
                    update(pool_hostname)
            else:
                pass
    if not(config['pool'] == "") or found == False:
        if check_p(config['pool']):
            data_J = {'id':info['id'],'hostname':config['hostname'],'is_pool':config['is_pool'],'port':config['port']}
            data_s = json.dumps(data_J)
            l = f'{config['pool']}/init?d={data_s}'
            rj = requests.get(config['pool'])
            if rj.status_code ==200:
                d = json.loads(rj.text)
                jpl[d['id']] = {'hostname':config['pool'],'time':int(time.time() * 1000)}
            r=requests.get(l)
            d = {}
            if r.status_code == 200:
                update(config['pool'])
                pass
            else:
                pass
    subprocess.run(f'TITLE py0_network: {info['id']}', shell=True)
    s1 = subprocess.Popen(["python", "py0_verification_node.py"], shell=True)
    if config['is_pool']:
        s2 = subprocess.Popen(["python","py0_pool.py"], shell=True)
try:
    main()
    print(f'{Colors.YELLOW} * PRESS CTRL+C TO CLOSE{Colors.END}')
except KeyboardInterrupt:
    pass
            