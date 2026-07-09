# Definizione del Target User e Scenario d'Uso

## Identikit dell'Utente Target (Target User Persona)
Per garantire l'efficacia dell'interfaccia di Visual Analytics, il design è calibrato sulle specifiche competenze del seguente utente:

* **Nome:** Clepper Jessen
* **Professione:** Giornalista investigativo per l'Hacklee Herald ed ex analista presso FishEye.
* **Competenze (Domain Knowledge):** Possiede una profonda conoscenza del contesto locale dell'isola di Oceanus (dinamiche politiche, movimenti navali, storici criminali). Tuttavia, **non è un esperto di teoria dei grafi**, data science o programmazione complessa.
* **Obiettivo Analitico Principale:** Estrarre conoscenza (sense-making) da un *Knowledge Graph* che mappa due settimane di comunicazioni radio intercettate. L'obiettivo è superare il rumore e l'incertezza dei dati per dimostrare l'esistenza di una rete logistica illecita operante sotto la copertura del turismo.

## Obiettivi Operativi (I 4 Task della MC3)
La dashboard deve permettere a Clepper di rispondere autonomamente a queste 4 domande:
1. **Analisi Temporale:** Identificare pattern giornalieri ricorrenti nelle comunicazioni e la loro evoluzione nel corso delle due settimane.
2. **Community Detection:** Riconoscere i gruppi/fazioni principali (Ambientalisti, Sailor Shift, Pesca/Logistica) e i topic di cui discutono.
3. **Entity Resolution:** Scoprire quali identità reali si nascondono dietro l'uso di pseudonimi ricorrenti (es. "Boss", "The Lookout") analizzando le sovrapposizioni comportamentali.
4. **Target Profiling:** Raccogliere prove visive inconfutabili per determinare se Nadia Conti è coinvolta o meno in attività illegali a Nemo Reef.

## Scenario d'Uso (Usage Scenario)
Il workflow tipico dell'utente all'interno della piattaforma seguirà i principi dell'*Information Foraging* e della navigazione Top-Down (Overview first, zoom and filter, then details-on-demand):

> Clepper accede al sistema avendo a disposizione l'intero dataset grezzo delle intercettazioni. Sospettando attività illecite notturne presso la barriera corallina (Nemo Reef), utilizza la **Sidebar dei Filtri** per isolare la fascia oraria "00:00 - 05:00". 
> Il sistema fornisce un feedback visivo immediato aggiornando la **Visualization Grid**: la vista temporale (*Overview*) evidenzia un picco anomalo di messaggi in quella finestra, mentre il grafo delle relazioni aggregato (*Community View*) rivela che i canagitli ufficiali sono silenti, lasciando attive solo comunicazioni tra entità associate a pseudonimi (es. "Boss").