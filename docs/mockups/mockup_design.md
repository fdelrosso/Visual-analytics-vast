## Wireframing e UI Design

## Architettura della Sidebar dei Filtri (Filtro Dinamico)
La sidebar è progettata seguendo il paradigma del **Cross-filtering**. Ogni interazione dell'utente con un widget aggiorna istantaneamente sia il grafo principale che gli altri widget della sidebar stessa, supportando il *sense-making* investigativo.

### Mappatura delle Dimensioni sui Widget
* **T-Nodes (Tipi di Nodi):** Gestiti tramite Checkbox Group (Entity, Event, Relationship). Permette di nascondere la struttura logica per concentrarsi solo sugli attori.
* **T-Links (Tipi di Legami):** Dropdown a selezione multipla (sent, received, evidence_for, structural).
* **P-Nodes (Proprietà dei Nodi):**
  * *Fazione (Louvain):* Color Legend interattiva. Cliccando su una fazione (es. Green Guardians), si isola la sua rete.
  * *Degree Centrality:* Range Slider. Permette di sfoltire l'Hairball nascondendo i nodi periferici (es. grado < 3).
  * *Identità:* Toggle Switch "Evidenzia Pseudonimi" per il Task 3.
* **P-Links (Proprietà dei Legami):**
  * *Fasce Orarie:* **Istogramma (Bar Chart) Interattivo**. Funge da "Time Brush". L'altezza delle barre mostra il volume di eventi. Cliccando sulla barra "Notte (00:00 - 05:00)", l'intera dashboard si filtra.
  * *Incertezza (is_inferred):* Toggle Switch per abilitare/disabilitare i collegamenti dedotti, modificando la codifica visiva degli archi (da linea continua a tratteggiata).