"""
Ricalcola SOLO `mentions` (about) e `commGroups` (Louvain res=1.3) usando l'attribuzione
RETTIFICATA (regola d'oro: se text_from_src e text_to_src sono entrambi 'canon' il testo
batte i metadati radio, altrimenti vale la radio) — la stessa applicata in DataModel.init().
I topic BERTopic NON dipendono dall'attribuzione e restano invariati.
Uso: python scripts/regen_groups.py   (richiede: networkx)
"""
import json, re, os, collections
import networkx as nx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, 'data', 'processed', 'vast_mc3_optimized.json')
DATA_JS = os.path.join(ROOT, 'src', 'data.js')

d = json.load(open(JSON_PATH, encoding='utf-8'))
nodes = {n['id']: n for n in d['nodes']}
ents = {nid: n for nid, n in nodes.items() if n['type'] == 'Entity'}
ent_names = {n['name']: nid for nid, n in ents.items()}

sent, recv = {}, {}
for l in d['links']:
    if l['type'] == 'sent': sent[l['target']] = l['source']
    if l['type'] == 'received': recv[l['source']] = l['target']
comms = [n for n in d['nodes'] if n.get('sub_type') == 'Communication']

# ---------------- Attribuzione rettificata (nomi) ----------------
corrected = 0
attr = {}   # comm id -> (nome mittente, nome destinatario)
for c in comms:
    rf = nodes[sent[c['id']]]['name'] if c['id'] in sent else None
    rt = nodes[recv[c['id']]]['name'] if c['id'] in recv else None
    tf, tt = c.get('text_from'), c.get('text_to')
    canon = c.get('text_from_src') == 'canon' and c.get('text_to_src') == 'canon' and tf != tt
    f, t = (tf, tt) if canon else (rf, rt)
    if canon and (tf != rf or tt != rt): corrected += 1
    attr[c['id']] = (f, t)
print(f"Attribuzione: {corrected} messaggi rettificati dal testo su {len(comms)}")

# ---------------- Dimensione "about" (entità menzionate) ----------------
name_list = sorted(ent_names.keys(), key=len, reverse=True)
mention_counter = collections.Counter()
for c in comms:
    txt = c.get('content') or ''
    f, t = attr[c['id']]
    ment = []
    for name in name_list:
        if name in (f, t): continue
        if re.search(r'\b' + re.escape(name) + r'\b', txt):
            ment.append(ent_names[name])
    c['mentions'] = ment
    for m in ment: mention_counter[m] += 1
print("Entità più citate:", [(nodes[k]['name'], v) for k, v in mention_counter.most_common(5)])

# ---------------- commGroups (Louvain res=1.3) + topic per gruppo ----------------
pairs = collections.Counter()
for c in comms:
    f, t = attr[c['id']]
    a, b = ent_names.get(f), ent_names.get(t)
    if a and b and a != b: pairs[tuple(sorted((a, b)))] += 1
G = nx.Graph()
for (a, b), w in pairs.items(): G.add_edge(a, b, weight=w)
cl = sorted(nx.algorithms.community.louvain_communities(G, weight='weight', seed=42, resolution=1.3),
            key=len, reverse=True)
node2grp = {m: gi for gi, members in enumerate(cl) for m in members}

def label_for(members):
    names = set(ents[m]['name'] for m in members)
    if 'Boss' in names or 'Mrs. Money' in names: return 'Rete Pseudonimi'
    if 'Green Guardians' in names or 'Reef Guardian' in names: return 'Ambiente & Conservazione'
    if 'Clepper Jensen' in names or 'Miranda Jordan' in names: return 'Giornalisti'
    # dopo la rettifica dell'attribuzione la vecchia macro-fazione "Sailor Shift & Logistica"
    # si scinde: chi opera in mare (navi/porti) e chi gestisce permessi (Council, Nadia).
    if 'Nadia Conti' in names or 'Oceanus City Council' in names: return 'Istituzioni & Permessi'
    if 'Mako' in names or 'V. Miesel Shipping' in names: return 'Navi & Operazioni in Mare'
    return ents[max(members, key=lambda x: ents[x].get('degree', 0))]['name']

tlabel = {t['id']: t['label'] for t in d['topics']}
commGroups = []
for gi, members in enumerate(cl):
    ms = sorted(members, key=lambda x: ents[x].get('degree', 0), reverse=True)
    tc = collections.Counter()
    for c in comms:
        f = ent_names.get(attr[c['id']][0])
        if f is not None and node2grp.get(f) == gi and c.get('topic', -1) >= 0:
            tc[tlabel[c['topic']]] += 1
    commGroups.append({'id': gi, 'label': label_for(members), 'size': len(ms),
                       'members': [ents[m]['name'] for m in ms],
                       'topics': [{'label': k, 'count': v} for k, v in tc.most_common(4)]})
for nid, n in nodes.items():
    if n['type'] == 'Entity': n['comm_group'] = node2grp.get(nid, -1)
d['commGroups'] = commGroups

# ---------------- Scrittura ----------------
json.dump(d, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
with open(DATA_JS, 'w', encoding='utf-8') as f:
    f.write('// Auto-generato da data/processed/vast_mc3_optimized.json — NON modificare a mano.\n')
    f.write(f"// {len(d['nodes'])} nodi, {len(d['links'])} link. Topic BERTopic ({len(d['topics'])}). "
            f"Menzioni 'about'. Louvain comm res=1.3 su attribuzione RETTIFICATA.\n")
    f.write('window.VAST_DATA = ')
    json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')
print('OK. data.js:', round(os.path.getsize(DATA_JS) / 1024), 'KB')
for g in commGroups:
    print(f"  G{g['id']} {g['label']} ({g['size']}): " + ", ".join(f"{t['label']}({t['count']})" for t in g['topics'][:2]))
    print(f"     {', '.join(g['members'][:8])}")
