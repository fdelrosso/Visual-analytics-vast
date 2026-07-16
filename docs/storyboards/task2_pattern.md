## Storyboard Task 2 — Interazioni, Fazioni e Topic

* **Obiettivo del Task (VAST MC3):** Aiutare Clepper a esplorare le interazioni e le relazioni tra imbarcazioni e persone nel knowledge graph; individuare i gruppi strettamente associati e determinare i **temi predominanti** di ciascun gruppo.

*Actor: Clepper Jensen.*

### Il workflow investigativo (sense-making)

* **Passo 1 — Dalle 1159 entità a 5 fazioni (vista "Gruppi & Topic")**
Invece dell'illeggibile hairball, Clepper vede un force graph con i nodi raggruppati in **5 fazioni** (Louvain), ciascuna con un alone colorato. Dettaglio decisivo: le fazioni sono calcolate sull'attribuzione **rettificata** dei messaggi (vedi Task 3), non sui metadati radio grezzi. Con la radio grezza "Green Guardians" risultava per errore il mittente n°1 (erano auto-anelli tipo «Green Guardians, Sentinel reporting»). Le 5 fazioni reali: **Navi & Operazioni in Mare, Istituzioni & Permessi, Rete Pseudonimi, Ambiente & Conservazione, Giornalisti.**

* **Passo 2 — Il tema di ogni gruppo**
Nel pannello di destra ogni fazione mostra i suoi **topic predominanti** come barre (es. "Istituzioni & Permessi" → Permessi & Clearance in testa). I 9 topic sono BERTopic calcolati offline. Clepper legge non solo *chi* sta con chi, ma *di cosa* parlano.

* **Passo 3 — Dal topic ai messaggi**
Clepper clicca la barra "Permessi & Clearance": il pannello si trasforma nella **lista di tutti i messaggi** di quel topic sull'intera rete, ciascuno con mittente→destinatario e testo. Può leggere le prove dietro l'etichetta, invece di fidarsi di un conteggio. Un pulsante "← Gruppi" riporta alla vista delle fazioni.

* **Passo 4 — Esplorazione della rete (chi parla CON chi / DI chi)**
Passa alla sotto-vista "Esplorazione Rete": due grafi circolari, uno delle **Comunicazioni** e uno delle **Relazioni**. Selezionando un'entità, il pannello messaggi mostra le sue comunicazioni con drill-down, ricerca full-text e la distinzione tra "parla **con**" e "si parla **di**" (dimensione *about*, dai mentions nel testo).

* **Conclusione Task 2:**
Clepper ha mappato l'ecosistema: cinque fazioni con temi netti. La più rilevante per l'inchiesta non è quella ambientalista, ma **Istituzioni & Permessi** — dove siedono Nadia Conti, l'Oceanus City Council e i porti — e la **Rete Pseudonimi**, che il Task 3 scioglierà per rivelare chi c'è davvero dietro gli handle.
