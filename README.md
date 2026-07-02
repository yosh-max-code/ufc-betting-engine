# UFC Betting Engine

Predicts the winner of a UFC matchup between two fighters using their historical
stats, calibrated to output a real win probability rather than just a class label,
with SHAP explainability and a market-odds EV comparison.

## What it does

1. **Loads** historical UFC fight data (`data/ufc-master.csv`, ~7,200 fights).
2. **Trains** an XGBoost classifier inside a scikit-learn `Pipeline`
   (`StandardScaler` + `OneHotEncoder` -> `XGBClassifier`), then **calibrates**
   its probabilities with `CalibratedClassifierCV` (Platt/sigmoid scaling) so a
   0.70 output actually means ~70% historically, not just "leans yes."
3. Evaluates on a **chronological** train/test split (80/20 by date, not
   random) so the reported metrics reflect genuine forward-looking performance
   rather than leaking future fights into training.
4. Given two fighter names, builds a live matchup row from each fighter's most
   recent stat-line and returns a calibrated win probability.
5. Explains *why* via **SHAP** — which stat differentials (takedown average,
   win streak, age, etc.) pushed the prediction toward one fighter.
6. If market odds are supplied, converts them to implied probability and
   compares against the model's probability to flag betting **EV**
   (positive EV = model thinks the market is underpricing that fighter).

## Results

On a chronological 80/20 train/test split:

- **Log-loss:** 0.628
- **AUC:** 0.711

(An in-sample eval on the full training set gives an optimistic ~0.54 log-loss —
the 0.628/0.711 numbers above are the honest, held-out figures.)

## Project structure

```
src/
  fighter.py    Fighter/Champion OOP classes (from/to dict, validation, title eligibility)
  model.py      FighterPredictor: pipeline, calibration, eval metrics, SHAP
  features.py   Fighter snapshot lookup + matchup row builder (live inference)
  predict.py    Entry point: trains the model and runs a sample matchup end to end
tests/
  test_fighter.py   Unit tests for Fighter
  test_predict.py   Unit + integration tests for the feature/prediction pipeline
data/
  ufc-master.csv    Historical fight data
```

## Running it

```bash
pip install -r requirements.txt
python -m src.predict
```

This trains the model, prints held-out log-loss/AUC, then runs a sample
matchup prediction with SHAP breakdown and EV vs sample odds.

Run the tests with:

```bash
pytest tests/
```

## Design notes

- **Why differentials, not raw stats?** The model is trained on
  `blue_stat - red_stat` for every numeric feature (reach, age, win streak,
  etc.) rather than each fighter's raw numbers. This halves the feature space
  and makes the model side-agnostic — it's learning "what stat gaps predict a
  win," not memorizing which absolute stat values tend to win, which
  generalizes better to new fighters.
- **Why calibrate separately from the base model?** `XGBClassifier.predict_proba`
  outputs are not guaranteed to be well-calibrated probabilities out of the box
  — they're good for ranking, less reliable as literal probabilities.
  `CalibratedClassifierCV` fixes that, which matters a lot for the EV
  calculation: EV is only meaningful if the model's probability is honest.
- **Why a chronological split instead of random k-fold?** Fights aren't
  independent of time — fighter form, weight-class trends, and roster
  composition all shift over the years. A random split would let the model
  "see the future" during training and overstate its real performance.

## Known limitations / future work

- **No MLflow model registry** — the trained model isn't versioned or
  persisted; each run retrains from scratch. Fine for a demo/portfolio project,
  not production-ready.
- **No Kelly Criterion bankroll backtest** — EV is computed per-matchup but
  there's no historical simulation of bankroll growth under a staking
  strategy.
- **No live odds feed** — odds are passed in manually per prediction rather
  than pulled from a sportsbook API.
- **PySpark version** (`spark_features.py`, not included in this repo) was
  prototyped on Databricks for the same differential feature engineering,
  proving the pipeline works at Spark scale. Cut from this repo since the
  dataset (~7K rows) doesn't actually need distributed processing — kept here
  as a note that the pattern was validated, not because it was needed.
