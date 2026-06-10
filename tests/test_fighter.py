from src.fighter import Fighter
import pytest


@pytest.fixture
def fighter_data():
    return {"name": "Islam Makhachev", "age": 32, "weight_class": "Lightweight", "record": "28-1-0"}

def test_fighter_creation(fighter_data):
    f = Fighter(fighter_data["name"], fighter_data["age"], fighter_data["weight_class"], fighter_data["record"])
    assert f.name == fighter_data["name"]

def test_is_title_eligible():
    assert Fighter.is_title_eligible("10-1-0") == True
#test to see if record is eligible

def test_is_title_not_eligible():
    assert Fighter.is_title_eligible("8-1-0") == False
#test to see if record is not eligible


def test_title_letter():
    with pytest.raises(ValueError): #assert function raises exception
        Fighter.is_title_eligible("haha")
#test to see if record throws exception for invalid input