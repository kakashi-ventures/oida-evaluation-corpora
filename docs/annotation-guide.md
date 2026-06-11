# Annotation Guide — "Similarity Is Not Enough" (Paper 2)

> Guida di annotazione **machine-fillable** per compilare i nuovi gold dei test del
> paper *Similarity Is Not Enough: Epistemic Configurations and Bounded Salience for
> Organizational Retrieval*. È pensata per essere data in pasto a Claude Code: ogni
> file ha uno **schema esatto**, un **vocabolario controllato chiuso**, e regole di
> **integrità referenziale** verificabili da `docs/validate_annotations.py`.
>
> Regola d'oro: **se non è in questo documento, non inventarlo.** Niente campi nuovi,
> niente valori di enum fuori lista, niente ID che non risolvono. Esegui sempre il
> validatore prima di considerare un corpus "fatto".

---

## 0. Come usare questa guida con Claude Code

1. Leggi `docs/format.md` (il contratto BEIR di base: `corpus.jsonl`, `queries.jsonl`,
   `qrels/test.tsv`). Questa guida lo **estende**, non lo sostituisce.
2. Scegli un corpus e individua, dalla §6 (matrice di copertura), **quali layer** vanno
   annotati per quel corpus.
3. Per ogni layer, compila i file nello schema esatto delle §3–§5.
4. Usa solo i **vocabolari controllati** della §1 e i **cutoff** della §2.
5. Esegui `python3 docs/validate_annotations.py corpora/<id>`: **deve uscire `OK`**,
   zero `ERROR`. I `WARN` vanno letti ma non bloccano.
6. Non toccare mai `corpus.jsonl` per inserire gold: resta neutro (cfr. `format.md`).
   Tutti i gold stanno in `qrels/` e `annotations/`.

### Layout finale di un corpus organizzativo (tutti i layer)

```
corpora/<id>/
├── corpus.jsonl                      # invariato (neutro, nessun gold)
├── queries.jsonl                     # + metadata: query_time, temporal_intent (§3)
├── qrels/
│   ├── test.tsv                      # invariato (end-of-corpus, BEIR core)
│   ├── test_t<t0>.tsv                # time-sliced al cutoff t0   (§4.2)
│   ├── test_t<t1>.tsv                # time-sliced al cutoff t1
│   └── test_t<t2>.tsv                # time-sliced al cutoff t2
├── annotations/
│   ├── doc_state.jsonl               # lifecycle + validità per doc, per cutoff (§4.1)
│   ├── edges.jsonl                   # archi tipati/firmati (supersedes, …)      (§4.3)
│   ├── stance.tsv                    # gold stance per query                     (§5.1)
│   └── traps.tsv                     # trap doc (score 0) per query              (§5.2)
└── README.md                         # dataset card (aggiorna i contatori)
```

I corpora investigativi (`inv-*`) ricevono **solo** `stance.tsv` (Layer 3 *partial*) e
non hanno file temporali — vedi §6.

---

## 1. Vocabolari controllati (ENUM chiusi)

Usa **esattamente** queste stringhe, minuscole dove indicato. Qualsiasi altro valore è
un `ERROR` di validazione.

### 1.1 `lifecycle_state` (9 valori — paper §3.3)

| valore | regime | semantica |
|---|---|---|
| `provisional` | working (W) | proposta/bozza, non ancora attiva |
| `active` | working (W) | corrente e operativa, non ancora ratificata |
| `unknown` | working (W) | ignoranza registrata (open question) |
| `canonical` | canonical (C) | ratificata, vincolante, sopravvissuta a review |
| `stale` | degraded | non più corrente, non ancora obsoleta — ancora *rankable* |
| `contradicted` | degraded | in conflitto attivo — ancora *rankable*, bassa priorità |
| `superseded` | obsolete | rimpiazzata da un item successivo |
| `archived` | obsolete | ritirata dal flusso attivo |
| `retracted` | obsolete | ritrattata/annullata |

Mappa regime (paper §3.3, usata da LRA e dal closure): `working = {provisional, active,
unknown}`, `canonical = {canonical}`, `obsolete = {superseded, archived, retracted}`,
`degraded = {stale, contradicted}`.

**Priorità di lifecycle per LRA** (ordine stretto, paper §5.1.3 T11):
`canonical > active > provisional > stale > superseded > archived > retracted`.
`contradicted` e `unknown` sono **esclusi** dalle coppie LRA.

### 1.2 `stance` gold (3 valori — paper §5.1.2)

`supports` · `contradicts` · `neutral`

> `neutral` = il corpus **registra la domanda come aperta** / ignoranza registrata (NEI).
> Le predizioni di sistema possono aggiungere `abstain`/`invalid`, ma il **gold** usa solo
> questi tre valori. Per le metriche di abstention `neutral` e `abstain` vengono collassati
> (broad abstention): non è compito tuo, è del valutatore.

### 1.3 `temporal_intent` (5 valori — paper §5.1.3 / §6.3)

`current_state` · `as_of_time` · `supersession_check` · `change_over_time` · `stable_knowledge`

| intent | la query chiede… | metrica headline |
|---|---|---|
| `current_state` | lo stato vincolante **adesso** (a `query_time`) | CSA@k, SL@k |
| `as_of_time` | lo stato vincolante a una **data passata** | AOA@k |
| `supersession_check` | qual è il doc *binding* vs i superati | MeanRankBinding, SupersededAbove |
| `change_over_time` | come è **evoluta** una decisione | CSA@k + LRA |
| `stable_knowledge` | un fatto **vecchio ma ancora canonico** | SKR@k, FOR |

### 1.4 Relazioni di arco tipate (paper §3.1)

| `relation` | `polarity` | note |
|---|---|---|
| `supports` | `positive` | rinforzo epistemico |
| `implements` | `positive` | |
| `based_on` | `positive` | |
| `contradicts` | `negative` | conflitto/inibizione (simmetrico nella pratica) |
| `blocks` | `negative` | |
| `supersedes` | `directional` | `src` **rimpiazza** `dst`: negativo verso `dst`, primazia di `src` |

> Convenzione direzione **fissa** per `supersedes`: `src` è l'item **nuovo/vincolante**,
> `dst` è l'item **superato**. Non invertire.

---

## 2. Cutoff temporali per corpus (paper Tab. 4)

Tre cutoff per ogni corpus **organizzativo**. Il `<TAG>` nei nomi file qrels e nel campo
`query_time` è **la data ISO del cutoff**.

| corpus | t0 (early) | t1 (mid) | t2 (late) |
|---|---|---|---|
| `org-consulting-clearpath` | `2025-09-30` | `2025-11-01` | `2025-12-15` |
| `org-iot-fireglass` | `2025-08-31` | `2025-09-30` | `2025-10-31` |
| `org-vc-vertexminds` | `2025-10-31` | `2025-11-10` | `2025-11-20` |

File qrels time-sliced risultanti, es. ClearPath:
`qrels/test_t2025-09-30.tsv`, `qrels/test_t2025-11-01.tsv`, `qrels/test_t2025-12-15.tsv`.

Una vista a un cutoff `T` si ottiene filtrando i doc su `metadata.created <= T` e le query
su `query_time <= T`. Lo stato vincolante (e quindi i punteggi qrels) può cambiare tra un
cutoff e l'altro: un doc vincolante a t0 (score 3) può diventare `superseded` e scendere a
0/1 a t2.

---

## 3. Estensione di `queries.jsonl` (proprietà della query)

`query_time` e `temporal_intent` descrivono **la domanda**, non la risposta: stanno in
`queries.jsonl > metadata` (come già `tests`/`difficulty`). I gold (stance, rilevanza
temporale) **non** stanno qui.

```json
{"_id": "q07", "text": "Which onboarding-time target is currently binding for the ClearPath engagement?", "metadata": {"tests": "onboarding_target_evolution", "difficulty": "medium", "query_time": "2025-12-15", "temporal_intent": "current_state"}}
```

Regole:

| campo | regola |
|---|---|
| `metadata.query_time` | ISO-8601 (`YYYY-MM-DD`). Per query temporali è **obbligatorio**. Per `as_of_time` è il "now" da cui si guarda indietro; la data target del *as-of* è espressa nel testo della query e nei gold di `test_t<as-of>.tsv`. |
| `metadata.temporal_intent` | uno dei 5 valori §1.3. Presente **solo** sulle query temporali. |
| `metadata.tests`, `metadata.difficulty` | restano come in `format.md`. Non rimuoverli. |

Non aggiungere altri campi a `metadata` oltre a quelli definiti qui e in `format.md`.

---

## 4. Layer 4 — stato temporale / lifecycle (solo corpora `org-*`)

### 4.1 `annotations/doc_state.jsonl` — stato per documento e per cutoff

Un oggetto JSON per riga, **un documento per riga**. Annota la validità (statica) e il
`lifecycle_state` **a ciascun cutoff** (può cambiare nel tempo).

```json
{"_id": "05-meetings/meeting-001-kickoff", "valid_from": "2025-09-15", "valid_until": null, "lifecycle_by_cutoff": {"2025-09-30": "active", "2025-11-01": "active", "2025-12-15": "stale"}}
{"_id": "01-scope/project-brief", "valid_from": "2025-09-10", "valid_until": "2025-11-01", "lifecycle_by_cutoff": {"2025-09-30": "active", "2025-11-01": "superseded", "2025-12-15": "superseded"}}
```

| campo | regola |
|---|---|
| `_id` | deve risolvere a un `_id` di `corpus.jsonl`. |
| `valid_from` | ISO-8601. Tipicamente `= metadata.created` del doc. |
| `valid_until` | ISO-8601 **oppure** `null` (intervallo aperto). Se valorizzato: `valid_until > valid_from`. |
| `lifecycle_by_cutoff` | oggetto con **una chiave per ciascun cutoff del corpus** (§2). Ogni valore ∈ enum §1.1. |

Regole di coerenza (controllate dal validatore, livello `WARN` dove non strettamente
formali):
- Monotonia di lifecycle: una volta `obsolete` (`superseded`/`archived`/`retracted`) a un
  cutoff, deve restare obsoleto ai cutoff successivi (no "resurrezione").
- Un doc con `metadata.created > T` **non** deve comparire come gold in `test_t<T>.tsv`
  (non esiste ancora a quel cutoff) → `ERROR`.
- Devi includere in `doc_state.jsonl` **tutti** i doc che compaiono in almeno un
  `test_t<TAG>.tsv`. I doc non-gold sono opzionali (ma consigliati per LRA/SL).

### 4.2 `qrels/test_t<TAG>.tsv` — rilevanza graduata al cutoff

Stesso schema di `qrels/test.tsv` (header `query-id\tcorpus-id\tscore`, TSV, `score`
intero 0–3). Riflette lo **stato vincolante a quel cutoff**.

Rubrica di rilevanza graduata (vale anche per `test.tsv`; il `relevance-guidelines.md`
storico è riassunto qui):

| score | significato | mapping temporale (per TempNDCG, paper §5.1.3 T6) |
|---|---|---|
| `3` | risponde direttamente / **fonte vincolante** | `gold-current` (lo stato corrente a quel cutoff) |
| `2` | supporto forte | `valid-non-primary` (valido ma non primario) |
| `1` | debole / contestuale | `historically-relevant` (storicamente rilevante, ora superato) |
| `0` | giudicato **non** rilevante / trap | irrilevante |

Come derivano i gold-set delle metriche temporali (così sai cosa mettere a 3/2/1/0):

- **CSA@k** (`current_state`): almeno un doc con score 3 (= gold-current) deve esistere
  nel `test_t<query_time>.tsv` della query.
- **SL@k** (Superseded Leakage): i doc obsoleti **non richiesti** dall'intent vanno a `0`
  nello slice corrente; il loro `lifecycle_by_cutoff[query_time]` ∈ obsolete in
  `doc_state.jsonl`. È la combinazione qrels(0) + doc_state(obsolete) che definisce un
  "leak".
- **SKR@k** (`stable_knowledge`): il fatto vecchio-ma-canonico è score 3 e
  `lifecycle = canonical`, con `valid_from` antecedente al cutoff (è "vecchio").
- **FOR** (`stable_knowledge`): serve almeno una coppia (doc recente `provisional` con
  `created` vicino a `query_time`) vs (doc `canonical` vecchio, score 3). Annota entrambi
  in `doc_state.jsonl`.
- **change_over_time**: gli stati intermedi compaiono come 3 nei rispettivi slice
  precedenti e degradano (3→1) nello slice finale.

### 4.3 `annotations/edges.jsonl` — archi tipati e firmati (Layer 2)

Un arco per riga. Servono per: contradiction recall, supersession resolution, e per
costruire il grafo inferenziale.

```json
{"src": "07-documents/report-final", "dst": "07-documents/presentation-interim", "relation": "supersedes", "polarity": "directional"}
{"src": "02-subject/observation-003-audit-workflow", "dst": "02-subject/bottleneck-analysis", "relation": "contradicts", "polarity": "negative"}
```

| campo | regola |
|---|---|
| `src`, `dst` | entrambi risolvono a `_id` di `corpus.jsonl`; `src != dst`. |
| `relation` | enum §1.4. |
| `polarity` | enum §1.4, **coerente** con `relation` (la coppia deve combaciare con la tabella). |

Per `supersedes`: `src` = nuovo/vincolante, `dst` = superato (vedi §1.4).

---

## 5. Layer 3 e Layer 2 — annotazioni a livello query

### 5.1 `annotations/stance.tsv` — gold stance (Layer 3)

TSV con header. Una riga per query annotata per stance. Non tutte le query hanno una
lettura di stance naturale (sui corpora investigativi è un sottoinsieme — Layer 3
*partial*): annota solo quelle che ce l'hanno.

```
query-id	gold_stance
q06	neutral
q19	supports
q04	contradicts
```

| colonna | regola |
|---|---|
| `query-id` | risolve a `queries.jsonl`. |
| `gold_stance` | enum §1.2 (`supports`/`contradicts`/`neutral`). |

> Promemoria semantico per non sbagliare il `neutral`: usa `neutral` quando il corpus
> **registra la domanda come aperta / non risolta** (es. "Legal non ha ancora approvato",
> "open question"), *non* quando semplicemente non ci sono documenti — quella è una query
> non annotabile per stance, lasciala fuori.

### 5.2 `annotations/traps.tsv` — trap doc (Layer 2, trap rejection)

I trap sono doc on-topic che **sembrano** rilevanti ma sono distrattori: vanno a `0` nei
qrels e sono elencati qui per la metrica `TrapInTop5`.

```
query-id	corpus-id
q05	06-market-context/competitor-benchmark
```

| colonna | regola |
|---|---|
| `query-id` | risolve a `queries.jsonl`. |
| `corpus-id` | risolve a `corpus.jsonl`; **deve** avere score `0` in `qrels/test.tsv` (e negli slice in cui esiste) — coerenza richiesta dal validatore. |

---

## 6. Matrice di copertura — quali layer per quale corpus (paper Tab. 3)

`✓` = annotare · `partial` = solo sottoinsieme di query · `—` = non applicabile (non creare i file).

| corpus | L1 `qrels/test.tsv` | L2 `edges.jsonl`+`traps.tsv` | L3 `stance.tsv` | L4 `doc_state.jsonl`+`test_t*.tsv` |
|---|:---:|:---:|:---:|:---:|
| `org-consulting-clearpath` | ✓ (esiste) | ✓ | ✓ | ✓ (3 cutoff) |
| `org-iot-fireglass` | ✓ (esiste) | ✓ | ✓ | ✓ (3 cutoff) |
| `org-vc-vertexminds` | ✓ (esiste) | ✓ | ✓ | ✓ (3 cutoff) |
| `inv-mystery-redhood` | ✓ (esiste) | ✓ | partial | — |
| `inv-ashford-mystery` | ✓ (esiste) | ✓ | partial | — |

I corpora investigativi sono *single-time puzzles*: **niente** `query_time`,
`temporal_intent`, `doc_state.jsonl`, né `test_t*.tsv`.

---

## 7. Integrità referenziale e checklist di validazione

Tutto ciò che segue è controllato da `docs/validate_annotations.py`. Un `ERROR` = file da
correggere prima di considerare il lavoro finito.

### Regole formali (ERROR se violate)

1. **JSONL**: ogni riga è un oggetto JSON valido; chiavi obbligatorie presenti; nessuna
   chiave fuori schema.
2. **TSV**: header esatto; separatore TAB (non spazi); `score` ∈ {0,1,2,3} intero.
3. **Enum chiusi**: `lifecycle_state`, `stance`, `temporal_intent`, `relation`, `polarity`
   solo dai valori §1.
4. **Risoluzione ID**: ogni `corpus-id`/`_id`/`src`/`dst` esiste in `corpus.jsonl`; ogni
   `query-id` esiste in `queries.jsonl`.
5. **Coppia relation/polarity** coerente con la tabella §1.4.
6. **`supersedes`** implica un arco con `src` non obsoleto e `dst` che diventa
   `superseded` in `doc_state.jsonl` allo stesso o successivo cutoff.
7. **Trap**: ogni riga di `traps.tsv` ha lo stesso `(query-id, corpus-id)` a **score 0**
   in `qrels/test.tsv`.
8. **Cutoff**: le chiavi di `lifecycle_by_cutoff` sono **esattamente** i 3 cutoff del
   corpus (§2); i nomi `test_t<TAG>.tsv` usano quei TAG.
9. **Causalità temporale**: nessun doc con `metadata.created > T` compare in
   `test_t<T>.tsv`.
10. **query_time/temporal_intent**: presenti e coerenti su tutte e sole le query
    temporali; `query_time` ∈ {date valide}; `temporal_intent` ∈ enum.

### Regole di buon senso (WARN, da rivedere)

- Monotonia lifecycle (no resurrezione da obsolete).
- Ogni query `current_state` ha almeno un gold-current (score 3) nello slice del suo
  `query_time`.
- Ogni doc gold negli slice è presente in `doc_state.jsonl`.
- `valid_until` ≥ ultimo cutoff in cui il doc è ancora non-obsoleto.

### κ inter-annotatore (paper §5.2, target di qualità)

Se più persone annotano, riportate Cohen's κ:
`F-CORP-Q1` → κ(`lifecycle_state`) ≥ **0.70**; `F-CORP-Q2` → κ(`supersedes`) ≥ **0.75**.
Sotto soglia: ri-conciliare le annotazioni prima di chiudere il corpus.

---

## 8. Esempi worked (end-to-end)

### 8.1 Decisione che evolve → `current_state` (ClearPath, target onboarding)

`queries.jsonl`:
```json
{"_id": "q31", "text": "What onboarding-time target is currently binding for the ClearPath engagement?", "metadata": {"tests": "onboarding_target_binding_now", "difficulty": "medium", "query_time": "2025-12-15", "temporal_intent": "current_state"}}
```
`annotations/doc_state.jsonl`:
```json
{"_id": "01-scope/project-brief", "valid_from": "2025-09-10", "valid_until": "2025-11-01", "lifecycle_by_cutoff": {"2025-09-30": "active", "2025-11-01": "superseded", "2025-12-15": "superseded"}}
{"_id": "07-documents/report-final", "valid_from": "2025-12-10", "valid_until": null, "lifecycle_by_cutoff": {"2025-09-30": "provisional", "2025-11-01": "provisional", "2025-12-15": "canonical"}}
```
`qrels/test_t2025-12-15.tsv` (estratto): `report-final` è il binding ora (3), il vecchio
brief è storico (1).
```
query-id	corpus-id	score
q31	07-documents/report-final	3
q31	01-scope/project-brief	1
```
`annotations/edges.jsonl`:
```json
{"src": "07-documents/report-final", "dst": "01-scope/project-brief", "relation": "supersedes", "polarity": "directional"}
```

### 8.2 Ignoranza registrata → `neutral` (stance)

Query "Is the 18% junior-consultant turnover rate a verified figure?" → il corpus la
registra come **non verificata** ⇒ stance gold `neutral`.
`annotations/stance.tsv`:
```
query-id	gold_stance
q04	neutral
```

### 8.3 Stable knowledge vs freshness (FOR)

Query `stable_knowledge` con `query_time = 2025-12-15`: un fatto canonico vecchio
(`valid_from: 2025-09`) deve battere un doc recente provvisorio.
```json
{"_id": "01-scope/requirements", "valid_from": "2025-09-12", "valid_until": null, "lifecycle_by_cutoff": {"2025-09-30": "canonical", "2025-11-01": "canonical", "2025-12-15": "canonical"}}
{"_id": "03-internal-comms/email/email-internal-008", "valid_from": "2025-12-12", "valid_until": null, "lifecycle_by_cutoff": {"2025-09-30": "provisional", "2025-11-01": "provisional", "2025-12-15": "provisional"}}
```
Nel `test_t2025-12-15.tsv` il doc canonico vecchio è il gold (3), il recente provvisorio è
distrattore (0 o 1).

---

## 9. Fuori scope di questa guida (NON annotare)

- **9 tipi epistemici dei KO** e pesi `Kt`: sono prodotti dall'estrazione di `oida-core`
  in ingest, **non** sono gold da scrivere a mano. Non aggiungerli ai file.
- **SciFact (Esperimento 1)**: è un dataset BEIR esterno, non uno di questi corpora; la sua
  stance è già etichettata (SUPPORT/CONTRADICT/NEI → `supports`/`contradicts`/`neutral`).
  Non ricrearlo qui.
- **Risultati/metriche**: le tabelle 6–17 del paper si **calcolano** dal valutatore, non si
  annotano. Tu produci solo il gold.
