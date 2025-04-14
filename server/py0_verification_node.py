import json
import requests
import time
import random
print(" * Node Started")
class verification_codes():
    def __init__(self):
        self.fail = 1
        self.success = 2
verification_status = verification_codes()
verification_max = 10
verification_count = 1
f = open('server-conf.json','r')
frs = f.read()
config = json.loads(frs)
f.close()
f = open('server_info.json','r')
frs = f.read()
info = json.loads(frs)
f.close()
pending_transaction_dir = "files/pending.json"
addresses_dir = "files/addresses.json"
pool_dir = "files/pool_list.json"
verified_dir = "files/verified.json"
transaction_dir = "files/transactions.json"
checked = []
pool_hostname =""
class trx_status():
    def __init__(self):
        self.fail = 1
        self.success = 2
        self.pending = 0
trx_status_code = trx_status()
def check_j(v):
    try:
        json.loads(v)
        return True
    except:
        return False
def check_p(l):
    try:
        r = requests.get(l)
        if r.status_code == 200:
            return True
        else:
            return False
    except:
        return False
j_pending = {}
def get_pending(ln):
    global j_pending
    l = f"{ln}/get_pending"
    r = requests.get(l)
    if r.status_code == 200:
        try:
            n_p = json.loads(r.text)
            j_pending = n_p
        except:
            pass
    else:
        pass
def update(i):
    try:
        f = open(transaction_dir,'r')
        jt = json.load(f)
        f.close()
        f = open(addresses_dir,'r')
        ja = json.load(f)
        f.close()
        f = open(pool_dir,'r')
        jl = json.load(f)
        f.close()
        ld = f'{i}/pool_info'
        rd = requests.get(ld)
        if rd.status_code == 200:
            d = json.loads(rd.text)  
            print('Syncing....',i)
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
                up_t = False
                up_a = False
                na = d['addresses']
                faucet_addr = "py00000000000000000000000000000000000000000000000000000000000000000"
                for a in na:
                    if a in ja:
                        tn = list(na[a]['trx_h'])
                        tn_f = list(jt)
                        if ja[a]['time'] >= na[a]['trx_h'][tn[-1]]['time'] and ja[a]['balance'] >= na[a]['balance']:
                            if jt[tn_f[-1]]['time'] >= na[a]['trx_h'][tn[-1]]['time']:
                                pass
                            else:
                                for t in na[a]['trx_h']:
                                    if t in jt:
                                        if jt[t]['time'] >= na[a]['trx_h'][t]['time']:
                                            pass
                                        else:
                                            jt[t] = na[a]['trx_h'][t]
                                            up_t = True
                                    else:
                                        jt[t] = na[a]['trx_h'][t]
                                        up_t = True
                        else:
                            for t in tn:
                                if t in ja[a]['trx_h']:
                                    if ja[a]['trx_h'][t]['time'] >= na[a]['trx_h'][t]['time']:
                                        pass
                                    else:
                                        ja[a]['trx_h'][t] = na[a]['trx_h'][t]
                                        up_a = True
                                else:
                                    ja[a]['trx_h'][t] = na[a]['trx_h'][t]
                                    up_a = True
                            ja[a]['balance'] = 0
                            for t in ja[a]['trx_h']:
                                if t in jt:
                                    if jt[t]['time'] >= ja[a]['trx_h'][t]['time']:
                                        pass
                                    else:
                                        jt[t] = ja[a]['trx_h'][t]
                                        up_t = True      
                                else:
                                    jt[t] = ja[a]['trx_h'][t]
                                    up_t = True
                                if ja[a]['trx_h'][t]['from'] == faucet_addr:
                                    ja[a]['balance'] = ja[a]['balance'] + ja[a]['trx_h'][t]["amount"]
                                elif ja[a]['trx_h'][t]['from'] == a:
                                    if ja[a]['trx_h'][t]['status'] == trx_status_code.success:
                                        ja[a]['balance'] = ja[a]['balance'] - ja[a]['trx_h'][t]['total']
                                else:
                                    if ja[a]['trx_h'][t]['status'] == trx_status_code.success:
                                        ja[a]['balance'] = ja[a]['balance'] + ja[a]['trx_h'][t]["amount"]
                                ja[a]['time'] = ja[a]['trx_h'][t]['time']
                                up_a = True
                    else:
                        ja[a] = na[a]
                        ja[a]['balance'] = 0
                        for t in ja[a]['trx_h']:
                            if t in jt:
                                if jt[t]['time'] >= ja[a]['trx_h'][t]['time']:
                                    pass
                                else:
                                    jt[t] = ja[a]['trx_h'][t]
                                    up_t = True      
                            else:
                                jt[t] = ja[a]['trx_h'][t]
                                up_t = True
                            if ja[a]['trx_h'][t]['from'] == faucet_addr:
                                ja[a]['balance'] = ja[a]['balance'] + ja[a]['trx_h'][t]["amount"]
                            elif ja[a]['trx_h'][t]['from'] == a:
                                if ja[a]['trx_h'][t]['status'] == trx_status_code.success:
                                    ja[a]['balance'] = ja[a]['balance'] - ja[a]['trx_h'][t]['total']
                            else:
                                if ja[a]['trx_h'][t]['status'] == trx_status_code.success:
                                    ja[a]['balance'] = ja[a]['balance'] + ja[a]['trx_h'][t]["amount"]
                            ja[a]['time'] = ja[a]['trx_h'][t]['time']
                        up_a = True
                if up_t:
                    f = open(transaction_dir,'w')
                    json.dump(jt,f)
                    f.close()
                if up_a:
                    f = open(addresses_dir,'w')
                    json.dump(ja,f)
                    f.close()
            f = open(pool_dir,'w')
            json.dump(jl,f)
            f.close()
        else:
            pass
    except:
        pass
def verify_transaction():
    out_data = {}
    send_data = {}
    global j_pending
    try:
        fa = open(addresses_dir,'r')
        rs = fa.read()
        j_addresses= json.loads(rs)
        fa.close()
        fv = open(verified_dir,'r')
        rs = fv.read()
        j_verified = json.loads(rs)
        fv.close()
        if len(j_pending) >0:
            selection =""
            for x in j_pending:
                if x in j_verified:
                    pass
                else:
                    selection = x 
                    break
            if not(selection == "" or selection == " "):
                trx = j_pending[selection]
                out_data['trx_id'] = selection
                send_data['trx_id'] = selection
                send_data['addr'] = config['addr']
                from_addr = j_pending[selection]['from']
                to_addr = j_pending[selection]['to']
                if from_addr in j_addresses:
                    pass
                else:
                    send = f"{pool_hostname}/addrinfo?addr={from_addr}"
                    r = requests.get(send)
                    if r.status_code == 200:
                        ja = json.loads(r.text)
                        j_addresses[from_addr] = ja
                        f = open(addresses_dir,'w')
                        json.dump(j_addresses,f)
                        f.close()
                    else:
                        pass
                    pass
                if to_addr in j_addresses:
                    pass
                else:
                    send = f"{pool_hostname}/addrinfo?addr={to_addr}"
                    r = requests.get(send)
                    if r.status_code == 200:
                        ja = json.loads(r.text)
                        j_addresses[to_addr] = ja
                        f = open(addresses_dir,'w')
                        json.dump(j_addresses,f)
                        f.close()
                    else:
                        pass
                    pass
                if j_addresses[from_addr]['balance'] >= j_pending[selection]['total']:
                    out_data['verification_status'] = verification_status.success
                    send_data['verification_status'] = verification_status.success
                elif j_addresses[from_addr]['balance'] < j_pending[selection]['total']:
                    out_data['verification_status'] = verification_status.fail
                    send_data['verification_status'] = verification_status.fail
                    pass
                if check_p(pool_hostname):
                    chw = requests.get(f"{pool_hostname}/check_w")
                    if chw.status_code == 200:
                        dt = json.loads(chw.text)
                        if dt['status'] == True:
                            time.sleep(1)
                        else:
                            pass
                        if check_p(pool_hostname):
                            print(out_data)
                            j_verified[selection] = out_data
                            f= open(verified_dir,'w')
                            f.write(json.dumps(j_verified))
                            f.close()
                            sd = f"{pool_hostname}/update_pending?d={json.dumps(send_data)}"
                            rs = requests.get(sd)
                            if rs.status_code == 200:
                                pass
                            else:
                                pass
                        else:
                            print('Connection Lost')
                else:
                    if len(pool_hostname) > 0 or not(pool_hostname==""):
                        print('Connection Lost')
    except:
        pass
ms = 500
s = ms/1000
tm = 1000 * 10
ct = 0
def main():
    global start
    start = True
    while True:
        f = open(pool_dir,'r')
        jl = json.load(f)
        f.close()
        global ct,pool_hostname
        tn = int(time.time() * 1000)
        time.sleep(s)
        if info['id'] in jl:
            jl.pop(info['id'])
        pool_hostname = ""
        found = True
        ch = []
        if len(jl)>0:
            pl = []
            for x in jl:
                pl.append(x)
            pool = random.choice(pl)
            pool_hostname = jl[pool]['hostname'] 
            while not(check_p(pool_hostname)):
                if len(ch) >= len(jl):
                    found = False
                    break
                else:
                    found = True
                    pass
                if not(pool in ch):
                    ch.append(ch)
                pool = random.choice(pl)
                pool_hostname = jl[pool]['hostname']
        elif not(config['pool'] == "") and check_p(config['pool']):
            pool_hostname = config['pool']
        if check_p(pool_hostname) and not(pool_hostname == ""):
            if ct >= tm:
                update(pool_hostname)
                ct = 0
            elif start == True:
                start = False
                update(pool_hostname)
            if len(pool_hostname) > 0 or not(pool_hostname==""):
                get_pending(pool_hostname)
            verify_transaction()
        ct += int(time.time() * 1000) - tn 
try:
    main()
except KeyboardInterrupt:
    pass