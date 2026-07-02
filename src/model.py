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
        explainer = shap.TreeExplainer(self.pipeline.named_steps["classifier"])
        transformed_data = self.pipeline.named_steps["preprocessor"].transform(fighter_df)
        contributions = explainer.shap_values(transformed_data)
        return contributions


lr_predictor = FighterPredictor(model=LogisticRegression()) 
xgb_predictor = FighterPredictor(model=XGBClassifier())
         



