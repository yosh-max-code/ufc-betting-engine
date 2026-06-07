


class Fighter:
    #fighter class method 

    def __init__(self, name :str, age : int, weight_class: str, record:str) -> None: #adding type hints to show what ouput will show    

                #these are attributes so no brackets needed when calling it
        self.name = name
        self.age = age # routes through setter for validation
        self.weight_class = weight_class
        self.record = record

    #getter method for correct age
    @property
    def age(self) -> int:
        return self._age
        #._ to store as private and internal use only
        
        #code setter block to check if age is in valid range
    @age.setter
    def age(self, value: int) -> None:
        if value < 18 or value > 50:
            raise ValueError('Not in valid range')
        else:
            self._age = value


    #class method for whole class to parse
    @classmethod
    def from_dict(cls, data:dict): #cls instead of self
        return cls(data['name'], data['age'],data['weight_class'], data['record'])
    
    #static method doesnt need self or cls as its utility for pure calc
    #if fighter has a record of 10 or more wins he is eligible for a title 
    @staticmethod
    def is_title_eligible(record: str): 
        win_loss = record.split('-')
        wins = int(win_loss[0])
        if wins >= 10:
            return True
        else:
            return False 


    #Method , can only be called with brackets so .summary()
    def summary(self)-> str: #type hint for method
        return(f'{self.name} | Age: {self._age} | {self.weight_class} | W/L/D: {self.record}') 

p1 = Fighter('Alex Perreira', 36, 'Heavyweight', '13-3-0')
p2 = Fighter('Ilia Topuria', 29, 'Lightweight', '17-0-0' )
#print(p1.summary())


#when inheriting always put in brackets where I am taking the attributes
class Champion(Fighter):
    #champion which inherits att from fighter
    def __init__(self, name: str, age: int, weight_class: str, record: str, title: str) -> None: #adding type hints to show what ouput will show
        #super(). method used to call parent init and repeat functions 
        super().__init__(name, age, weight_class, record)
        self.title = title

c1 = Champion('Islam Makhachev', 34, 'Welterweight', '28-1-0', 'Champion')
print(c1.summary())



"""
fighter_data = {"name": "Islam Makhachev", "age": 32, "weight_class": "Lightweight", "record": "28-1-0"}
#centralised parsing to prep for data received in messy formats [ENCAPSULATION]
D1 = Fighter.from_dict(fighter_data) 
print(D1.summary())
"""

#checking if W/L record is title eligible need Wins > 9
"""
t1 = Fighter.is_title_eligible('10-1-0')
t2 = Fighter.is_title_eligible('9-1-0')
print(t1)
print(t2)
"""
