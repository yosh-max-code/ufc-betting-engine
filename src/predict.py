
#Run with:  python -m src.predict

import pandas as pd

from src.model import FighterPredictor
from src.features import build_matchup_row, DIFF_COL_MAP


MODEL_FEATURE_COLS = list(DIFF_COL_MAP.keys()) + [
    "dif_odds",
    "weight_class",
    "R_Stance",
    "B_Stance",
]


def load_training_data(csv_path="data/ufc-master.csv"):
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])

    #drop draws/no-contests, only want a win/loss to predict
    df = df[df["Winner"].isin(["Red", "Blue"])].copy()

    #target column, 1 if Blue won, 0 if Red won
    df["y"] = (df["Winner"] == "Blue").astype(int)

    #CSV already has stat diffs but no odds diff, so build one the same way
    df["dif_odds"] = df["B_odds"] - df["R_odds"]

    df = df.sort_values(by="date", ascending=True)
    df = df.reset_index(drop=True)
    return df


def train_test_split_by_date(df, train_frac=0.8):
    #chronological split, don't want future fights leaking into training
    cutoff = int(len(df) * train_frac)
    train_df = df.iloc[:cutoff]
    test_df = df.iloc[cutoff:]
    return train_df, test_df


def train_predictor(train_df):
    x_train = train_df[MODEL_FEATURE_COLS]
    y_train = train_df["y"]

    predictor = FighterPredictor()
    predictor.fit(x_train, y_train)
    return predictor


def american_odds_to_prob(odds):
    #positive odds = underdog, negative odds = favorite, different formula each way
    if odds > 0:
        prob = 100 / (odds + 100)
    else:
        prob = -odds / (-odds + 100)
    return prob


def explain_matchup(fighter_a, fighter_b, df, predictor, odds_a=None, odds_b=None):
    matchup_df = build_matchup_row(fighter_a, fighter_b, df)

    #model outputs P(fighter_b wins), so fighter_a's chance is just 1 minus that
    prob_b_wins = predictor.predict_proba_calibrated(matchup_df)[:, 1][0]
    prob_a_wins = 1 - prob_b_wins

    #default winner to fighter_a, only swap it if fighter_b actually scored higher
    winner = fighter_a
    winner_prob = prob_a_wins
    if prob_b_wins > prob_a_wins:
        winner = fighter_b
        winner_prob = prob_b_wins

    shap_values = predictor.get_shap_values(matchup_df)

    result = {}
    result["fighter_a"] = fighter_a
    result["fighter_b"] = fighter_b
    result["predicted_winner"] = winner
    result["win_probability"] = round(float(winner_prob), 4)
    result["prob_a"] = round(float(prob_a_wins), 4)
    result["prob_b"] = round(float(prob_b_wins), 4)
    result["shap_values"] = shap_values
    result["shap_feature_names"] = MODEL_FEATURE_COLS

    #only do the EV maths if odds were given for both fighters
    if odds_a is not None and odds_b is not None:
        implied_a = american_odds_to_prob(odds_a)
        implied_b = american_odds_to_prob(odds_b)
        #EV = model's probability minus what the market odds are implying
        result["ev_a"] = round(prob_a_wins - implied_a, 4)
        result["ev_b"] = round(prob_b_wins - implied_b, 4)

    return result


def print_result(result):
    print("")
    print(result["fighter_a"] + " vs " + result["fighter_b"])
    print("Predicted winner: " + result["predicted_winner"])
    print("Win probability: " + str(result["win_probability"]))
    print("P(" + result["fighter_a"] + " wins) = " + str(result["prob_a"]))
    print("P(" + result["fighter_b"] + " wins) = " + str(result["prob_b"]))

    #EV keys only show up in the dict if odds were actually passed in
    if "ev_a" in result:
        print("EV for " + result["fighter_a"] + ": " + str(result["ev_a"]))
        print("EV for " + result["fighter_b"] + ": " + str(result["ev_b"]))

        if result["ev_a"] > 0:
            print("-> Model sees value on " + result["fighter_a"])
        if result["ev_b"] > 0:
            print("-> Model sees value on " + result["fighter_b"])

    print("All SHAP feature contributions:")

    #loop through every feature and print it, no sorting needed since we show them all
    names = result["shap_feature_names"]
    values = result["shap_values"][0]

    for i in range(len(names)):
        name = names[i]
        value = values[i]

        if value > 0:
            direction = "favors " + result["fighter_b"]
        else:
            direction = "favors " + result["fighter_a"]

        print("  " + name + "  " + str(round(value, 3)) + "  (" + direction + ")")


if __name__ == "__main__":
    df = load_training_data()
    train_df, test_df = train_test_split_by_date(df)

    predictor = train_predictor(train_df)

    x_test = test_df[MODEL_FEATURE_COLS]
    y_test = test_df["y"]
    print("Held-out log-loss: " + str(predictor.evaluate_logloss(x_test, y_test)))
    print("Held-out AUC: " + str(predictor.evaluate_auc(x_test, y_test)))

    #trains again on the full dataset so the "live" predictor has the most recent fighter data
    full_predictor = train_predictor(df)

    full_predictor.save_model("data/trained_predictor.joblib")
    print("Saved trained model to data/trained_predictor.joblib")

    result = explain_matchup("Conor McGregor", "Max Holloway", df, full_predictor, 180, -240)
    print_result(result)
