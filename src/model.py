import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

class FighterPredictor:
    def __init__(self) -> None:
        self.pipeline = Pipeline(steps=[("scaler", StandardScaler()), #
                                        ("classifier", LogisticRegression())])
    
    #StandardScaler rescales every feature so they're all on the same playing field. No stat bullies the others.
    #LogisitcRegression a classification model. You feed it fighter stats and it outputs a probability between 0 and 1


    def fit(self, x, y):
        self.pipeline.fit(x, y)
        #showing model histrorical data x = stats, y = winner

    def predict_proba(self, x):
        return self.pipeline.predict_proba(x)
        #returns a win probability for a new matchup
