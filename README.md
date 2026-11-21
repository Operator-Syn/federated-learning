# Inclusion-Aware Client Selection for Federated Learning under Intermittent Connectivity: Medicine Surge Classification at Iligan City Barangay Health Centers

**A Simulation Study Calibrated to Iligan City Barangay Health Centers**

CSC198 · Group Beira, Jagonia, Ybanez

---

Federated learning lets health facilities train one shared model without their records ever leaving the clinic. Each site trains on its own data, and only the resulting model weights travel. The dividend is architectural rather than incidental: fewer copies of patient data exist, and facility-level separation survives contact with the design. The promise is well established. What it costs in a place like Iligan is not.

The one part of the argument that is easier to operate than to describe. Four phases, one round: the server shares the model, each station trains on its own records, only weights come back, and the aggregator averages them into the next version.

[![One federated round: the server shares v1 with three health stations, each trains on its own records, only the updates travel back, and the aggregator averages them, with the matching step highlighted below](assets/round-loop.gif)](https://operator-syn.github.io/federated-learning/figures/round-loop/)

*Three health stations keep their own records; only model updates cross to the aggregator. Click to step through one round.*

Client selection under intermittent availability is already an active line of work. Adaptive sampling reacts to which clients happen to be reachable, resource-aware selection prefers the ones that finish a round soonest, and fair-sampling strategies raise the probability of clients that keep getting passed over. What that literature cannot tell the Iligan City health office is what any of these policies would cost *here*, because the parameters that decide the answer are local. The city has forty-four barangays; this study does not attempt all of them, and starts with three facility nodes. Most facilities hold only a few hundred records, so a station that has never recorded a surge has almost nothing to learn from. Links are uneven across the city and change with weather, staffing, and power; a round cannot complete until its slowest selected facility answers, so whichever station is having a bad week sets the pace for everyone. And the records themselves live in stock cards and iClinicSys, not in a research warehouse.

This study therefore does not propose a new selection algorithm. It takes the policy families that already exist, instantiates them under Iligan's constraints, and measures the two things the general literature does not report at this scale: how long each takes to reach a usable model, and what holding every facility above a participation floor costs in time. The output is a starting protocol the city health office could adopt and extend, with its price stated rather than implied — together with a calibrated parameter set that outlives the study, so the comparison can be re-run as more facilities come online.

---

## Working in this repository

```bash
uv sync        # environment from uv.lock
make help      # every target, with what it does
make check     # lint, gate self-tests, spec-name drift, spec audit, notebook storage — what a commit must pass
make spec      # build the technical specification PDF
```

| path | what lives there |
|---|---|
| `docs/` | the source library, its index, and the generated bibliography |
| `docs/spec/` | **technical specification** — entities, selection policies, metric formulas, parameters, conformance. Not the paper: the paper cites its section numbers |
| `src/fl_thesis/` | reusable logic behind the notebooks, organised by concern: `workspace` (paths), `runtime` (environment), `data` (generators), `viz` (figures). `federation/` and `evaluation/` arrive with the simulation |
| `notebooks/` | workspace; cells hold configuration and calls only, and outputs are stripped before commit |
| `scripts/` | repository tooling, documented in `scripts/README.md` |

Prerequisites are `uv` and, for the specification, a LaTeX distribution with `latexmk`. Without
`latexmk`, `make spec` cannot run and `make check` skips the PDF audit with a printed notice.

