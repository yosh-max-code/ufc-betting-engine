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



class FighterPredictor:
    def __init__(self, model=LogisticRegression()) -> None:
        
        

        self.preprocessor = ColumnTransformer(transformers=[("scaler", StandardScaler(), ["age", "strike_accuracy"]),
                                                            ("encoder", OneHotEncoder(), ["stance", "weight_class"])])
        #ENCODE non numerical catergories into numbers i.e stance, weightclass

        self.pipeline = Pipeline(steps=[("preprocessor", self.preprocessor), 
                                        ("classifier", model)])
        
        self.calibrated_pipeline = CalibratedClassifierCV(estimator=self.pipeline, method="sigmoid")

    
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
        #LOG LOSS CALCULATION

    def evaluate_auc(self, x: pd.DataFrame, y_true: pd.Series) -> float:
        y_pred_proba = self.predict_proba_calibrated(x)
        return roc_auc_score(y_true, y_pred_proba)


lr_predictor = FighterPredictor(model=LogisticRegression())
xgb_predictor = FighterPredictor(model=XGBClassifier())
         



