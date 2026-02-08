import random, zlib, os, time, hashlib, inspect, sys

class Generator:
    def __init__(self, bytecode, consts):
        self.bc = bytecode
        self.cn = consts
        self.k_next = sum(ord(c) for c in "NEXT_NODE") % 251
        self.k_bump = sum(ord(c) for c in "STATE_BUMP") % 251

    def generate_stub(self):
        entropy = int(time.perf_counter_ns()) & 0xFFFFFFFF
        return f'''
import os,time,zlib,hashlib,random,inspect,sys

def _vmp():
    _hist=[]
    _s=(os.getpid()^{entropy})&0xFFFFFFFF
    _m={self._map(entropy)}
    _kn={self.k_next}
    _kb={self.k_bump}
    _p={self._hid("ENTRY")}
    _c=_s
    _t0=time.perf_counter_ns()

    while _p:
        if _p not in _m:break
        _blk=_m.pop(_p)
        try:
            if sys.gettrace():raise RuntimeError
            if inspect.currentframe().f_back.f_trace:raise RuntimeError
            h=hashlib.sha256(str(_hist).encode()).digest()
            sd=_c^int.from_bytes(h[:4],'big')
            r=list(range(256))
            random.seed(sd);random.shuffle(r)
            inv={{v:k for k,v in enumerate(r)}}
            raw=bytearray()
            for b in zlib.decompress(_blk):
                v=inv[b]
                raw.append(((v<<1)&255)|(v>>7))
            ns={{}}
            buf=b''
            for x in raw:
                buf+=bytes([x])
                if x==59:
                    exec(buf,ns)
                    buf=b''
            _p=ns.get(_kn)
            _c=(_c^ns.get(_kb,0)^((time.perf_counter_ns()-_t0)>>4))&0xFFFFFFFF
            _hist.append(_p)
        except:
            _p={self._hid("POISON")}
    os.environ["VMP_AUTH"]=hex(_c)

if __name__=="__main__":
    _vmp()
'''

    def _hid(self,n):
        return int(hashlib.sha256(n.encode()).hexdigest()[:12],16)

    def _map(self,key):
        blocks={
            "ENTRY":f"ns[{self.k_next}]={self._hid('CORE')};ns[{self.k_bump}]=0x1337;",
            "CORE":f"ns[{self.k_next}]={self._hid('EXIT')};ns[{self.k_bump}]=0xDEAD;",
            "EXIT":f"ns[{self.k_next}]=0;ns[{self.k_bump}]=0;",
            "POISON":"import time;[time.sleep(0.02) for _ in range(50)];"
        }
        m={}
        c=key
        h=[]
        for n in ("ENTRY","CORE","EXIT","POISON"):
            d=hashlib.sha256(str(h).encode()).digest()
            sd=c^int.from_bytes(d[:4],'big')
            r=list(range(256))
            random.seed(sd);random.shuffle(r)
            comp=zlib.compress(f"ns={{}};{blocks[n]}".encode())
            out=bytearray()
            for b in comp:
                v=((b>>1)|(b<<7))&255
                out.append(r[v])
            m[self._hid(n)]=bytes(out)
            h.append(self._hid(n))
            c^=(0x1337 if n=="ENTRY" else 0xDEAD if n=="CORE" else 0)
        return m