## Storyboard Task 3 — Alias di Persone e Navi (Entity Resolution)

* **Obiettivo del Task (VAST MC3):** Determinare quali individui **e imbarcazioni** usano alias e identificarli; tenere presente che **più entità possono condividere lo stesso alias**; spiegare come le visualizzazioni facilitano l'identificazione e come — sciogliendo gli pseudonimi — **cambia la lettura dei fatti**.

*Actor: Clepper Jensen.*

### Il workflow: tre lenti complementari (toggle in alto)

* **Passo 1 — Similarity Heatmap (i nomi in codice)**
Clepper apre la prima vista: una matrice **pseudonimo × entità** di similarità comportamentale (contatti in comune 50% · topic 30% · orario 20%). Le celle accese suggeriscono stessa identità o coordinamento. Emergono un match netto — **The Intern ≈ Sam** (0.80) — e un blocco caldo tra Boss, The Middleman, The Accountant e Mrs. Money: non somigliano a una persona nota, ma **tra loro**.

* **Passo 2 — Alias delle Navi (nave → operatore)**
Seconda vista: due matrici di confusione fra il **nome-radio** e l'**operatore reale** ricavato dal preambolo del testo. Il call-sign di una nave maschera chi la guida: **Mako → Davis, Remora → Rodriguez**. Le celle fuori diagonale sono le attribuzioni rettificate — la stessa correzione che regge tutte le altre tab. È la risposta alla parte "which vessels use aliases".

* **Passo 3 — Scioglimento (de-anonimizzazione)**
Terza vista, il colpo di scena. Clepper collassa ogni alias sull'identità reale. Il grafo **non contiene** una relazione "è-alias-di": ogni corrispondenza è una **tesi con la sua evidenza** (score di similarità calcolato live + relazione operatore). L'anello Boss/Middleman/Accountant/Mrs. Money non si risolve in un nome → diventa un unico nodo **"Rete Pseudonimi"**. Risultato: **da 40 a 34 attori**, e la "Rete Pseudonimi" con **97 messaggi** balza al 2° posto per volume (dietro solo Mako) — prima era invisibile, spezzata in quattro handle piccoli. The Intern→Sam, The Lookout→Kelly, Small Fry→Rodriguez completano lo scioglimento.

* **Passo 4 — I flussi (Sankey)**
In fondo, il Sankey dei flussi pseudonimi conferma il raggio d'azione: chi manda a chi, con l'opzione di isolare i soli flussi sospetti.

* **Conclusione Task 3:**
Sciogliere gli pseudonimi cambia la scena: persone note (Kelly, Sam, Rodriguez) risultano molto più attive di quanto sembrasse, e a dominare il traffico occulto non è un singolo "Boss" ma un **anello coordinato** di più handle. È la risposta ai due punti spesso trascurati del task: **alias condivisi/coordinati da più entità** e **come cambia l'interpretazione** una volta sciolti.
