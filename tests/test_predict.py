"""
Integration-level tests for the feature building and prediction pipeline.
Uses a small synthetic DataFrame rather than the full CSV so tests run fast
and don't depend on real fighter names.
"""

import pandas as pd
import pytest

from src.features import get_fighter_snapshot, build_matchup_row
from src.predict import (
    load_training_data,
    train_test_split_by_date,
    train_predictor,
    american_odds_to_prob,
    explain_matchup,
    MODEL_FEATURE_COLS,
)


@pytest.fixture
def toy_df():
    """Two fighters, two fights each, enough to build a snapshot from."""
    rows = [
        {
            "R_fighter": "Fighter A", "B_fighter": "Fighter B",
            "date": "2024-01-01", "Winner": "Red",
            "R_odds": -150, "B_odds": 130,
            "R_current_lose_streak": 0, "B_current_lose_streak": 1,
            "R_current_win_streak": 3, "B_current_win_streak": 0,
            "R_avg_SIG_STR_landed": 4.5, "B_avg_SIG_STR_landed": 3.2,
            "R_avg_SUB_ATT": 0.5, "B_avg_SUB_ATT": 0.2,
            "R_avg_TD_landed": 1.2, "B_avg_TD_landed": 0.8,
            "R_win_by_KO/TKO": 3, "B_win_by_KO/TKO": 1,
            "R_win_by_Submission": 1, "B_win_by_Submission": 2,
            "R_Height_cms": 180, "B_Height_cms": 175,
            "R_Reach_cms": 185, "B_Reach_cms": 178,
            "R_age": 29, "B_age": 33,
            "R_Stance": "Orthodox", "B_Stance": "Southpaw",
            "weight_class": "Lightweight",
        },
        {
            "R_fighter": "Fighter C", "B_fighter": "Fighter A",
            "date": "2024-06-01", "Winner": "Blue",
            "R_odds": 110, "B_odds": -130,
            "R_current_lose_streak": 1, "B_current_lose_streak": 0,
            "R_current_win_streak": 0, "B_current_win_streak": 4,
            "R_avg_SIG_STR_landed": 3.9, "B_avg_SIG_STR_landed": 4.8,
            "R_avg_SUB_ATT": 0.3, "B_avg_SUB_ATT": 0.6,
            "R_avg_TD_landed": 0.9, "B_avg_TD_landed": 1.4,
            "R_win_by_KO/TKO": 2, "B_win_by_KO/TKO": 4,
            "R_win_by_Submission": 0, "B_win_by_Submission": 1,
            "R_Height_cms": 178, "B_Height_cms": 180,
            "R_Reach_cms": 180, "B_Reach_cms": 185,
            "R_age": 31, "B_age": 29,
            "R_Stance": "Orthodox", "B_Stance": "Orthodox",
            "weight_class": "Lightweight",
        },
    ]
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def test_get_fighter_snapshot_picks_latest_fight(toy_df):
    snap = get_fighter_snapshot(toy_df, "Fighter A")
    # Fighter A's most recent fight (2024-06-01) was on the Blue side
    assert snap["fighter"] == "Fighter A"
    assert snap["current_win_streak"] == 4


def test_get_fighter_snapshot_unknown_fighter_raises(toy_df):
    with pytest.raises(ValueError):
        get_fighter_snapshot(toy_df, "Nobody Real")


def test_build_matchup_row_has_model_schema(toy_df):
    matchup = build_matchup_row("Fighter A", "Fighter C", toy_df)
    assert list(matchup.columns) == [
        "ko_dif", "sub_dif", "height_dif", "reach_dif", "age_dif",
        "sig_str_dif", "avg_sub_att_dif", "avg_td_dif",
        "lose_streak_dif", "win_streak_dif",
        "dif_odds", "weight_class", "R_Stance", "B_Stance",
    ]
    assert len(matchup) == 1


def test_american_odds_to_prob_favorite_and_underdog():
    # Heavy favorite (-150) should imply a higher win probability than an even-money bet
    assert american_odds_to_prob(-150) > 0.5
    # Underdog (+130) should imply a lower win probability than an even-money bet
    assert american_odds_to_prob(130) < 0.5


def test_full_pipeline_trains_and_predicts():
    """Smoke test: real CSV, real training, real matchup prediction."""
    df = load_training_data("data/ufc-master.csv")
    train_df, test_df = train_test_split_by_date(df)

    predictor = train_predictor(train_df)

    x_test = test_df[MODEL_FEATURE_COLS]
    y_test = test_df["y"]

    auc = predictor.evaluate_auc(x_test, y_test)
    assert 0.5 < auc < 1.0  # better than random, not suspiciously perfect

    result = explain_matchup("Joe Pyfer", "Israel Adesanya", df, predictor)
    assert result["predicted_winner"] in ("Joe Pyfer", "Israel Adesanya")
    assert 0 <= result["win_probability"] <= 1
    assert abs(result["prob_a"] + result["prob_b"] - 1.0) < 1e-6
