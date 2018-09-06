import unittest
from datetime import timedelta, date

from operators import Operator, OperatorAction, OperatorStore

class test_operators(unittest.TestCase):
    def test_operatorValidity(self):
        #Arrange
        op = Operator()
        op.first_name = "monty"
        op.date_of_birth = date(1990, 9, 30)
        op.drone_license = 2
        op.rescue_endorsement = True
        op.operations = 5
        opStore = OperatorStore()

        #Act
        action = opStore.add(op)
        
        #Assert
        self.assertIsNotNone(op.first_name)
        self.assertIsNotNone(op.date_of_birth)
        self.assertIsNotNone(op.drone_license)
        if (op.drone_license == 2):
            self.assertTrue(date.today() - op.date_of_birth >= timedelta(7300))
        if (op.rescue_endorsement):
            self.assertTrue(op.operations >= 5)
            
        self.assertTrue(action.is_valid())
        
    def test_operatorInvalidName(self):
        #Arrange
        op = Operator()
        op.date_of_birth = date(1990, 9, 30)
        op.drone_license = 2
        op.rescue_endorsement = True
        op.operations = 5
        opStore = OperatorStore()

        #Act
        action = opStore.add(op)
        
        #Assert
        self.assertIsNone(op.first_name)
        self.assertFalse(action.is_valid())
        self.assertIn("First name is required", action.messages)
        
    def test_operatorInvalidDOB(self):
        #Arrange
        op = Operator()
        op.first_name = "monty"
        op.drone_license = 2
        op.rescue_endorsement = True
        op.operations = 5
        opStore = OperatorStore()

        #Act
        action = opStore.add(op)
        
        #Assert
        self.assertIsNone(op.date_of_birth)
        self.assertFalse(action.is_valid())
        self.assertIn("Date of birth is required", action.messages)

    def test_operatorInvalidDroneLicense(self):
        #Arrange
        op = Operator()
        op.first_name = "monty"
        op.date_of_birth = date(1990, 9, 30)
        op.rescue_endorsement = True
        op.operations = 5
        opStore = OperatorStore()

        #Act
        action = opStore.add(op)
        
        #Assert
        self.assertIsNone(op.drone_license)
        self.assertFalse(action.is_valid())
        self.assertIn("Drone license is required", action.messages)

    def test_operatorInvalidDL2(self):
        #Arrange
        op = Operator()
        op.first_name = "monty"
        op.rescue_endorsement = True
        op.operations = 5
        op.date_of_birth = date(2015, 9, 30)
        op.drone_license = 2
        opStore = OperatorStore()

        #Act
        action = opStore.add(op)
        
        #Assert
        if (op.drone_license == 2):
            self.assertFalse(date.today() - op.date_of_birth >= timedelta(7300))
        self.assertFalse(action.is_valid())
        self.assertIn("Operator should be at least twenty to hold a class 2 license", action.messages)

    def test_operatorInvalidEndorsement(self):
        #Arrange
        op = Operator()
        op.first_name = "monty"
        op.date_of_birth = date(1990, 9, 30)
        op.drone_license = 2
        op.rescue_endorsement = True
        op.operations = 4
        opStore = OperatorStore()

        #Act
        action = opStore.add(op)
        
        #Assert
        if (op.rescue_endorsement):
            self.assertFalse(op.operations >= 5)
        self.assertFalse(action.is_valid())
        self.assertIn("Operator should have been involved in five prior rescue operations to hold a rescue drone endorsement", action.messages)

    def test_commit(self):
        #Arrange
        op = Operator()
        op.first_name = "monty"
        op.family_name = "python"
        op.date_of_birth = date(1990, 9, 30)
        op.drone_license = 2
        op.rescue_endorsement = True
        op.operations = 5
        opStore = OperatorStore()

        action = opStore.add(op)

        #Act
        if action.is_valid():
            action.commit()
        else:
            for i in action.messages:
                print(i)
        
        #Assert
        listy = []
        for i in opStore.list_all():
            listy.append(opStore.get(i))
        self.assertIn(op, listy)
    
if __name__ == '__main__':
    unittest.main()
