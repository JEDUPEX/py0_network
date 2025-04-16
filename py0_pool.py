import requests
import json
from flask import Flask, request
import py0_core
import random
import time
import shutil
import os
import logging
from operator import itemgetter, le
app = Flask(__name__)
"""log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)"""
verification_max = 10
class verification_codes():
    def __init__(self):
        self.fail = 1
        self.success = 2
verification_status = verification_codes()
pending_transaction_dir = "./files/pending/"
addresses_dir = "./files/addresses/"
pool_dir = "./files/pool_list/"
node_dir = "./files/node_list/"
verified_dir = "./files/verified/"
transaction_dir = "./files/transactions/"
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
def gen_trx_id(t):
    keys = '0123456789'
    l = 32-len(str(t))
    output = f"tx{str(t)}"
    for x in range(l):
        output+=random.choice(keys)
    return output
@app.route('/', methods=['POST','GET'])
def home():
    output = {'id':info['id']}
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
                pr[id] = {'hostname':h,'cur_time':int(time.time() * 1000)}
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
                pr[id] = {'hostname':h,'cur_time':int(time.time() * 1000)}
                f=open(pool_dir,'w')
                json.dump(pr,f)
                f.close()
    output['id'] = info['id']
    return f"{json.dumps(output)}" , 200
@app.route('/get_pending', methods=['POST','GET'])
def get_pending():
    pass
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
        if trx_id in [0]:
            pass
    except:
        pass
    C_Working = False
    return "True", 200
@app.route('/pool_info', methods=['POST','GET'])
def inf():
    ti = 0
    if request.method == 'POST':
        pass
    output = {}
    try:
        f = open(f"{transaction_dir}")
    except:
        pass
    trls = os.listdir
@app.route('/faucet', methods=['POST','GET'])
def faucet():
    addr = ""
    if request.method == 'GET':
        addr = request.args['addr']
    if request.method == 'POST':
        addr = request.form['addr']
    f_amount = 20
    faucet_addr = "py00000000000000000000000000000000000000000000000000000000000000000"
    j = {}
    code = 200
    output = {}
    ti =  int(time.time()*1000)
    trx_id = gen_trx_id(ti)
    trx = {'from':faucet_addr,'to':addr,'amount':f_amount,'start_time':ti,'cur_time':ti,'status':trx_status_code.success}
    output["trx_id"] = trx_id
    try:
        if os.path.exists(f"{addresses_dir}{addr}/"):
            j = {}
            f = open(f"{addresses_dir}{addr}/info.json","r")
            d = json.load(f)
            f.close()
            j['balance'] = d['balance'] + f_amount
            j['cur_time'] = ti
            f = open(f"{addresses_dir}{addr}/info.json","w")
            json.dump(j,f)
            f.close()
            f = open(f"{addresses_dir}{addr}/trx_h/{trx_id}.json",'w')
            json.dump(trx,f)
            f.close()
        else:
            try:
                os.mkdir(f"{addresses_dir}{addr}/")
                os.mkdir(f"{addresses_dir}{addr}/trx_h/")
                f = open(f"{addresses_dir}{addr}/info.json","w")
                wr = {"balance":f_amount,'cur_time':ti}
                json.dump(wr,f)
                f.close()
                f = open(f"{addresses_dir}{addr}/trx_h/{trx_id}.json",'w')
                json.dump(trx,f)
                f.close()
            except:
                output = "something went wrong try again later"
                code = 404
                pass
        f = open(f"{transaction_dir}{trx_id}.json","w")
        json.dump(trx,f)
        f.close()
    except:
        output = "something went wrong try again later"
        code = 404
        pass          
    return f"{output}",code
@app.route('/createtrx', methods=['POST','GET'])
def createtrx():
    code = 200
    if request.method == 'POST':
        pk = request.form['pk']
        from_addr = request.form['from_addr']
        to_addr = request.form['to_addr']
        amount = request.form['amount']
        pubk = py0_core.GeneratePubK(pk)
        output = {}
        out = {}
        ti = int(time.time() * 1000)
        trx_id = gen_trx_id(ti)
        am = float(amount)
        gas = am/verification_max
        out['trx_id'] = trx_id
        output = {'from':from_addr,'to':to_addr,'amount':am,'gas':gas,'total':am+gas,'start_time':ti,'cur_time':ti,'verifications':0,'status':trx_status_code.pending,'successes':0,'failures':0}
        out = json.dumps(out)
        if 'forwarded' in request.form:
            if "address" in request.form:
                addresses = json.loads(request.form['address'])
        if pubk == from_addr:
            try:
                if os.path.exists(f"{addresses_dir}{from_addr}/"):
                    f = open(f"{addresses_dir}{from_addr}/trx_h/{trx_id}.json",'w')
                    json.dump(output,f)
                    f.close()
                else:
                    os.mkdir(f"{addresses_dir}{from_addr}/")
                    os.mkdir(f"{addresses_dir}{from_addr}/trx_h/")
                    f = open(f"{addresses_dir}{from_addr}/info.json","w")
                    wr = {"balance":0,'cur_time':ti}
                    f.write(json.dumps(wr))
                    f.close()
                    f = open(f"{addresses_dir}{from_addr}/trx_h/{trx_id}.json",'w')
                    json.dump(output,f)
                    f.close()
                if os.path.exists(f"{addresses_dir}{to_addr}/"):
                    f = open(f"{addresses_dir}{to_addr}/trx_h/{trx_id}.json",'w')
                    json.dump(output,f)
                    f.close()
                else:
                    os.mkdir(f"{addresses_dir}{to_addr}/")
                    os.mkdir(f"{addresses_dir}{to_addr}/trx_h/")
                    f = open(f"{addresses_dir}{to_addr}/info.json","w")
                    wr = {"balance":0,'cur_time':ti}
                    f.write(json.dumps(wr))
                    f.close()
                    f = open(f"{addresses_dir}{to_addr}/trx_h/{trx_id}.json",'w')
                    json.dump(output,f)
                    f.close()
                f = open(f"{transaction_dir}{trx_id}.json","w")
                json.dump(output,f)
                f.close()
                f = open(f"{pending_transaction_dir}{trx_id}.json","w")
                json.dump(output,f)
                f.close()
            except:
                code = 500
                out = "Transaction failed try again later"
                pass
        else:
            out,code = "Transaction not created",500
        return f"{out}", code
    else:
        return f"Invalid request method {request.method}", 500

@app.route('/addrinfo', methods=['POST','GET'])
def addr_info():
    addr = ""
    trx_state = 0
    trx_num = 0
    if request.method == 'GET':
        addr = request.args['addr']
        addr= str(addr)
        if 'trx_h' in request.args:
            if request.args['trx_h'] == "*":
                trx_state = 1
            else:
                try:
                    trx_num = int(request.args['trx_h'])
                    trx_state = 2
                except:
                    pass
    else:
        addr = request.form['addr']
        addr= str(addr)
        if 'trx_h' in request.form:
            if request.form['trx_h'] == "*":
                trx_state = 1
            else:
                try:
                    trx_num = int(request.form['trx_h'])
                    trx_state = 2
                except:
                    pass

    output = ""
    code = 200
    if addr[:2] == "tx":
        try:
            if os.path.exists(f"{transaction_dir}{addr}.json"):
                f = open(f"{transaction_dir}{addr}.json","r")
                output = f.read()
                f.close()
            else:
                output = "Transaction not found"
                code= 404
        except:
            output = "Transaction not found"
            code= 404
            pass
    elif addr[:3] == "py0":
        try:
            if os.path.exists(f"{addresses_dir}{addr}/"):
                j = {}
                f = open(f"{addresses_dir}{addr}/info.json","r")
                d = json.load(f)
                f.close()
                j['balance'] = d['balance']
                j['cur_time'] = d['cur_time']
                j['trx_h'] = {}
                if trx_state in (1,2):
                    trx_ls = os.listdir(f"{addresses_dir}{addr}/trx_h/")
                    trx_sorted = sorted(trx_ls,reverse=True)
                    n = 1
                    for t in trx_sorted:
                        ti = t.replace('.json','')
                        if n > trx_num and trx_state == 2:
                            break
                        with open(f"{addresses_dir}{addr}/trx_h/{t}",'r') as f:
                            j['trx_h'][ti] = json.load(f)
                        n += 1
                output = json.dumps(j) 
            else:
                try:
                    os.mkdir(f"{addresses_dir}{addr}/")
                    os.mkdir(f"{addresses_dir}{addr}/trx_h/")
                    f = open(f"{addresses_dir}{addr}/info.json","w")
                    wr = {"balance":0,'cur_time':int(time.time() * 1000)}
                    f.write(json.dumps(wr))
                    f.close()
                    j = {"balance":0,'cur_time':int(time.time() * 1000),"trx_h":{}}
                    output = json.dumps(j)
                except:
                    output = "something went wrong try again later"
                    code = 500
                    pass
        except:
            output = "something went wrong try again later"
            code = 500
            pass             
        pass
    return f"{output}", code
try:
    app.run(host=config['allow_ip'],port=config['port'])
except KeyboardInterrupt:
    pass
