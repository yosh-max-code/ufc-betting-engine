


class Fighter:
    #fighter class method 

    def __init__(self, name, age, weight_class, record):
        #these are attributes so no brackets needed when calling it
        self.name = name
        self.age = age
        self.weight_class = weight_class
        self.record = record

    #Method , can only be called with brackets so .summary()
    def summary(self):
        return(f'{self.name} | Age: {self.age} | {self.weight_class} | W/L/D: {self.record}')

p1 = Fighter('Alex Perreira', 36, 'Heavyweight', '13-3-0')
p2 = Fighter('Ilia Topuria', 29, 'Lightweight', '17-0-0' )
#print(p1.summary())


#when inheriting always put in brackets where I am taking the attributes
class Champion(Fighter):
    #champion which inherits att from fighter
    def __init__(self, name, age, weight_class, record, title):
        #super(). method used to call parent init and repeat functions 
        super().__init__(name, age, weight_class, record)
        self.title = title

c1 = Champion('Islam Makhachev', 34, 'Welterweight', '28-1-0', 'Champion')
print(c1.summary())
print(c1.title)