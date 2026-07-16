"""
Rigenera data/processed/vast_mc3_optimized.json e src/data.js con:
- Topic modeling BERTopic (config ispirata alla tesi Verhagen)
- Dimensione "about": entità menzionate nel testo di ogni messaggio
- commGroups (Louvain res=1.3 sulla rete di comunicazione) con topic per gruppo ricalcolati
Uso: python scripts/regen_bertopic.py

NB: qui mentions/commGroups usano l'attribuzione RADIO grezza (text_from non esiste ancora).
Pipeline corretta: regen_bertopic.py -> resolve_senders_bert.py -> regen_groups.py,
che li RICALCOLA sull'attribuzione rettificata. Non fermarsi a questo script.
"""
import json, re, os, collections, sys

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
raw_texts = [(n.get('content') or '') for n in comms]

# ---------------- Preprocessing (rimuove nomi mitt/dest + numeri) ----------------
entity_tokens = set()
for n in d['nodes']:
    if n['type'] == 'Entity':
        for tok in re.findall(r'[a-z]+', (n.get('name') or '').lower()):
            if len(tok) > 2: entity_tokens.add(tok)

# rimuovi TUTTI i nomi di entità (persone, navi, LUOGHI, org, gruppi) così i topic
# riflettono il TEMA (permessi, pagamenti, movimenti...) e non il luogo (Nemo Reef domina tutto)
all_names = sorted(ent_names.keys(), key=len, reverse=True)
name_re = re.compile(r'\b(' + '|'.join(re.escape(n) for n in all_names) + r')\b', re.I)
# rimuovi anche parole-luogo generiche molto frequenti
generic = re.compile(r'\b(reef|harbor|harbour|bay|cove|quadrant|zone|zones|dock|point|coastline|island|islands|area|areas|boundary|shoals|waters|route)\b', re.I)

def preprocess(c):
    txt = name_re.sub(' ', (c.get('content') or ''))
    txt = generic.sub(' ', txt)
    txt = re.sub(r'\d+', ' ', txt)              # rimuovi numeri
    txt = re.sub(r'\s+', ' ', txt).strip()
    return txt

docs = [preprocess(c) for c in comms]

# ---------------- BERTopic ----------------
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance
from sklearn.feature_extraction.text import CountVectorizer
from hdbscan import HDBSCAN
from umap import UMAP
from sentence_transformers import SentenceTransformer

print("Carico embedding model all-MiniLM-L6-v2 ...")
emb = SentenceTransformer("all-MiniLM-L6-v2")
vectorizer = CountVectorizer(ngram_range=(2, 3), stop_words="english", max_features=200)
umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)  # riproducibile
hdb = HDBSCAN(min_cluster_size=5, min_samples=3, metric='euclidean', prediction_data=True)
rep = [KeyBERTInspired(), MaximalMarginalRelevance(diversity=0.5)]
topic_model = BERTopic(embedding_model=emb, vectorizer_model=vectorizer, umap_model=umap_model,
                       hdbscan_model=hdb, representation_model=rep,
                       calculate_probabilities=False, verbose=True)
assign, _ = topic_model.fit_transform(docs)
# riduci a un numero interpretabile di topic e riassegna gli outlier (-1)
try:
    topic_model.reduce_topics(docs, nr_topics=10)
except Exception as e:
    print("reduce_topics skip:", e)
assign = topic_model.topics_
try:
    assign = topic_model.reduce_outliers(docs, assign, strategy="c-tf-idf")
    topic_model.update_topics(docs, topics=assign, vectorizer_model=vectorizer, representation_model=rep)
except Exception as e:
    print("reduce_outliers skip:", e)
info = topic_model.get_topic_info()
print(info[['Topic', 'Count', 'Name']].to_string())

# Etichette CURATE per id (riproducibile grazie a UMAP random_state=42).
CURATED = {
    0: 'Permessi & Clearance',
    1: 'Operazioni Notturne & Personale',
    2: 'Estrazione Sospetta & Sorveglianza',
    3: 'Conservazione & Fauna',
    4: 'Valutazioni Ambientali',
    5: 'Produzione Videoclip',
    6: 'Logistica & Traffico Navale',
    7: 'Operazioni in Aree Protette',
    8: 'Accessi Illeciti & Contingenza',
}

topic_ids = sorted(t for t in set(assign) if t >= 0)
remap = {t: i for i, t in enumerate(topic_ids)}   # id BERTopic -> 0..K-1
topics_meta = []
for t in topic_ids:
    words = [w for w, _ in topic_model.get_topic(t)][:6]
    fid = remap[t]
    cnt = sum(1 for a in assign if a == t)
    label = CURATED.get(fid) or ' / '.join(words[:2]).title()
    topics_meta.append({'id': fid, 'label': label, 'keywords': words, 'count': cnt})
for c, a in zip(comms, assign):
    c['topic'] = remap.get(a, -1)
d['topics'] = topics_meta
print(f"\nBERTopic -> {len(topics_meta)} topic (+ {sum(1 for c in comms if c['topic']<0)} outlier)")
for tm in topics_meta:
    print(f"  [{tm['id']}] {tm['label']} ({tm['count']}) :: {', '.join(tm['keywords'][:5])}")

# ---------------- Dimensione "about" (entità menzionate) ----------------
name_list = sorted(ent_names.keys(), key=len, reverse=True)
mention_counter = collections.Counter()
for c in comms:
    txt = (c.get('content') or '')
    s = sent.get(c['id']); r = recv.get(c['id'])
    sn = nodes[s]['name'] if s else None
    rn = nodes[r]['name'] if r else None
    ment = []
    for name in name_list:
        if name in (sn, rn): continue
        if re.search(r'\b' + re.escape(name) + r'\b', txt):
            ment.append(ent_names[name])
    c['mentions'] = ment
    for m in ment: mention_counter[m] += 1
print(f"Menzioni estratte. Entità più citate: {[(nodes[k]['name'], v) for k, v in mention_counter.most_common(5)]}")

# ---------------- commGroups (Louvain res=1.3) + topic per gruppo ----------------
import networkx as nx
pairs = collections.Counter()
for c in comms:
    s = sent.get(c['id']); r = recv.get(c['id'])
    if s and r and s != r: pairs[tuple(sorted((s, r)))] += 1
G = nx.Graph()
for (a, b), w in pairs.items(): G.add_edge(a, b, weight=w)
cl = sorted(nx.algorithms.community.louvain_communities(G, weight='weight', seed=42, resolution=1.3), key=len, reverse=True)
node2grp = {m: gi for gi, members in enumerate(cl) for m in members}

def label_for(members):
    names = set(ents[m]['name'] for m in members)
    if 'Green Guardians' in names or 'Reef Guardian' in names: return 'Ambiente & Conservazione'
    if 'Boss' in names or 'Mrs. Money' in names: return 'Rete Pseudonimi'
    if 'Sailor Shifts Team' in names or 'V. Miesel Shipping' in names or 'Mako' in names: return 'Sailor Shift & Logistica'
    if 'Serenity' in names or 'Marlin' in names: return 'Pesca & Diporto'
    if 'Clepper Jensen' in names or 'Miranda Jordan' in names: return 'Giornalisti'
    return ents[max(members, key=lambda x: ents[x].get('degree', 0))]['name']

tlabel = {t['id']: t['label'] for t in topics_meta}
commGroups = []
for gi, members in enumerate(cl):
    ms = sorted(members, key=lambda x: ents[x].get('degree', 0), reverse=True)
    tc = collections.Counter()
    for c in comms:
        s = sent.get(c['id'])
        if s in node2grp and node2grp[s] == gi and c.get('topic', -1) >= 0:
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
    f.write(f"// {len(d['nodes'])} nodi, {len(d['links'])} link. Topic BERTopic ({len(topics_meta)}). Menzioni 'about'. Louvain comm res=1.3.\n")
    f.write('window.VAST_DATA = ')
    json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')
print('OK. data.js:', round(os.path.getsize(DATA_JS) / 1024), 'KB')
for g in commGroups:
    print(f"  G{g['id']} {g['label']} ({g['size']}): " + ", ".join(f"{t['label']}({t['count']})" for t in g['topics'][:2]))
