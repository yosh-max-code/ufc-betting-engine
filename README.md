# **ufc-betting-engine**

## Developing a UFC Betting engine to further understand data manipulation in context with betting and sports

### **04/06/2026**
initial project structure setup: adding src, tests, data and notebooks folders

### **05/06/2026**
implementing classes, __init__ , self, 
a class for fighter with att(name, age, weight class and record) & added champion method class to check for title

adding type hints in code to improve clarity and clean practice

implemented getter and setter methods using @property and @age.setter for manipulating attribute
verifying private and public usages of self.age / self._age

### **07/06/2026**
implemented @classmethod
for applying method to a whole cls and parsing messy data like dict by extracting fighter keys using Fighter.from_dict(Data)

implemented @staticmethod 
for utility and calculation, in this case a checker for title eligibility if wins are 10 and above in record '10-x-x'

### **08/06/2026** ## 
- implmenting some numpy calculations such as np where for filtering arrays and np.dot to multiply and sum arrays for a single weighted value
- adding np.clip to keep values clamped between 0 and 1 in probability context

### **09/06/2026**
implemented Google-style docstrings across all methods for production-level documentation

added explicit try/except exception handling with descriptive error messages
- ValueError raised for invalid record formats in is_title_eligible
- KeyError caught and re-raised in from_dict for missing fighter fields
- json.JSONDecodeError handled for malformed JSON feed simulation

implemented JSON parsing using Python's json library
- json.loads() to parse incoming fight data strings

### **10/06/2026**
installed pytest and configured project test structure
- added conftest.py at root level for import resolution
- added __init__.py to src/ to make it a Python package

wrote unit test suite in tests/test_fighter.py
- positive, negative and edge case tests for is_title_eligible
- pytest.fixture for reusable mock fighter data
- pytest.raises() to verify ValueError on invalid input
- full Fighter object creation test asserting all attributes

production Git workflow practice
- feature branching with feature/ naming convention
- opening and merging Pull Requests on GitHub
- simulated and resolved a merge conflict locally

### **11/06/2026**

- Created src/model.py on branch phase-2-ml-engineering
- Built a FighterPredictor class with a sklearn Pipeline bundling preprocessing and a model into one object
- Added a ColumnTransformer to handle mixed data types — StandardScaler for numeric columns (age, strike_accuracy) and OneHotEncoder for categorical columns (stance, weight_class)
- Refactored to use dependency injection,  model is passed as a parameter with LogisticRegression() as the default, making the class reusable for any - sklearn-compatible model
- Added XGBClassifier as the production model, instantiated separately as xgb_predictor

### **12/06/2026**

Probability Calibration (Betting Core)
  - Understand why raw machine learning model scores are not true probabilities.
  - Learn Platt Scaling and Isotonic Regression to calibrate model outputs into sharp market percentages.


### **19/06/2026**
-LOG LOSS, AUC and calibration curve implementation
- Built get_shap_values() method on FighterPredictor using shap.TreeExplainer
- Method extracts the raw classifier via self.pipeline.named_steps["classifier"], transforms input data via self.pipeline.named_steps["preprocessor"].transform(), - then computes per-feature contributions with explainer.shap_values()
- Verified output shape (n_fighters, n_features) against synthetic test data in notebooks/test_model_manual.ipynb
- Used get_feature_names_out() to map SHAP's unlabeled NumPy array columns back to actual feature names (scaler__age, encoder__stance_orthodox, etc.) for readability
- Confirmed SHAP values correctly attribute positive/negative contributions per fighter, per feature, matching the one-hot encoded preprocessing schema


### **02/07/2026**

 — PySpark feature engineering on Databricks
- Ported pandas create_fight_differentials logic to PySpark (src/spark_features.py)
- Diagnosed and resolved local Windows/Hadoop winutils.exe write limitation by 
  moving execution to Databricks Community Edition (serverless, Spark Connect)
- Confirmed full read -> transform -> write pipeline working on Unity Catalog 
  volumes, verified via _SUCCESS marker and output partition files

 — Model training on real fight data
- Rebuilt FighterPredictor's ColumnTransformer to use real differential features 
  (ko_dif, sig_str_dif, dif_odds, physical/streak differentials) and stance/
  weight_class categoricals, replacing placeholder columns from Phase 2 prototyping
- Added handle_unknown='ignore' to OneHotEncoder for unseen-category safety at 
  inference time
- Built binary target from Winner column; excluded Draw/No Contest fights as 
  non-binary outcomes
- Implemented time-based (not random) train/test split to avoid data leakage 
  and simulate real forward-looking prediction
- Result: AUC 0.71, log-loss 0.63 on held-out future fights — confirms model 
  generalizes beyond training data, not just memorizing it

Known limitations (deliberately deferred):
- src/spark_features.py locally still reflects pre-Databricks version; 
  Databricks notebook version not yet synced back to repo
- Databricks Repos/Git integration not set up; class code manually copied 
  into notebook cells
- Feature set excludes dedicated stance-matchup encoding (uses R_Stance/
  B_Stance separately rather than a combined matchup feature)