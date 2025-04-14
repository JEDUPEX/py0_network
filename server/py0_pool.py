import requests
import json
from flask import Flask, request
import py0_core
import random
import time
import logging
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)
verification_max = 10
class verification_codes():
    def __init__(self):
        self.fail = 1
        self.success = 2
verification_status = verification_codes()
pending_transaction_dir = "files/pending.json"
addresses_dir = "files/addresses.json"
pool_dir = "files/pool_list.json"
verified_dir = "files/verified.json"
transaction_dir = "files/transactions.json"
f = open('server-conf.json','r')
config = json.load(f)
f.close()
f=open('server_info.json','r')
info = json.load(f)
f.close()
C_Working = False
def check_j(dr):
    try:
        fj = open(dr,'r')
        o = json.load(fj)
        fj.close()
        return True , o
    except:
        return False,{}
def check_p(l):
    try:
        r = requests.get(l)
        if r.status_code == 200:
            return True
        else:
            return False
    except:
        return False
class trx_status():
    def __init__(self):
        self.fail = 1
        self.success = 2
        self.pending = 0
trx_status_code = trx_status()
def gen_trx_id():
    keys = '0123456789'
    l = 32
    output = "tx"
    for x in range(l):
        output+=random.choice(keys)
    return output
@app.route('/', methods=['POST','GET'])
def home():
    f=open('server_info.json','r')
    output = json.load(f)
    f.close()
    return f"{json.dumps(output)}" , 200
@app.route('/get_gas',methods=['POST','GET'])
def get_gas():
    amount = 0
    out = {}
    if request.method == 'POST':
        amount = request.form['amount']
    elif request.method == 'GET':
        amount = request.args['amount']
    amount = float(amount)
    out['gas'] = amount/verification_max
    return f'{json.dumps(out)}',200
@app.route('/init', methods=['POST','GET'])
def init():
    output = {}
    f=open('server_info.json','r')
    fr = json.load(f)
    f.close()
    f=open(pool_dir,'r')
    pr = json.load(f)
    f.close()
    if request.method == 'POST':
        d = json.loads(str(request.form['d']))
        id = d['id']
        hostn = d['hostname']
        is_pool = d['is_pool']
        port = d['port']
        if id == fr['id']:
            pass
        else:
            if id in fr['connections']:
                pass
            else:
                fr['connections'][id] = "0"
                f=open('server_info.json','w')
                json.dump(fr,f)
                f.close()
            if is_pool == True:
                h = hostn
                if hostn == "" or hostn == None:
                    h = f"http://{request.remote_addr}:{port}"
                else:
                    pass
                pr[id] = {'hostname':h,'time':int(time.time() * 1000)}
                f=open(pool_dir,'w')
                json.dump(pr,f)
                f.close()
    elif request.method == 'GET':
        d = json.loads(str(request.args['d']))
        id = d['id']
        hostn = d['hostname']
        is_pool = d['is_pool']
        port = d['port']
        if id == fr['id']:
            pass
        else:
            if id in fr['connections']:
                pass
            else:
                fr['connections'][id] = "0"
                f=open('server_info.json','w')
                json.dump(fr,f)
                f.close()
            if is_pool == True:
                h = hostn
                if hostn == "" or hostn == None:
                    h = f"http://{request.remote_addr}:{port}"
                else:
                    pass
                pr[id] = {'hostname':h,'time':int(time.time() * 1000)}
                f=open(pool_dir,'w')
                json.dump(pr,f)
                f.close()
    output['id'] = info['id']
    return f"{json.dumps(output)}" , 200
@app.route('/get_pending', methods=['POST','GET'])
def get_pending():
    f = open(pending_transaction_dir,'r')
    output = f.read()
    f.close()
    return f"{output}",200
@app.route('/check_w', methods=['POST','GET'])
def check_w():
    global C_Working
    out = {}
    out['status'] = C_Working
    return f"{json.dumps(out)}",200
@app.route('/update_pending', methods=['POST','GET'])
def update_pending():
    global C_Working
    C_Working = True
    try:
        f = open(pending_transaction_dir,'r')
        j = json.load(f)
        f.close()
        f = open(addresses_dir,'r')
        ja = json.load(f)
        f.close()
        trx_id = ""
        v_address = "py00000000000000000000000000000000000000000000000000000000000000000"
        vr_status = verification_status.success
        ti = int(time.time() * 1000)
        if request.method == 'POST':
            d = json.loads(str(request.form['d']))
            trx_id = d['trx_id']
            vr_status = d['verification_status']
            v_address = d['addr']
            pass
        if request.method == 'GET':
            d = json.loads(str(request.args['d']))
            trx_id = d['trx_id']
            vr_status = d['verification_status']
            v_address = d['addr']
            pass
        if trx_id in j:
            verifications = j[trx_id]['verifications']
            verifications += 1
            trx_amount = j[trx_id]['amount']
            trx_gas = j[trx_id]['gas']
            if v_address in ja:
                pass
            else:
                ja[v_address] = {"balance":0,"trx_h":{},'time':ti}
            v_id = gen_trx_id()
            ja[v_address]['time'] = ti
            faucet_addr = "py00000000000000000000000000000000000000000000000000000000000000000"
            trx_o = {'from':faucet_addr,'to':v_address,'amount':(trx_gas/(verification_max)),'time':ti}
            ja[v_address]['trx_h'][v_id] = trx_o
            #m
            j[trx_id]['verifications'] = verifications
            j[trx_id]['time'] = ti
            from_addr = j[trx_id]['from']
            to_addr = j[trx_id]['to']
            ja[from_addr]['time'] = ti
            ja[to_addr]['time'] = ti
            if vr_status == verification_status.fail:
                j[trx_id]['failures'] = j[trx_id]['failures'] + 1
            elif vr_status == verification_status.success:
                j[trx_id]['successes'] = j[trx_id]['successes'] + 1
            if verifications >= verification_max:
                if j[trx_id]['successes'] > j[trx_id]['failures']:
                    j[trx_id]['status'] = trx_status_code.success
                    ja[from_addr]['trx_h'][trx_id]= j[trx_id]
                    ja[to_addr]['trx_h'][trx_id]= j[trx_id]
                    j.pop(trx_id)
                elif j[trx_id]['successes'] < j[trx_id]['failures']:
                    j[trx_id]['status'] = trx_status_code.fail
                    ja[from_addr]['trx_h'][trx_id]= j[trx_id]
                    ja[to_addr]['trx_h'][trx_id]= j[trx_id]
                elif j[trx_id]['successes'] == j[trx_id]['failures']:
                    j[trx_id]['status'] = trx_status_code.pending
                    if j[trx_id]['failures'] >= verification_max:
                        j[trx_id]['status'] = trx_status_code.fail
                    else:
                        j[trx_id]['verifications'] = 0
                    ja[from_addr]['trx_h'][trx_id]= j[trx_id]
                    ja[to_addr]['trx_h'][trx_id]= j[trx_id]
                    if j[trx_id]['status'] == trx_status_code.fail:
                        j.pop(trx_id)
            else:
                ja[from_addr]['trx_h'][trx_id]= j[trx_id]
                ja[to_addr]['trx_h'][trx_id]= j[trx_id]
            fe = open(pending_transaction_dir,'w')
            fe.write(json.dumps(j))
            fe.close()
            f = open(addresses_dir,'w')
            json.dump(ja,f)
            f.close()
    except:
        pass
    C_Working = False
    return "True", 200
@app.route('/pool_info', methods=['POST','GET'])
def inf():
    output = {}
    try:
        fa = open(addresses_dir,'r')
        fr = json.load(fa)
        output['addresses'] = fr
        fa.close()
        f = open(pool_dir,'r')
        fr = json.load(f)
        output['pool_list'] = fr
        f.close()
        return f'{json.dumps(output)}',200
    except:
        return f'{json.dumps(output)}',400
@app.route('/faucet', methods=['POST','GET'])
def faucet():
    f_amount = 20
    st,j = check_j(addresses_dir)
    while not(st):
        st,j = check_j(addresses_dir)
        pass
    faucet_addr = "py00000000000000000000000000000000000000000000000000000000000000000"
    if request.method == 'GET':
        addr = request.args['addr']
        if addr in j:
            pass
        else:
            j[addr] = {"balance":0,"trx_h":{},'time':int(time.time() * 1000)}
        id = gen_trx_id()
        j[addr]['balance'] = j[addr]['balance'] + f_amount
        trx_o = {'from':faucet_addr,'to':addr,'amount':f_amount,'time':int(time.time() * 1000)}
        j[addr]['trx_h'][id] = trx_o
        fa = open(addresses_dir,'w')
        json.dump(j,fa)
        fa.close()
        pass
    if request.method == 'POST':
        addr = request.form['addr']
        if addr in j:
            pass
        else:
            j[addr] = {"balance":0,"trx_h":{},'time':int(time.time() * 1000)}
        id = gen_trx_id()
        j[addr]['balance'] = j[addr]['balance'] + f_amount
        trx_o = {'from':faucet_addr,'to':addr,'amount':f_amount,'time':int(time.time() * 1000)}
        j[addr]['trx_h'][id] = trx_o
        fa = open(addresses_dir,'w')
        json.dump(j,fa)
        fa.close()
        pass
    output = json.dumps(j[addr])
    return f"{output}",200
@app.route('/createtrx', methods=['POST','GET'])
def createtrx():
    if request.method == 'POST':
        pk = request.form['pk']
        from_addr = request.form['from_addr']
        to_addr = request.form['to_addr']
        amount = request.form['amount']
        pubk = py0_core.GeneratePubK(pk)
        output = {}
        out = {}
        f = open(pool_dir,'r')
        jpl= json.load(f)
        f.close()
        st,j = check_j(addresses_dir)
        while not(st):
            st,j = check_j(addresses_dir)
        ch = []
        if info['id'] in jpl:
            jpl.pop(info['id'])
        global pool_hostname,found
        pool_hostname = ""
        found = True
        forward = random.choice([False,True])
        if len(jpl) > 0 and not('forwarded' in request.form) and forward == True:
            pl = []
            for x in jpl:
                pl.append(x)
            pool = random.choice(pl)
            pool_hostname = jpl[pool]['hostname']
            while not(check_p(pool_hostname)):
                if len(ch) >= len(jpl):
                    found = False
                    break
                else:
                    found = True
                    pass
                if not(pool in ch):
                    ch.append(ch)
                pool = random.choice(pl)
                pool_hostname = jpl[pool]['hostname']
        if found == True and not(pool_hostname == ""):
            address = {}
            address[from_addr] = j[from_addr]
            address[to_addr] = j[to_addr]
            d = dict(amount=amount,to_addr=to_addr,from_addr=from_addr,pk=pk,forwarded=True,address=json.dumps(address))
            send = f"{pool_hostname}/createtrx"
            r = requests.post(send,data=d)
            if r.status_code == 200:
                    out = r.text
        else:
            if 'forwarded' in request.form:
                if "address" in request.form:
                    addresses = json.loads(request.form['address'])
                    if from_addr in j:
                        if addresses[from_addr]['time'] > j[from_addr]['time']:
                            j[from_addr] = addresses[from_addr]
                    else:
                        j[from_addr] = addresses[from_addr]
                    if to_addr in j:
                        if addresses[to_addr]['time'] > j[to_addr]['time']:
                            j[to_addr] = addresses[to_addr]
                    else:
                        j[to_addr] = addresses[to_addr]
            if pubk == from_addr:
                id = gen_trx_id()
                am = float(amount)
                gas = am/verification_max
                out['trx_id'] = id
                output = {'from':from_addr,'to':to_addr,'amount':am,'gas':gas,'total':am+gas,'verifications':0,'status':trx_status_code.pending,'successes':0,'failures':0,'start_time':int(time.time() * 1000),'time':int(time.time() * 1000)}
                sta,jr= check_j(pending_transaction_dir)
                while not(sta):
                    sta,j = check_j(pending_transaction_dir)
                jr[id] = output
                f = open(pending_transaction_dir,'w')
                f.write(json.dumps(jr))
                f.close()
                if from_addr in j:
                    j[from_addr]['trx_h'][id] = output
                else:
                    j[from_addr] = {"balance":0,"trx_h":{},'time':int(time.time() * 1000)}
                    j[from_addr]['trx_h'][id] = output
                if to_addr in j:
                    j[to_addr]['trx_h'][id] = output
                else:
                    j[to_addr] = {"balance":0,"trx_h":{},'time':int(time.time() * 1000)}
                    j[to_addr]['trx_h'][id] = output
                f = open(addresses_dir,"w")
                json.dump(j,f)
                f.close()
                out = json.dumps(out)
            else:
                out = {"F":0}
        return f"{out}", 200
    else:
        return f"Invalid request method {request.method}", 200

@app.route('/addrinfo', methods=['POST','GET'])
def addr_info():
    if request.method == 'GET':
        addr = request.args['addr']
        addr= str(addr)
        output = ""
        code = 200
        if addr[:2] == "tx":
            try:
                f = open(transaction_dir,"r")
                r = f.read()
                f.close()
                j = json.loads(r)
                if addr in j:
                    output = json.dumps(j[addr])
                else:
                    output = "Transaction not Found"
                    code = 400
                    pass
            except:
                code = 400
                pass
        elif addr[:3] == "py0":
            try:
                f = open(addresses_dir,"r")
                r = f.read()
                f.close()
                j = json.loads(r)
                if addr in j:
                    output = json.dumps(j[addr])
                else:
                    j[addr] = {"balance":0,"trx_h":{},'time':int(time.time() * 1000)}
                    sj = json.dumps(j)
                    f = open(addresses_dir,"w")
                    f.write(sj)
                    f.close()
                    output = json.dumps(j[addr])
            except:
                code = 400
                pass
        return f"{output}", code
    else:
        addr = request.form['addr']
        addr= str(addr)
        output = ""
        code = 200
        if addr[:2] == "tx":
            try:
                f = open(transaction_dir,"r")
                r = f.read()
                f.close()
                j = json.loads(r)
                if addr in j:
                    output = json.dumps(j[addr])
                else:
                    output = "Transaction not Found"
                    code = 400
                    pass
            except:
                code = 400
                pass
        elif addr[:3] == "py0":
            try:
                f = open(addresses_dir,"r")
                r = f.read()
                f.close()
                j = json.loads(r)
                if addr in j:
                    output = json.dumps(j[addr])
                else:
                    j[addr] = {"balance":0,"trx_h":{},'time':int(time.time() * 1000)}
                    sj = json.dumps(j)
                    f = open(addresses_dir,"w")
                    f.write(sj)
                    f.close()
                    output = json.dumps(j[addr])
            except:
                code = 400
                pass
        return f"{output}", code
try:
    app.run(host=config['allow_ip'],port=config['port'],debug=False)
except KeyboardInterrupt:
    pass
