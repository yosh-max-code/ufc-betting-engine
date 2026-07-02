import joblib
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from xgboost import XGBClassifier

from sklearn.metrics import log_loss
from sklearn.metrics import roc_auc_score
from sklearn.calibration import CalibratedClassifierCV
import pandas as pd

from sklearn.calibration import calibration_curve
from typing import Tuple
import matplotlib.pyplot as plt


import shap


class FighterPredictor:
    def __init__(self, model=XGBClassifier()) -> None:



        self.preprocessor = ColumnTransformer(transformers=[("scaler", StandardScaler(), ['ko_dif', 'sub_dif', 'height_dif', 'reach_dif',
                                                                                        'age_dif', 'sig_str_dif', 'avg_sub_att_dif', 'avg_td_dif',
                                                                                        'lose_streak_dif', 'win_streak_dif', 'dif_odds']),

                                                            ("encoder", OneHotEncoder(handle_unknown='ignore'), ['weight_class', 'R_Stance', 'B_Stance'])])
        #ENCODE non numerical catergories into numbers i.e stance, weightclass

        self.pipeline = Pipeline(steps=[("preprocessor", self.preprocessor),
                                        ("classifier", model)])

        self.calibrated_pipeline = CalibratedClassifierCV(estimator=self.pipeline, method="sigmoid", cv=2)
        #cv=2 means this actually trains 2 separate copies of the pipeline (one per fold)
        #and averages their answers together for a more honest probability. that's why
        #get_shap_values below has to loop over multiple fold copies too, instead of
        #just explaining one model - it's explaining the same averaged prediction this makes.
        #bump this number up later and get_shap_values just loops over more folds, no other changes needed.


    #StandardScaler rescales every feature so they're all on the same playing field. No stat bullies the others.
    #LogisitcRegression a classification model. You feed it fighter stats and it outputs a probability between 0 and 1


    def fit(self, x, y):
        self.pipeline.fit(x, y)
        self.calibrated_pipeline.fit(x, y)
        #showing model histrorical data x = stats, y = winner

    def predict_proba(self, x):
        return self.pipeline.predict_proba(x)
        #returns a win probability for a new matchup

    def predict_proba_calibrated(self, x):
        return self.calibrated_pipeline.predict_proba(x)
        #returns a win probability for a new matchup calibrated using platt scaling
        #platt scaling [sigmoid] vs isotonic regression

    def evaluate_logloss(self, x: pd.DataFrame, y_true: pd.Series) -> float:
        y_pred_proba = self.predict_proba_calibrated(x)
        return log_loss(y_true, y_pred_proba)
        #LOG LOSS CALCULATION FOR CONFIDENCE

    def evaluate_auc(self, x: pd.DataFrame, y_true: pd.Series) -> float:
        y_pred_proba = self.predict_proba_calibrated(x)[:, 1]
        return roc_auc_score(y_true, y_pred_proba)
        #ROC AUC CALC FOR RANKINGS


    def get_calibration_curve(self, x:pd.DataFrame, y_true: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        y_pred_proba = self.predict_proba_calibrated(x)
        return calibration_curve(y_true, y_pred_proba)
        #CALIBRATION CURVE USING TWO ARRAYS ONE ON REAL Y AND ONE ON PREDICTED Y

    def plot_calibration_curve(self, x:pd.DataFrame, y_true:pd.Series) -> None:
        y_pred_proba = self.predict_proba_calibrated(x)[:, 1]
        actual_probs, predicted_probs = calibration_curve(y_true, y_pred_proba)
        plt.plot(predicted_probs, actual_probs, marker="o")
        plt.plot([0, 1], [0, 1], linestyle="--") #REFERENCE LINE CALIBRATION
        plt.xlabel("predicted probability")
        plt.ylabel("actual probability")
        plt.show()

    def get_shap_values(self, fighter_df:pd.DataFrame) -> np.ndarray:
        #predict_proba_calibrated doesn't use self.pipeline on its own, it actually
        #uses a couple of fitted copies of it (one per CV fold) and averages their
        #results together. so explaining that exact prediction means running SHAP
        #on each fold's copy separately, then averaging those explanations too.

        #the first 11 transformed columns are always the numeric stat diffs, same
        #order every fold since the scaler never adds or removes columns. everything
        #after that is one-hot encoded weight_class/stance, and different folds can
        #see different categories during training, so those column counts don't
        #line up between folds. easiest fix: average just the 11 numeric columns
        #across folds, and use the first fold's numbers for the rest.

        numeric_col_count = 11

        total_numeric_shap = None
        first_fold_full_shap = None
        first_fold_col_names = None

        for calibrated_classifier in self.calibrated_pipeline.calibrated_classifiers_:
            fold_pipeline = calibrated_classifier.estimator
            fold_classifier = fold_pipeline.named_steps["classifier"]
            fold_preprocessor = fold_pipeline.named_steps["preprocessor"]

            explainer = shap.TreeExplainer(fold_classifier)
            transformed_data = fold_preprocessor.transform(fighter_df)
            fold_shap_values = explainer.shap_values(transformed_data)

            if first_fold_full_shap is None:
                first_fold_full_shap = fold_shap_values
                first_fold_col_names = fold_preprocessor.get_feature_names_out()

            numeric_part = fold_shap_values[:, 0:numeric_col_count]
            if total_numeric_shap is None:
                total_numeric_shap = numeric_part
            else:
                total_numeric_shap = total_numeric_shap + numeric_part

        #average the numeric part across however many folds there were
        num_folds = len(self.calibrated_pipeline.calibrated_classifiers_)
        average_numeric_shap = total_numeric_shap / num_folds

        #collapse everything down to one value per MODEL_FEATURE_COLS entry.
        #the 11 numeric diffs map straight across, already averaged above.
        #weight_class/R_Stance/B_Stance are spread across several one-hot columns
        #each, so add up all the columns belonging to each one into a single value.
        collapsed_values = []
        for i in range(numeric_col_count):
            collapsed_values.append(average_numeric_shap[0][i])

        #columns from index 11 onward belong to weight_class, R_Stance, B_Stance
        #in that order, taken from the first fold's SHAP values
        remaining_names = first_fold_col_names[numeric_col_count:]
        remaining_values = first_fold_full_shap[0][numeric_col_count:]

        weight_class_total = 0
        r_stance_total = 0
        b_stance_total = 0
        for i in range(len(remaining_names)):
            col_name = remaining_names[i]
            if "weight_class" in col_name:
                weight_class_total = weight_class_total + remaining_values[i]
            elif "R_Stance" in col_name:
                r_stance_total = r_stance_total + remaining_values[i]
            elif "B_Stance" in col_name:
                b_stance_total = b_stance_total + remaining_values[i]

        collapsed_values.append(weight_class_total)
        collapsed_values.append(r_stance_total)
        collapsed_values.append(b_stance_total)

        #wrapped in a list so the shape matches what the rest of the code expects
        return np.array([collapsed_values])

    def save_model(self, path: str) -> None:
        joblib.dump(self, path)
        #dumps the whole object (pipeline + calibrated pipeline) so it doesn't need retraining every time

    @staticmethod
    def load_model(path: str):
        return joblib.load(path)
        #loads back whatever save_model wrote to disk


lr_predictor = FighterPredictor(model=LogisticRegression())
xgb_predictor = FighterPredictor(model=XGBClassifier())
