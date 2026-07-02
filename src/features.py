
import pandas as pd

#maps model column name to the raw stat name once R_/B_ prefix is stripped off
DIFF_COL_MAP = {
    "ko_dif": "win_by_KO/TKO",
    "sub_dif": "win_by_Submission",
    "height_dif": "Height_cms",
    "reach_dif": "Reach_cms",
    "age_dif": "age",
    "sig_str_dif": "avg_SIG_STR_landed",
    "avg_sub_att_dif": "avg_SUB_ATT",
    "avg_td_dif": "avg_TD_landed",
    "lose_streak_dif": "current_lose_streak",
    "win_streak_dif": "current_win_streak",
}


#gets the most recent stat line for a fighter, checks both Red and Blue side
def get_fighter_snapshot(df: pd.DataFrame, fighter: str) -> pd.Series:
    #lowercase both sides so capitalization typos still match
    fighter_lower = fighter.lower()
    mask = (df["R_fighter"].str.lower() == fighter_lower) | (df["B_fighter"].str.lower() == fighter_lower)
    matched_rows = df[mask]

    if matched_rows.empty:
        raise ValueError(f"No fights found for fighter: {fighter!r}")

    #sort ascending by date, last row is the most recent fight
    latest_row = matched_rows.sort_values(by="date", ascending=True).iloc[-1]

    #figure out which side (Red or Blue) fighter was on for that fight
    if latest_row["R_fighter"].lower() == fighter_lower:
        prefix = "R_"
    else:
        prefix = "B_"

    #only keep the columns for that side
    fighter_cols = []
    for col in latest_row.index:
        if col.startswith(prefix):
            fighter_cols.append(col)

    snapshot = latest_row[fighter_cols]

    #strip the prefix off so column names come out clean
    new_index = []
    for col in fighter_cols:
        new_index.append(col.replace(prefix, "", 1))
    snapshot.index = new_index

    return snapshot


#builds one row of stat differentials (fighter_b - fighter_a) in the schema the model expects
def build_matchup_row(fighter_a: str, fighter_b: str, df: pd.DataFrame) -> pd.DataFrame:
    snap_a = get_fighter_snapshot(df, fighter_a)
    snap_b = get_fighter_snapshot(df, fighter_b)

    row = {}
    for model_col, base_col in DIFF_COL_MAP.items():
        value_a = snap_a.get(base_col, 0)
        value_b = snap_b.get(base_col, 0)
        row[model_col] = value_b - value_a
        #Blue minus Red, matches the convention the CSV already uses for its own diffs

    row["dif_odds"] = snap_b.get("odds", 0) - snap_a.get("odds", 0)
    row["weight_class"] = df["weight_class"].mode()[0] #placeholder since no per-fighter weight class is stored
    row["R_Stance"] = snap_a.get("Stance", "Orthodox")
    row["B_Stance"] = snap_b.get("Stance", "Orthodox")

    return pd.DataFrame([row]) #wrapped in a list so pandas makes a row, not a Series


if __name__ == "__main__":
    raw_data = pd.read_csv("data/ufc-master.csv")
    raw_data["date"] = pd.to_datetime(raw_data["date"])
    raw_data = raw_data.sort_values(by="date", ascending=True).reset_index(drop=True)

    print("First row date:", raw_data["date"].iloc[0])
    print("Last row date:", raw_data["date"].iloc[-1])
    print("Rows:", len(raw_data))
