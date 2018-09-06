import unittest

from drones import Drone, DroneStore
from operators import Operator

class AllocationTest(unittest.TestCase):
    def test_allocate_success(self):
        # Arrange
        dr = Drone("Test drone", class_type=1)
        op = Operator()
        op.first_name = "John"
        op.drone_license = 1
        store = DroneStore()

        # Act
        act = store.allocate(dr, op)

        # Assert
        self.assertTrue(act.is_valid())

    def test_only_one_drone(self):
        # Arrange
        dr = Drone("Test drone", class_type=1)
        op = Operator()
        op.first_name = "John"
        op.drone_license = 1
        op.drone = Drone("Yet another")
        store = DroneStore()

        # Act
        act = store.allocate(dr, op)

        # Assert
        self.assertFalse(act.is_valid())
        self.assertIn("Operator can only control one drone", act.messages)

    def test_holds_correct_license(self):
        # Arrange
        dr = Drone("Test drone", class_type=2)
        op = Operator()
        op.first_name = "John"
        op.drone_license = 1
        store = DroneStore()

        # Act
        act = store.allocate(dr, op)

        # Assert
        self.assertFalse(act.is_valid())
        self.assertIn("Operator does not have correct drone license", act.messages)

    def test_has_rescue_endorsement(self):
        # Arrange
        dr = Drone("Test drone", rescue=True)
        op = Operator()
        op.first_name = "John"
        op.drone_license = 1
        store = DroneStore()

        # Act
        act = store.allocate(dr, op)

        # Assert
        self.assertFalse(act.is_valid())
        self.assertIn("Operator does not have rescue endorsement", act.messages)

    def test_commit(self):
        # Arrange
        dr = Drone("Test drone", class_type=1)
        op = Operator()
        op.first_name = "John"
        op.drone_license = 1
        store = DroneStore()

        # Act
        act = store.allocate(dr, op)
        act.commit()

        # Assert
        self.assertEquals(dr.operator, op)
        self.assertEquals(op.drone, dr)

if __name__ == '__main__':
    unittest.main()
