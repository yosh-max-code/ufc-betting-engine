import pandas as pd
from sklearn.preprocessing import StandardScaler

def create_fight_differentials(df: pd.DataFrame) -> pd.DataFrame:

    # Initialize our empty list for base columns shared fight data
    base_columns = []
    # Loop through all columns to find the shared names like date etc
    for col in df.columns:
        if not col.startswith('R_') and not col.startswith('B_'):
            base_columns.append(col)
    #print(base_columns)

    #STATS for each fighter side
    red_cols = []
    blue_cols = []

    #fighter specific stats and creating a single column for both 
    clean_columns = []

    # Loop through all columns again to categorize them
    for col in df.columns:
        if col.startswith('R_'):
            red_cols.append(col)
            clean_name = col.replace('R_', '')
            clean_columns.append(clean_name)

        elif col.startswith('B_'):
            blue_cols.append(col)

    # Print the length of the lists to verify i caught them all
    #print(f"Found {len(red_cols)} Red columns and {len(blue_cols)} Blue columns.")
    #print(clean_columns)

    #dataframe for just r_columns sliced from df
    all_red_cols = base_columns + red_cols
    red_df = df[all_red_cols]
    #print(red_df.shape)

    all_blue_cols = base_columns + blue_cols
    blue_df = df[all_blue_cols]
    #print(blue_df.shape)

    #final columns layout
    master_headers = base_columns + clean_columns

    red_df.columns = master_headers
    blue_df.columns = master_headers

    #print("Red headers:", red_df.columns[:8])
    #print("Blue headers:", blue_df.columns[:8])

    math_columns = clean_columns
    red_math_df = red_df[math_columns].select_dtypes(include=['number'])
    blue_math_df = blue_df[math_columns].select_dtypes(include=['number'])
    #including only numbered column values for mathematical differentiation

    differential_df = blue_math_df - red_math_df
    #print("Diff columns:", differential_df.columns[:5])
    #print("Diff shape:", differential_df.shape)

    differential_df.columns = [f"dif_{col}" for col in differential_df.columns]

    final_df = df.join(differential_df)

    return final_df

if __name__ == "__main__":
    raw_data = pd.read_csv("ufc-master.csv")
    final_features = create_fight_differentials(raw_data)

    #fit_transform() is ONLY used on your Training Data (it learns the mean/std and transforms it).
    #transform() is used on your Test Data or Live Data 
    """
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(final_features[['dif_odds', 'dif_current_win_streak']])
    print(final_features[:5])
    print(scaled_features[:5])
    """

    #test_rank = final_features['dif_Featherweight_rank'].fillna(16)
    #print(test_rank.head(10))

    final_features = final_features.sort_values(by='date', ascending=True).reset_index(drop=True)
    print("First row date:", final_features['date'].iloc[0])
    print("Last row date:", final_features['date'].iloc[-1])
    print("First 5 index numbers:", final_features.index[:5].tolist())




    
