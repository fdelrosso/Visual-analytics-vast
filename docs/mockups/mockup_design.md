## Wireframing e UI Design

## Architettura della Sidebar dei Filtri (Filtro Dinamico)
La sidebar è progettata seguendo il paradigma del **Cross-filtering**. Ogni interazione dell'utente con un widget aggiorna istantaneamente sia il grafo principale che gli altri widget della sidebar stessa, supportando il *sense-making* investigativo.

## Mappatura delle Dimensioni sui Widget
* **T-Nodes (Tipi di Nodi):** Gestiti tramite Checkbox Group (Entity, Event, Relationship). Permette di nascondere la struttura logica per concentrarsi solo sugli attori.
* **T-Links (Tipi di Legami):** Dropdown a selezione multipla (sent, received, evidence_for, structural).
* **P-Nodes (Proprietà dei Nodi):**
  * *Fazione (Louvain):* Color Legend interattiva. Cliccando su una fazione (es. Green Guardians), si isola la sua rete.
  * *Degree Centrality:* Range Slider. Permette di sfoltire l'Hairball nascondendo i nodi periferici (es. grado < 3).
  * *Identità:* Toggle Switch "Evidenzia Pseudonimi" per il Task 3.
* **P-Links (Proprietà dei Legami):**
  * *Fasce Orarie:* **Istogramma (Bar Chart) Interattivo**. Funge da "Time Brush". L'altezza delle barre mostra il volume di eventi. Cliccando sulla barra "Notte (00:00 - 05:00)", l'intera dashboard si filtra.
  * *Incertezza (is_inferred):* Toggle Switch per abilitare/disabilitare i collegamenti dedotti, modificando la codifica visiva degli archi (da linea continua a tratteggiata).








## La Griglia Modulare a Due Righe (Visualization Grid)

Lo spazio visivo principale (a destra della Sidebar) è strutturato in una griglia 2x2, studiata per guidare l'indagine di Clepper dai pattern globali ai dettagli specifici (Shneiderman's Mantra). 

### Riga 1: Overview (Il Contesto Globale)
I due moduli superiori offrono una visione d'insieme del Knowledge Graph, rispondendo ai Task 1 e 2 della VAST Challenge senza causare *Hairball effect*:
* **Modulo Temporale (Top-Left):** Un grafico a linee o a barre (*Line/Bar Chart*) che mostra il volume delle comunicazioni lungo le due settimane. Serve a identificare picchi anomali (es. un'impennata di messaggi di notte durante il weekend).
* **Modulo Community (Top-Right):** Un grafo aggregato (es. *Packed Bubble Chart* o *Force-Directed Graph* raggruppato). Invece di mostrare i 1159 nodi, mostra solo 3-4 grandi bolle rappresentanti le fazioni estratte con l'algoritmo di Louvain (Ambientalisti, Istituzioni, Operatori Marittimi).

### Riga 2: Detail-on-Demand (L'Indagine Specifica)
I due moduli inferiori si popolano e si raffinano in base a ciò che l'utente seleziona nei moduli superiori (Cross-filtering), rispondendo ai Task 3 e 4:
* **Modulo Flussi/Identità (Bottom-Left):** Un diagramma di Sankey o una Matrice di Adiacenza. Traccia in modo lineare chi parla con chi tra gruppi specifici. È essenziale per il Task 3: isolare i flussi di comunicazione dei nodi pseudonimo ("Boss", "The Lookout") per capire con quali entità reali condividono pattern.
* **Modulo Ego-Network (Bottom-Right):** Il microscopio dell'analista. Un grafo *Node-Link* classico ma limitato a 1 o 2 gradi di separazione da un nodo target. Quando Clepper seleziona "Nadia Conti" in una vista, questo modulo isola lei e i suoi contatti diretti, mostrando chiaramente i legami certi e quelli dedotti (tratteggiati).







## Definizione dei Trade-off Visivi (Design Rationale)

La progettazione dei quattro moduli visivi e della sidebar interattiva è il risultato di precise scelte di design, volte a massimizzare l'efficacia analitica per l'utente (Clepper) a fronte della complessità del dataset. Di seguito vengono documentati i principali trade-off visivi accettati:

### 1. Astrazione vs. Dettaglio Topologico (Il problema dell'Hairball)
* **Scelta:** Utilizzare una *Community View* (bolle aggregate per fazione) nell'Overview, rinunciando a un diagramma globale Node-Link.
* **Trade-off:** Si sacrifica la visibilità della topologia esatta del grafo originale (che è composto da ben 1159 nodi e 3226 archi[cite: 2]). Visualizzare l'intero network avrebbe generato un "hairball" (groviglio) illeggibile. L'astrazione semantica per fazioni permette all'utente di identificare immediatamente i macro-gruppi (Task 2), delegando l'esplorazione topologica alle viste di dettaglio.

### 2. Focus Locale vs. Contesto Globale (L'Ego-Network)
* **Scelta:** Utilizzare un *Ego-Network* per analizzare i target specifici (come Nadia Conti), nascondendo il resto del grafo.
* **Trade-off:** L'utente perde la consapevolezza della posizione del target rispetto alla periferia della rete (Contesto Globale). In cambio, ottiene una pulizia visiva assoluta sui legami diretti di 1° e 2° grado (Focus Locale), essenziale per il Task 4 (raccogliere prove sui contatti diretti del target) e per distinguere chiaramente gli archi "certi" da quelli "dedotti" (is_inferred).

### 3. Analisi Temporale vs. Animazione di Rete
* **Scelta:** Utilizzare un Istogramma a barre statico nella Sidebar (aggiornabile tramite Cross-filtering) invece di un'animazione che fa scorrere il grafo nel tempo.
* **Trade-off:** Si rinuncia a mostrare visivamente l'evoluzione dinamica della struttura del grafo (animazione), che è soggetta al fenomeno della *Change Blindness* (cecità al cambiamento). Si opta per un istogramma che permette all'occhio umano di rilevare istantaneamente, tramite l'altezza delle barre, i pattern temporali ricorrenti (Task 1), delegando al cross-filtering l'aggiornamento topologico.

### 4. Flusso vs. Metriche di Rete (Entity Resolution)
* **Scelta:** Utilizzare un diagramma di flusso (Sankey) o una matrice per l'allineamento degli pseudonimi, anziché metriche di centralità stampate a schermo.
* **Trade-off:** Invece di richiedere all'utente di leggere tabelle di similarità matematica, il flusso visivo mostra la ripartizione dei messaggi inviati e ricevuti[cite: 4]. Questo sacrifica la precisione numerica a favore di un *Pattern Matching* visivo immediato, rendendo intuitivo il Task 3 (scoprire chi si cela dietro "Boss" o "The Lookout").