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

## **08/06/2026** ## 
implmenting some numpy calculations such as np where for filtering arrays and np.dot to multiply and sum arrays for a single weighted value

## **08/06/2026** ## 
adding np.clip to keep values clamped between 0 and 1 in probability context

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

