# -*- coding: utf-8 -*-
"""
OT PLUS API v3 - Backend de validação de keys
Deploy: Render / Railway / Fly.io (grátis)
"""
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3, secrets, hashlib, hmac, base64, json, os

# ============ CONFIG (MUDE ISSO) ============
ADMIN_USER = "admin"
ADMIN_PASS = "otplus2025"                     # ⚠ MUDAR
SECRET    = "otplus-v3-secret-troque-2025"    # ⚠ MUDAR
DB_PATH   = "otplus.db"
# ============================================

app = FastAPI(title="OT PLUS API v3", version="3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS keys (
        key TEXT PRIMARY KEY, created TEXT, expires TEXT,
        lock_type TEXT DEFAULT 'BOTH', bound_ip TEXT, bound_hwid TEXT,
        revoked INTEGER DEFAULT 0, last_seen TEXT, used_count INTEGER DEFAULT 0,
        notes TEXT DEFAULT '', user_label TEXT DEFAULT ''
    )""")
    con.commit(); con.close()
init_db()

def db():
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
    return con

def make_token():
    payload = {"u": ADMIN_USER, "exp": (datetime.now()+timedelta(hours=12)).isoformat()}
    raw = json.dumps(payload).encode()
    sig = hmac.new(SECRET.encode(), raw, hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(raw).decode() + "." + sig

def check_token(tok):
    try:
        b64, sig = tok.split(".")
        raw = base64.urlsafe_b64decode(b64.encode())
        if not hmac.compare_digest(sig, hmac.new(SECRET.encode(), raw, hashlib.sha256).hexdigest()):
            return False
        return datetime.fromisoformat(json.loads(raw)["exp"]) > datetime.now()
    except: return False

def require_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401, "Não autenticado")
    if not check_token(authorization[7:]): raise HTTPException(401, "Token inválido")
    return True

def new_key():
    return "OTP-" + "-".join(secrets.token_hex(2).upper() for _ in range(4))

# ---------- MODELOS ----------
class ValidateReq(BaseModel):
    key: str; hwid: str; ip: str
class LoginReq(BaseModel):
    user: str; password: str
class CreateReq(BaseModel):
    days: int = 30; lock_type: str = "BOTH"; notes: str = ""; user_label: str = ""

# ---------- ROTAS PÚBLICAS ----------
@app.get("/")
def root():
    return {"service": "OT PLUS API v3", "status": "online", "time": datetime.now().isoformat()}

@app.post("/api/validate")
def validate(req: ValidateReq):
    con = db()
    row = con.execute("SELECT * FROM keys WHERE key=?", (req.key.upper().strip(),)).fetchone()
    if not row:
        con.close(); return {"ok": False, "reason": "invalid", "msg": "Key não encontrada"}
    k = dict(row)
    if k["revoked"]:
        con.close(); return {"ok": False, "reason": "revoked", "msg": "Key revogada"}
    exp = datetime.fromisoformat(k["expires"])
    if datetime.now() > exp:
        con.close(); return {"ok": False, "reason": "expired", "msg": f"Expirou em {exp:%d/%m/%Y}"}
    lock = k["lock_type"] or "BOTH"
    upd = {}
    if lock in ("IP", "BOTH"):
        if k["bound_ip"] and k["bound_ip"] != req.ip:
            con.close(); return {"ok": False, "reason": "ip", "msg": f"Key vinculada ao IP {k['bound_ip']}"}
        if not k["bound_ip"]: upd["bound_ip"] = req.ip
    if lock in ("HWID", "BOTH"):
        if k["bound_hwid"] and k["bound_hwid"] != req.hwid:
            con.close(); return {"ok": False, "reason": "hwid", "msg": "Key vinculada a outro PC"}
        if not k["bound_hwid"]: upd["bound_hwid"] = req.hwid
    upd["last_seen"] = datetime.now().isoformat()
    upd["used_count"] = (k["used_count"] or 0) + 1
    sets = ", ".join(f"{x}=?" for x in upd)
    con.execute(f"UPDATE keys SET {sets} WHERE key=?", (*upd.values(), k["key"]))
    con.commit(); con.close()
    return {"ok": True, "expires": k["expires"],
            "days_left": (exp - datetime.now()).days, "lock": lock}

# ---------- ROTAS ADMIN ----------
@app.post("/api/admin/login")
def admin_login(req: LoginReq):
    if req.user != ADMIN_USER or req.password != ADMIN_PASS:
        raise HTTPException(401, "Credenciais inválidas")
    return {"token": make_token()}

@app.get("/api/admin/keys")
def list_keys(_: bool = Depends(require_admin)):
    con = db()
    rows = con.execute("SELECT * FROM keys ORDER BY created DESC").fetchall()
    con.close()
    return [dict(r) for r in rows]

@app.post("/api/admin/keys")
def create_key(req: CreateReq, _: bool = Depends(require_admin)):
    k = new_key()
    con = db()
    con.execute("""INSERT INTO keys (key, created, expires, lock_type, revoked, used_count, notes, user_label)
                   VALUES (?, ?, ?, ?, 0, 0, ?, ?)""",
                (k, datetime.now().isoformat(),
                 (datetime.now()+timedelta(days=req.days)).isoformat(),
                 req.lock_type, req.notes, req.user_label))
    con.commit(); con.close()
    return {"key": k, "days": req.days, "lock": req.lock_type}

@app.delete("/api/admin/keys/{key}")
def del_key(key: str, _: bool = Depends(require_admin)):
    con = db(); con.execute("DELETE FROM keys WHERE key=?", (key.upper(),))
    con.commit(); con.close(); return {"ok": True}

@app.post("/api/admin/keys/{key}/revoke")
def revoke(key: str, _: bool = Depends(require_admin)):
    con = db(); con.execute("UPDATE keys SET revoked=1 WHERE key=?", (key.upper(),))
    con.commit(); con.close(); return {"ok": True}

@app.post("/api/admin/keys/{key}/unrevoke")
def unrevoke(key: str, _: bool = Depends(require_admin)):
    con = db(); con.execute("UPDATE keys SET revoked=0 WHERE key=?", (key.upper(),))
    con.commit(); con.close(); return {"ok": True}

@app.post("/api/admin/keys/{key}/reset")
def reset(key: str, _: bool = Depends(require_admin)):
    con = db()
    con.execute("UPDATE keys SET bound_ip=NULL, bound_hwid=NULL WHERE key=?", (key.upper(),))
    con.commit(); con.close(); return {"ok": True}

@app.post("/api/admin/keys/{key}/extend/{days}")
def extend(key: str, days: int, _: bool = Depends(require_admin)):
    con = db()
    row = con.execute("SELECT expires FROM keys WHERE key=?", (key.upper(),)).fetchone()
    if not row: con.close(); raise HTTPException(404)
    cur = datetime.fromisoformat(row["expires"])
    base = max(cur, datetime.now())
    new = (base + timedelta(days=days)).isoformat()
    con.execute("UPDATE keys SET expires=? WHERE key=?", (new, key.upper()))
    con.commit(); con.close(); return {"ok": True, "new_expires": new}

# ---------- PAINEL ADMIN HTML ----------
ADMIN_HTML = """<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><title>OT PLUS Admin</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:'Consolas',monospace}
body{background:#0a0e13;color:#d6f7ff;padding:24px}
h1{color:#39ff14;font-size:28px;margin-bottom:4px}
.sub{color:#7ee7ff;font-size:12px;margin-bottom:24px}
.card{background:#161c24;border-radius:12px;padding:20px;margin-bottom:18px}
.card h2{color:#39ff14;font-size:14px;margin-bottom:14px;letter-spacing:1px}
input,select,button{padding:10px;border-radius:6px;border:1px solid #2a3542;
  background:#0a0e13;color:#39ff14;font-family:inherit;font-size:13px;outline:none}
input:focus,select:focus{border-color:#39ff14}
button{cursor:pointer;background:#39ff14;color:#001a00;font-weight:bold;
  border:none;padding:11px 20px;transition:.15s}
button:hover{background:#2be00f;transform:translateY(-1px)}
button.danger{background:#ff5d5d;color:#fff}
button.warn{background:#ffd700;color:#000}
button.ghost{background:#161c24;color:#7ee7ff;border:1px solid #2a3542}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
table{width:100%;border-collapse:collapse;margin-top:12px;font-size:12px}
th{background:#0e1319;color:#39ff14;text-align:left;padding:10px;border-bottom:1px solid #2a3542}
td{padding:9px 10px;border-bottom:1px solid #1c242e}
tr:hover{background:#0e1319}
.badge{padding:3px 9px;border-radius:20px;font-size:11px;font-weight:bold}
.ativa{background:#39ff14;color:#000}
.expirada{background:#ffd700;color:#000}
.revogada{background:#ff5d5d;color:#fff}
#login{max-width:380px;margin:80px auto}
#login input{width:100%;margin-bottom:10px}
#login button{width:100%}
.hide{display:none!important}
.keybox{background:#0a0e13;padding:14px;border-radius:8px;
  border:1px dashed #39ff14;font-size:16px;color:#39ff14;text-align:center;
  letter-spacing:1.5px;margin-top:12px}
</style></head><body>

<div id="login">
  <div class="card">
    <h1>👑 OT PLUS Admin</h1>
    <div class="sub">Painel de Controle v3</div>
    <input id="u" placeholder="Usuário" value="admin">
    <input id="p" type="password" placeholder="Senha">
    <button onclick="doLogin()">🔓 Entrar</button>
  </div>
</div>

<div id="panel" class="hide">
  <h1>👑 OT PLUS ADMIN</h1>
  <div class="sub" id="hello"></div>

  <div class="card">
    <h2>➕ GERAR NOVA KEY</h2>
    <div class="row">
      <input id="dias" type="number" value="30" placeholder="Dias" style="width:90px">
      <select id="lock">
        <option value="BOTH">Trava: IP + HWID</option>
        <option value="IP">Trava: só IP</option>
        <option value="HWID">Trava: só HWID</option>
        <option value="NONE">Sem trava</option>
      </select>
      <input id="label" placeholder="Nome do cliente (opcional)" style="flex:1;min-width:180px">
      <button onclick="gerar()">➕ Gerar Key</button>
    </div>
    <div id="keybox" class="keybox hide"></div>
  </div>

  <div class="card">
    <h2>📋 KEYS CADASTRADAS</h2>
    <div class="row" style="margin-bottom:10px">
      <button class="ghost" onclick="load()">🔄 Atualizar</button>
      <span id="stats" style="color:#7ee7ff;font-size:12px"></span>
    </div>
    <table><thead><tr>
      <th>Key</th><th>Cliente</th><th>Expira</th><th>Trava</th>
      <th>IP</th><th>HWID</th><th>Status</th><th>Ações</th>
    </tr></thead><tbody id="tbody"></tbody></table>
  </div>
</div>

<script>
const API = "";  // vazio = mesmo host. Se separar, coloque a URL do backend
let TOKEN = localStorage.getItem("otplus_token") || "";

async function doLogin(){
  const u = document.getElementById("u").value;
  const p = document.getElementById("p").value;
  const r = await fetch(API+"/api/admin/login",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({user:u,password:p})});
  if(!r.ok){alert("Login falhou");return;}
  const j = await r.json();
  TOKEN = j.token; localStorage.setItem("otplus_token",TOKEN);
  showPanel();
}

function showPanel(){
  document.getElementById("login").classList.add("hide");
  document.getElementById("panel").classList.remove("hide");
  document.getElementById("hello").textContent = "Logado como administrador";
  load();
}

async function api(path,opts={}){
  opts.headers = opts.headers||{};
  opts.headers["Authorization"] = "Bearer "+TOKEN;
  if(opts.body && !opts.headers["Content-Type"]) opts.headers["Content-Type"]="application/json";
  const r = await fetch(API+path,opts);
  if(r.status===401){localStorage.removeItem("otplus_token");location.reload();return null;}
  return r.json();
}

async function load(){
  const keys = await api("/api/admin/keys");
  if(!keys) return;
  const tb = document.getElementById("tbody"); tb.innerHTML="";
  let at=0,ex=0,rv=0;
  keys.forEach(k=>{
    const exp = new Date(k.expires);
    const now = new Date();
    let st = k.revoked?"revogada":(now>exp?"expirada":"ativa");
    if(st==="ativa")at++; else if(st==="expirada")ex++; else rv++;
    tb.innerHTML += `<tr>
      <td><b style="color:#39ff14">${k.key}</b></td>
      <td>${k.user_label||'-'}</td>
      <td>${exp.toLocaleDateString('pt-BR')}</td>
      <td>${k.lock_type}</td>
      <td>${k.bound_ip||'-'}</td>
      <td>${(k.bound_hwid||'-').substring(0,14)}</td>
      <td><span class="badge ${st}">${st}</span></td>
      <td>
        <button class="ghost" onclick="copiar('${k.key}')">📋</button>
        <button class="ghost" onclick="resetar('${k.key}')">🔓</button>
        <button class="warn" onclick="estender('${k.key}')">+30d</button>
        <button class="danger" onclick="revogar('${k.key}')">🚫</button>
        <button class="danger" onclick="excluir('${k.key}')">🗑️</button>
      </td>
    </tr>`;
  });
  document.getElementById("stats").textContent =
    `✅ ${at} ativas  |  ⏰ ${ex} expiradas  |  🚫 ${rv} revogadas`;
}

async function gerar(){
  const days = parseInt(document.getElementById("dias").value)||30;
  const lock = document.getElementById("lock").value;
  const label = document.getElementById("label").value;
  const r = await api("/api/admin/keys",{method:"POST",
    body:JSON.stringify({days,lock_type:lock,user_label:label})});
  if(!r) return;
  const box = document.getElementById("keybox");
  box.classList.remove("hide");
  box.innerHTML = `✅ Key gerada — clique para copiar:<br><br>
    <b style="font-size:20px;cursor:pointer" onclick="copiar('${r.key}')">${r.key}</b>`;
  load();
}

function copiar(k){ navigator.clipboard.writeText(k); alert("Copiada: "+k); }
async function resetar(k){ if(!confirm("Resetar vínculo de "+k+"?"))return;
  await api("/api/admin/keys/"+k+"/reset",{method:"POST"}); load(); }
async function revogar(k){ if(!confirm("Revogar "+k+"?"))return;
  await api("/api/admin/keys/"+k+"/revoke",{method:"POST"}); load(); }
async function estender(k){ await api("/api/admin/keys/"+k+"/extend/30",{method:"POST"}); load(); }
async function excluir(k){ if(!confirm("EXCLUIR "+k+" PERMANENTEMENTE?"))return;
  await api("/api/admin/keys/"+k,{method:"DELETE"}); load(); }

if(TOKEN) showPanel();
</script></body></html>"""

@app.get("/admin", response_class=HTMLResponse)
def admin_page(): return ADMIN_HTML