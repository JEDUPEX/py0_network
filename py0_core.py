import random
import math
def IntPow(x):
    s = str(x)
    n = len(s)
    return n-1
keys = 'abcdefghijklmnopqrstuvwxyz'
keysv = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7,'i':8,'j':9,'k':10,'l':11,'m':12,'n':13,'o':14,'p':15,'q':16,'r':17,'s':18,'t':19,'u':20,'v':21,'w':22,'x':23,'y':24,'z':25}
def GeneratePrivK(l:int):
    l = 128 if l < 128 else l
    pk = ""
    for i in range(l):
        pk += random.choice(keys)
    return(pk)
def GeneratePubK(pk):
    out = []
    on = 0
    st = "py0"
    l = 64
    pubk = st
    n =0
    for i in pk:
        if n>=l:
                n=0
        if len(out) < l:
            out.append(keysv[i])
        else:
            out[n] = out[n]+keysv[i]
        n+=1
    for x in out:
         if x > len(keys)-1:
            p = IntPow(x)
            u = x/(10**p)
            o = math.ceil(u)
            t = str(o)
            pubk += t
            pass
         else:
             pubk += keys[x]
    return str(pubk)