
#quick matchup lookups without retraining - run python -m src.predict once first to save the model
#Run with:  python -m src.predict_matchup
#then just type in the fighter names and odds when it asks

from src.model import FighterPredictor
from src.predict import load_training_data, explain_matchup, print_result


def predict_matchup(fighter_a, fighter_b, odds_a, odds_b):
    #loads the saved model instead of retraining from scratch
    predictor = FighterPredictor.load_model("data/trained_predictor.joblib")

    #still needed since build_matchup_row looks up fighter snapshots from it
    df = load_training_data()

    result = explain_matchup(fighter_a, fighter_b, df, predictor, odds_a, odds_b)
    print_result(result)


if __name__ == "__main__":
    #strip() removes any accidental leading/trailing spaces from typing
    fighter_a = input("Fighter A name: ").strip()
    fighter_b = input("Fighter B name: ").strip()

    #odds are optional, leave blank to skip the EV calculation
    odds_a_text = input("Fighter A odds (leave blank to skip): ").strip()
    odds_b_text = input("Fighter B odds (leave blank to skip): ").strip()

    if odds_a_text == "" or odds_b_text == "":
        odds_a = None
        odds_b = None
    else:
        odds_a = float(odds_a_text)
        odds_b = float(odds_b_text)

    predict_matchup(fighter_a, fighter_b, odds_a, odds_b)
