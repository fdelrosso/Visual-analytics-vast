# CLAUDE.md — VAST 2025 MC3 Dashboard

## Cos'è
Esame di **Visual Analytics** (prof. Rinzivillo, UniPi) di Filippo Del Rosso. Risoluzione grafica della **VAST 2025 Mini-Challenge 3 (MC3)**: knowledge graph di comunicazioni radio intercettate sull'isola di Oceanus, per dimostrare una rete logistica illecita sotto copertura turistica.

**Persona utente:** Clepper Jensen, giornalista investigativo, NON esperto di grafi.
**I 4 task MC3:** (1) pattern temporali, (2) community/gruppi + topic, (3) entity resolution pseudonimi, (4) profiling di Nadia Conti.

## Stato attuale (aggiornare quando cambia)
- **Tab 1 — Pattern Temporali:** ✅ ottimizzata. Heatmap giorno×ora (08:00–15:00), 1 marcatore per messaggio a **divisione orizzontale** (metà sotto=tipo mittente, metà sopra=tipo destinatario, **nessuna iniziale**, le due metà a spigolo vivo si toccano), box Topic, legenda tipi HTML. Pannello **Utenti come menu a tendina** (casella che apre la lista). In **vista panoramica** selezionando un topic le celle mostrano SOLO quel topic (le altre si spengono). Pannello **"Chi influenza chi"** (Task 1c): target + finestra Δ, due liste (lo precedono=mandanti / reagiscono a lui) via **precedenza temporale** (`DataModel.influence`); clic su un messaggio della catena → **anello rosso sulla cella** della heatmap.
- **Tab 2 — Rete & Gruppi:** ✅ ottimizzata. Due sotto-viste (toggle): "Gruppi & Topic" (force graph Louvain a **layout sincrono** — 300 tick + clamp + `stop()` come la Tab 4, quindi verificabile nel browser interno e senza ballonzolamento; aloni; pannello per gruppo con barre **Topic** E barre **"Eventi di corruzione"** = categorie `CORRUPTION_EVENTS` contate sui messaggi INVIATI dai membri; **clic su una barra evento → messaggi del gruppo con keyword evidenziate**, clic su una barra topic → tutti i messaggi del topic sull'intera rete, back "← Gruppi") e "Esplorazione Rete" (due grafi circolari Communication+Relationship + pannello messaggi con drill-down, ricerca full-text, modo with/about — il modo about usa ancora i `mentions` offline). Le 5 fazioni sono calcolate sull'attribuzione **rettificata**. Le barre evento profilano le fazioni: "Rete Pseudonimi" → 1° evento "Uso di intermediari".
- **Tab 3 — Entity Resolution:** ✅ ottimizzata. **Tre** viste (toggle): "Similarity Heatmap" (comportamentale pseudonimo×entità) / **"Alias delle Navi"** (ex "Radio vs Testo": due matrici di confusione nome-radio×operatore reale, es. Mako→Davis, Remora→Rodriguez) / **"Scioglimento"** (de-anonimizzazione, vedi sotto). Sankey in fondo (scroll), colori nodi = `comm_group` rettificato.
  - **Vista "Scioglimento" (`DataModel.deanonymization`):** collassa ogni alias sull'identità reale. Il grafo NON ha una relazione "è-alias-di" → ogni corrispondenza è una **tesi con la sua evidenza** (score similarità live + relazione operatore), in `DataModel.RESOLUTION` (The Intern→Sam, The Lookout→Kelly, Small Fry→Rodriguez). L'**anello** `DataModel.RING` (Boss, The Middleman, The Accountant, Mrs. Money) non si risolve in un nome → nodo unico "Rete Pseudonimi". Prima/dopo per volume: **40→34 attori**, "Rete Pseudonimi" con **97 msg** al 2° posto (prima invisibile, spezzata in 4 handle). Risponde ai due punti scoperti del Task 3: alias condivisi + cambio d'interpretazione.
- **Tab 4 — Dossier Nadia Conti:** ✅ ottimizzata (*dossier a prove*, ora **scrollabile**: wrapper `overflow-y-auto` + `min-h-[900px]`, su schermi bassi si scorre invece di schiacciare i pannelli). Sinistra, 3 pannelli: ego-network della compromissione (area ∝ n. messaggi, rosso=pseudonimo, arancio=contatto compromesso, tratteggio=arco dedotto; clic → filtra prove E grafico eventi) + timeline delle prove (1 cerchio per messaggio, pieno=incriminante, clic → scrolla alla prova; bottone **"Messaggi indiretti"** = `filters.showIndirect`, default OFF, indiretti col bordo ambra) + **"Eventi di corruzione nel tempo"** (dallo stile del video di riferimento: una LINEA per categoria, conteggio GIORNALIERO non cumulato, pallini nei giorni con eventi, toggle scope **Target/Tutte**, legenda HTML sotto il grafico). Destra: "Catena delle prove" = i **38** messaggi che coinvolgono/nominano Nadia. Wordcloud eliminata (rimosso anche il CDN d3-cloud).
  - **`DataModel.CORRUPTION_EVENTS`** = i "**nuovi topic**" della Tab 4: ~10 categorie keyword (Gestione permessi, Uso di intermediari, Accessi non autorizzati, Pagamenti illeciti & tangenti, Attività sospetta, Abuso di riservatezza, Distruzione di documenti, Accessi speciali, Favoritismi, Riciclaggio), regex **calibrate sui `content` reali** (contare i match PRIMA di fissare le keyword). In tutta la Tab 4 i "topic" mostrati sono queste categorie, NON i topic BERTopic (che restano in Tab 1/2): chip sui cartellini della catena (via `corruptionEventsOf`), "tema dominante" nel riepilogo.
  - **Indiretti = nome nel testo** (`DataModel.aboutRegex`, whole-word; per le persone anche i token distintivi "Nadia"/"Conti", per gli pseudonimi SOLO il nome completo — "Mrs. Money" col token "money" aggancerebbe mezzo dataset). Sostituisce il campo `mentions` offline, troppo conservativo: trovava 5 indiretti contro i 15 reali (era la discrepanza col video di riferimento). Dossier Nadia: **38 = 23 diretti + 15 indiretti, 24 incriminanti**, 3 rettifiche radio (badge azzurro), 0 incerti.
  - **5 capi d'accusa** = regole keyword trasparenti (`DataModel.ACCUSE`): Distruzione di prove, Corruzione & favori, Depistaggio & false dichiarazioni, Occultamento dell'operazione, Costruzione illecita a Nemo Reef. Sono l'**accusa formale** (filtri, flag incriminante, evidenziazione frasi) — tassonomia DISTINTA dagli eventi di corruzione.
  - Il selettore target generalizza lo strumento (su "Boss" il rapporto incriminanti/totale crolla → il contrasto è esso stesso un risultato).
  - ⚠️ Trappola di layout nel pannello eventi: la legenda HTML va popolata **PRIMA** di misurare il `clientHeight` del chart, altrimenti l'asse X finisce fuori dall'SVG (tagliato).

## File chiave
- `src/index.html` — **la dashboard**, single-file: Vue 3 + D3 v7 + d3-sankey + Tailwind (tutto via CDN; d3-cloud rimosso con la wordcloud). Contiene 3 blocchi: `DataModel` (layer dati/derivazioni + **attribuzione rettificata in `init()`**), `D3Charts` (rendering), app Vue (stato/tab).
- `src/data.js` — **generato**, `window.VAST_DATA` = grafo reale + campi calcolati offline. NON modificare a mano.
- `data/processed/vast_mc3_optimized.json` — sorgente di `data.js` (1159 nodi, 3226 link) con campi arricchiti.
- `scripts/regen_bertopic.py` — rigenera topic (BERTopic) + `mentions` ("about") + `commGroups` (Louvain). ⚠️ qui `mentions`/`commGroups` girano ancora sulla radio grezza (`text_from` non esiste ancora): è il PRIMO passo, non l'ultimo.
- `scripts/resolve_senders_bert.py` — aggiunge `text_from`/`text_to` + `text_from_src`/`text_to_src` (mittente/dest reale via regole + BERT QA). Esegue DOPO regen_bertopic.
- `scripts/regen_groups.py` — **NUOVO**. RICALCOLA `mentions` + `commGroups` (Louvain res=1.3) sull'attribuzione **rettificata** (regola canon). Esegue ULTIMO (dopo resolve_senders_bert). Leggero: solo `networkx`, non ritocca i topic BERTopic (non dipendono dall'attribuzione). Le 5 fazioni derivano da qui.
- `docs/` — design_rationale, mockup, storyboard (in italiano).
- Riferimenti esterni sul Desktop: `2025-SusComVis-VAST-Challenge.pdf` (paper FGV) e un riassunto tesi Verhagen (Utrecht).

## Qualità dei dati (audit fatto il 2026-07-14)
Il grafo grezzo **sulle comunicazioni è già pulito**: 584 Communication, 14 giorni pieni (1–14 ott 2040), 0 mittenti/destinatari mancanti, 0 contenuti vuoti, 0 archi duplicati, 0 problemi sui nomi delle 72 entità. Solo 8 testi duplicati (4 coppie) e 1 timestamp anomalo (un `VesselMovement` del 2023, escluso dai filtri). **Non serve il preprocessing pesante della tesi Verhagen** (dedup, normalizzazione nomi, parsing date).

**Il vero problema è l'attribuzione mittente/destinatario**, ed è per design (è il Task 3):
- I metadati radio (archi `sent`/`received`) contraddicono il testo in **177 casi su 584 (30%)**, inclusi **31 auto-anelli** tipo `Davis → Davis` dove il testo dice «Davis, Mako here».
- Ma **nemmeno `text_from`/`text_to` sono verità**: dipende da QUALE pattern li ha prodotti.
- **La discriminante sono le FORMULE D'APERTURA del protocollo radio, che fissano entrambi i ruoli senza ambiguità.** Sono 5 (lista `CANON` in `resolve_senders_bert.py`): «Dest, Mitt **here**» · «Dest, Mitt **reporting/responding**» · «Dest, **this is** Mitt» · «Mitt **here to** Dest» · «Mitt **to** Dest». Quando c'è una di queste, **il testo batte i metadati radio**. Le estrazioni non canoniche (altre regex, BERT QA) **non vengono mai usate per attribuire**: sono rumorose e generano dubbi inesistenti.
- `resolve_senders_bert.py` salva **`text_from_src` / `text_to_src`** su 3 livelli: **`'canon'`** | `'rule'` | `'bert'`. Bilancio: **541 messaggi canonici su 584, 79 che rettificano la radio, 31 auto-anelli tutti risolti, 0 casi indecidibili.**
- **Regola d'oro (nessuna incertezza gratuita), applicata UNA VOLTA SOLA in `DataModel.init()` e valida per TUTTE le tab:** se entrambi i ruoli sono `'canon'` → il testo vince e **RETTIFICA** la radio; **altrimenti vale la radio**. `from`/`to` sono l'attribuzione rettificata (usata ovunque); `radioFrom`/`radioTo` conservano il grezzo, **usato solo dalla Tab 3**, che esiste apposta per confrontare le due fonti (usare lì `from`/`to` annullerebbe la discrepanza da mostrare). La Tab 4 dichiara le rettifiche con un badge azzurro.
- **Impatto reale:** con la radio grezza il mittente n°1 risultava `Green Guardians` (44 msg) — falso, erano gli auto-anelli «Green Guardians, Sentinel reporting» in cui ne è il *destinatario*. Dopo la rettifica sparisce dai primi 5 e `Mako` sale da 35 a 52. Cambia heatmap, rete, gruppi e dossier: per questo la regola sta nel DataModel e non in una singola tab.
- Bug delle regole trovati e corretti (erano loro a produrre le attribuzioni assurde): (1) le regex cercavano in tutto il messaggio (`«…it's a protected area»` → mittente "Protected areas"); (2) leggevano «The Lookout here!» come *destinatario*; (3) il matcher dei nomi usava il primo token, condiviso tra entità diverse (`Sailor Shift` la Person vs `Sailor Shifts Team` l'Organization) — ora usa solo **token discriminanti** (`shifts`→Team, `miesel`→V. Miesel Shipping, così riconosce anche «V. Miesel HQ»); (4) lo splitter di frase troncava i preamboli con abbreviazioni («Davis here to V. Miesel Shipping» → «Davis here to V.») — **rimosso**, le formule sono già ancorate all'inizio; (5) mancava il verbo `reporting`/`responding`, ed erano proprio quei 13 messaggi a restare irrisolti.

## Dati reali — fatti da ricordare
- Comunicazioni SOLO diurne (ore 8–14, picco 10:00). **Nessuna attività notturna** (contraddice gli storyboard iniziali — vedi memoria `storyboard-vs-dati-reali`). Le date delle comunicazioni sono pulite: 14 giorni, 1–14 ottobre 2040 (la vecchia nota "date sporche 2023→2040" riguardava *tutti* gli eventi, non le comunicazioni).
- 72 entità (18 Person, 15 Vessel, 5 Org, 5 Group, 29 Location); 584 Communication; campo `is_inferred` per l'incertezza.
- **7 pseudonimi:** Boss, The Lookout, The Intern, The Middleman, Mrs. Money, Small Fry, The Accountant.
- **5 gruppi** (Louvain res=1.3, su attribuzione **rettificata** via `regen_groups.py`): **Navi & Operazioni in Mare, Istituzioni & Permessi, Rete Pseudonimi, Ambiente & Conservazione, Giornalisti.** (La vecchia macro-fazione "Sailor Shift & Logistica" si è scissa in "Navi & Operazioni in Mare" + "Istituzioni & Permessi" — quest'ultima è il lato permessi corrotti del dossier Nadia; "Pesca & Diporto" è sparita, Serenity/Marlin sono in "Navi".)
- **9 topic** BERTopic curati (Permessi & Clearance, Estrazione Sospetta, Operazioni Notturne, Conservazione, Valutazioni Ambientali, Produzione Videoclip, ecc.).
- Entity resolution (Task 3): The Intern≈Sam, The Lookout≈Kelly, Boss↔Middleman↔Accountant (ring); nave→operatore Davis⇄Mako, Rodriguez⇄Remora.
- **Nadia Conti (Task 4) — la prova è nei `content`, non nella topologia.** **38 messaggi** nel dossier (23 diretti + 15 indiretti via `aboutRegex`; 3 attribuzioni radio corrette dal preambolo, 0 incerte), **24 incriminanti**; tema dominante (eventi di corruzione): **Gestione permessi**. Catena: permit **#CR-7844** su Nemo Reef (area protetta) ottenuto con favori al permit office (Commissioner Torres firma in poche ore) → 10-05 09:45 ordina a Haacklee Harbor «Destroy all related documentation» → 09:47 il porto la denuncia al Council → 09:49 mente al Council («I wasn't aware of any permit approvals») → corrompe Liam Thorne (doppia parcella perché «Harbor Master remains cooperative», lui: «Council suspects nothing») → depista Marlin/EcoVigil → costruzione subacquea permanente con «tourism facade maintained». **Non agisce sola:** The Accountant, The Middleman, Davis, Elise, Neptune, Liam Thorne, V. Miesel Shipping.
- **Storyboard (`docs/storyboards/task1..4_pattern.md`): RISCRITTI** e allineati alla dashboard attuale (rimossa ovunque l'attività notturna smentita; fazioni, viste e nomi reali; persona uniformata a "Clepper Jensen").

## Rigenerare i dati
```bash
python scripts/regen_bertopic.py        # 1) topic BERTopic (+ mentions/commGroups provvisori su radio grezza)
python scripts/resolve_senders_bert.py  # 2) text_from/text_to + *_src (transformers; usa AutoModelForQuestionAnswering, NON il pipeline QA)
python scripts/regen_groups.py          # 3) RICALCOLA mentions + commGroups sull'attribuzione RETTIFICATA (solo networkx)
```
L'ordine conta: i gruppi/mentions definitivi vengono dal passo 3. Tutti e tre riscrivono `data/processed/vast_mc3_optimized.json` E `src/data.js`. UMAP ha `random_state=42` (riproducibile).

## Come testare (workflow)
- **L'utente** apre `src/index.html` con doppio-click: funziona (data.js incluso via `<script>`, niente CORS).
- **Per Claude nel browser interno:** `python -m http.server 8777` dentro `src/`, poi navigare a `http://127.0.0.1:8777/index.html`. Il browser interno **NON apre `file://`**.
- **Cache:** dopo una modifica, il browser interno serve la versione in cache → navigare con `?v=N`. Se cambia `data.js`, il cache-busting sull'HTML non basta: **usare una porta nuova**.
- **Verifica:** gli screenshot vanno **sempre** in timeout (pagina pesante) → verificare via `javascript_tool` sul DOM + `read_console_messages` (deve essere pulita). Per i layout, misurare i bounding box degli elementi contro quello dell'SVG.
- ⚠️ **Nel browser interno il tab è nascosto → `requestAnimationFrame` è sospeso → le force-simulation animate NON fanno nemmeno un tick.** Per questo **sia l'ego-network (Tab 4) sia il force graph (Tab 2)** risolvono la simulazione **in modo sincrono** (300 tick + clamp, poi `stop()`; il drag la rimette in moto): verificabili nel browser interno e niente ballonzolamento all'apertura.
- ⚠️ Se il pannello browser ricrea il tab (es. dopo che un hook apre il file in `file://`), il viewport può risultare **0×0** (`window.innerHeight === 0` → i chart escono subito con width/height 0). Rimedio: `resize_window` a una misura reale e poi `window.dispatchEvent(new Event('resize'))`.
- Fermare sempre il server a fine test. `pkill` **non esiste** su Windows: usare PowerShell → `Get-CimInstance Win32_Process -Filter "Name like '%python%'" | Where-Object { $_.CommandLine -like '*http.server*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }`.
- Sanity JS: estrarre lo `<script>` principale e `node --check`.

## Lavoro fatto nelle sessioni recenti
**2026-07-15** — copertura dei 4 task completata: `regen_groups.py` → 5 fazioni rettificate; Sankey su `comm_group`; Tab 1 "Chi influenza chi"; Tab 2 lista messaggi per topic; Tab 3 "Alias delle Navi" + "Scioglimento"; storyboard riscritti.

**2026-07-16** — Tab 2 e Tab 4 riallineate a un video di riferimento che risolve la challenge:
1. **Tab 2 a layout sincrono** (stesso pattern della Tab 4) → verificabile nel browser interno, niente ballonzolamento. Chiuso il vecchio Prossimo passo #3.
2. **Tab 4 scrollabile** (i 3 pannelli sinistri non si schiacciano più su schermi bassi).
3. **Timeline prove: bottone "Messaggi indiretti"** (default OFF; indiretti col bordo ambra + nota nel tooltip).
4. **Nuovo grafico "Eventi di corruzione nel tempo"** al posto dell'evoluzione topic: `DataModel.CORRUPTION_EVENTS` (~10 categorie keyword calibrate sui `content` reali), linee giornaliere per categoria, toggle **Target/Tutte**, filtro per contatto dal clic sull'ego-network, legenda HTML sotto il grafico.
5. **"Nuovi topic" in tutta la Tab 4**: i cartellini della catena mostrano chip di eventi di corruzione (via `corruptionEventsOf`) e il "tema dominante" usa le stesse categorie; via i badge BERTopic.
6. **Indiretti = nome nel testo** (`DataModel.aboutRegex`): dossier Nadia 28→**38** (15 indiretti), incriminanti 18→**24**. Il campo `mentions` offline resta in uso solo nella Tab 2 (modo about).
7. **Tab 2: barre "Eventi di corruzione" per gruppo** nella card di ogni fazione (conteggio sui messaggi inviati dai membri) + drill-down con keyword evidenziate.
8. Pulizia: rimossi `topicColor`/`TOPIC_PALETTE` (morti dopo il punto 4).

## Prossimi passi (aperti)
1. **Verifica end-to-end nel browser dell'utente** (doppio-click su `src/index.html`).
2. Eventuali ritocchi estetici.
3. Opzioni Tab 2 rimaste sul tavolo (proposte, non richieste): evidenziazione dei vicini al clic sul force graph; grafi circolari ordinati per fazione; "ponte" nodo → dossier Tab 4.

## Convenzioni / gusto
- UI e commenti in **italiano**. Palette tipi = **Okabe-Ito** (alto contrasto). Approccio: derivazioni pesanti OFFLINE in Python embeddate in data.js; il frontend deriva il resto in JS. Ogni modifica va verificata nel browser prima di dichiararla fatta.
- **Il dubbio si dichiara solo dove è reale.** Non marcare come "incerto" ciò che una regola trasparente sa risolvere (l'utente lo ha chiesto esplicitamente), ma non correggere mai in silenzio: quando la dashboard rettifica un dato, deve dirlo e mostrare l'originale.
- Note di dettaglio più granulari nelle memorie: `project-vast-mc3`, `qualita-dati-attribuzione`, `tab1-topic-model`, `tab2-rete-comunicazione`, `dimensione-about-e-pannello-messaggi`, `tab3-entity-resolution`, `tab4-dossier-nadia`.
