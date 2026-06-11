import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


class FighterPredictor:
    def __init__(self) -> None:

        self.preprocessor = ColumnTransformer(transformers=[("scaler", StandardScaler(), ["age", "strike_accuracy"]),
                                                            ("encoder", OneHotEncoder(), ["stance", "weight_class"])])
        #ENCODE non numerical catergories into numbers




        self.pipeline = Pipeline(steps=[("preprocessor", self.preprocessor), 
                                        ("classifier", LogisticRegression())])
    
    #StandardScaler rescales every feature so they're all on the same playing field. No stat bullies the others.
    #LogisitcRegression a classification model. You feed it fighter stats and it outputs a probability between 0 and 1


    def fit(self, x, y):
        self.pipeline.fit(x, y)
        #showing model histrorical data x = stats, y = winner

    def predict_proba(self, x):
        return self.pipeline.predict_proba(x)
        #returns a win probability for a new matchup


