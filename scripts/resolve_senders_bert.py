"""
Entity resolution mittente/destinatario reale dei messaggi (Task 3), pipeline stile tesi:
  1) regole sintattiche ad alta confidenza (regex "Dest, Mitt here / it's Mitt / X to Y")
  2) classificatore BERT (question-answering estrattivo) per i casi residui
Scrive c['text_from'] / c['text_to'] (id entità o null) in JSON e rigenera src/data.js.
NON ri-esegue BERTopic (preserva topics/mentions/commGroups già presenti).
Uso: python scripts/resolve_senders_bert.py
"""
import json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, 'data', 'processed', 'vast_mc3_optimized.json')
DATA_JS = os.path.join(ROOT, 'src', 'data.js')

d = json.load(open(JSON_PATH, encoding='utf-8'))
nodes = {n['id']: n for n in d['nodes']}
ent_names = {n['name']: n['id'] for n in d['nodes'] if n['type'] == 'Entity'}

# --- name matcher: nome completo + token DISCRIMINANTI (a confine di parola) ---
# Il vecchio matcher usava il primo token del nome, che è spesso condiviso: "Sailor" sta sia
# nella Person "Sailor Shift" sia nell'Organization "Sailor Shifts Team", e vinceva quello
# sbagliato ("Remora here to Sailor Shifts" → la cantante invece del team). Ora ogni token
# ambiguo (presente in più entità) viene SCARTATO, e restano solo quelli che identificano
# univocamente un'entità: "shifts"→Team, "shift"→Sailor Shift, "miesel"→V. Miesel Shipping
# (che così riconosce anche l'abbreviazione "V. Miesel HQ"), "conti"→Nadia Conti.
ent_list = [n['name'] for n in d['nodes'] if n['type'] == 'Entity']
tok_owner = {}
for nm in ent_list:
    for t in re.findall(r"[\w'’]+", nm.lower()):
        if len(t) > 3:
            tok_owner.setdefault(t, set()).add(nm)

aliases = [(nm.lower(), nm) for nm in ent_list]
aliases += [(t, list(owners)[0]) for t, owners in tok_owner.items() if len(owners) == 1]
aliases.sort(key=lambda x: -len(x[0]))   # sempre il match più lungo (più specifico) per primo

def find_name(frag):
    f = (frag or '').lower()
    for k, nm in aliases:
        if re.search(r'\b' + re.escape(k) + r'\b', f):
            return nm
    return None

NAME = r"[\w.'’ ]{2,32}?"

# Le formule d'apertura del protocollo radio che fissano ENTRAMBI i ruoli senza ambiguità.
# Si applicano SOLO al preambolo (la prima frase): cercarle in tutto il messaggio produce
# falsi positivi (es. «...it's a protected area» faceva estrarre la Location "Protected areas"
# come mittente). Ordinate dalla più specifica alla più generica.
CANON = [
    # "Destinatario, Mittente here|reporting|responding"
    #   → «Davis, Nadia here.» · «Green Guardians, Sentinel reporting.»
    # Il verbo cambia ma la struttura è la stessa: erano proprio i "reporting" a restare
    # irrisolti (13 messaggi con auto-anello radio tipo "Green Guardians → Green Guardians").
    (re.compile(rf"^\s*(?P<r>{NAME})\s*[,:]\s*(?P<s>{NAME})\s+(?:here|reporting|responding)\b", re.I), 's', 'r'),
    # "Destinatario, this is Mittente"   → «Ms. Conti, this is Oceanus City Council.»
    (re.compile(rf"^\s*(?P<r>{NAME})\s*[,:]\s*(?:this is|it'?s)\s+(?P<s>{NAME})\s*[.!,]", re.I), 's', 'r'),
    # "Mittente here to Destinatario"    → «Davis here to V. Miesel Shipping.»
    (re.compile(rf"^\s*(?P<s>{NAME})\s+here\s+to\s+(?P<r>{NAME})\s*[.!,:]", re.I), 's', 'r'),
    # "Mittente to Destinatario"         → «V. Miesel HQ to Nadia.»
    (re.compile(rf"^\s*(?:this is\s+)?(?P<s>{NAME})\s+to\s+(?P<r>{NAME})\s*[.!,:]", re.I), 's', 'r'),
]
# Formule che rivelano solo il MITTENTE: il destinatario resta ai metadati radio.
SENDER_ONLY = [
    re.compile(rf"^\s*(?P<s>{NAME})\s+here\b", re.I),                    # «The Lookout here!»
    re.compile(rf"(?:this is|it'?s)\s+(?P<s>{NAME})\s*[.!,]", re.I),     # «This is Nadia.»
]

def rules(txt):
    # NIENTE splitting in frasi: spezzare sul primo "." troncava i preamboli con abbreviazioni
    # («Davis here to V. Miesel Shipping» diventava «Davis here to V.»). Non serve: le formule
    # canoniche sono ancorate all'inizio del messaggio, quindi non possono pescare a metà testo.
    head = (txt or '').strip()

    for rx, gs, gr in CANON:
        m = rx.match(head)
        if not m: continue
        s = find_name(m.group(gs)); r = find_name(m.group(gr))
        if s and r and s != r:
            return s, r, True          # ruoli fissati dal preambolo: è la fonte più affidabile

    # Qui invece cerchiamo (non ancorato), quindi restiamo sull'apertura per non raccogliere
    # falsi positivi dal corpo del messaggio (era così che «it's a protected area» diventava
    # un mittente).
    for rx in SENDER_ONLY:
        m = rx.search(head[:90])
        if m:
            s = find_name(m.group('s'))
            if s: return s, None, False
    return None, None, False

comms = [n for n in d['nodes'] if n.get('sub_type') == 'Communication']

# --- BERT QA per i residui (modello caricato direttamente: il pipeline QA non c'è in transformers 5.x) ---
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
import torch.nn.functional as F
print("Carico BERT QA (distilbert-base-cased-distilled-squad)...")
_tok = AutoTokenizer.from_pretrained("distilbert-base-cased-distilled-squad")
_model = AutoModelForQuestionAnswering.from_pretrained("distilbert-base-cased-distilled-squad").eval()

def qa_name(question, context, thr=0.15):
    ctx = (context or '').strip()
    if not ctx: return None
    inp = _tok(question, ctx[:400], return_tensors="pt", truncation=True, max_length=384)
    with torch.no_grad():
        out = _model(**inp)
    sp = F.softmax(out.start_logits, -1)[0]
    ep = F.softmax(out.end_logits, -1)[0]
    si = int(sp.argmax()); ei = int(ep.argmax())
    if ei < si: ei = si
    score = float(sp[si] * ep[ei])
    if score < thr: return None
    ans = _tok.decode(inp['input_ids'][0][si:ei + 1], skip_special_tokens=True)
    return find_name(ans)

n_rule_s = n_rule_r = n_bert_s = n_bert_r = 0
for i, c in enumerate(comms):
    txt = (c.get('content') or '').strip()
    ts, tr, is_canon = rules(txt[:160])
    # Provenienza dell'attribuzione, su tre livelli di affidabilità:
    #   'canon' = preambolo canonico "Destinatario, Mittente here" → identifica entrambi i ruoli
    #             senza ambiguità: qui il testo BATTE i metadati radio, che spesso sono invertiti
    #   'rule'  = altre regex ("X here to Y", "this is X") → utili ma ambigue sui nomi simili
    #   'bert'  = fallback QA → rumoroso, da non usare per l'attribuzione
    src_s = ('canon' if is_canon else 'rule') if ts else None
    src_r = ('canon' if is_canon else 'rule') if tr else None
    if ts: n_rule_s += 1
    if tr: n_rule_r += 1
    if not ts:
        ts = qa_name("Who is speaking or sending this message?", txt)
        if ts: n_bert_s += 1; src_s = 'bert'
    if not tr:
        tr = qa_name("Who is this message addressed to?", txt)
        if tr: n_bert_r += 1; src_r = 'bert'
    c['text_from'] = ent_names.get(ts) if ts else None
    c['text_to'] = ent_names.get(tr) if tr else None
    c['text_from_src'] = src_s if c['text_from'] else None
    c['text_to_src'] = src_r if c['text_to'] else None
    if (i + 1) % 100 == 0:
        print(f"  {i+1}/{len(comms)}")

print(f"Mittente: regole {n_rule_s} + BERT {n_bert_s} | Destinatario: regole {n_rule_r} + BERT {n_bert_r}")

json.dump(d, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
with open(DATA_JS, 'w', encoding='utf-8') as f:
    f.write('// Auto-generato — NON modificare a mano.\n')
    f.write(f"// {len(d['nodes'])} nodi. Topic BERTopic + mentions + commGroups + text_from/text_to (rules+BERT QA).\n")
    f.write('window.VAST_DATA = ')
    json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')
print('OK. data.js:', round(os.path.getsize(DATA_JS) / 1024), 'KB')
print('con text_from:', sum(1 for c in comms if c.get('text_from')),
      '| con text_to:', sum(1 for c in comms if c.get('text_to')))
