import unittest

from drones import Drone, DroneStore, DroneAction

class DroneTest(unittest.TestCase):
    def test_droneAdd(self):
        # Arrange
        dr = Drone("Tester")
        dr2 = Drone("Tester2")
        dr3 = Drone("Tester3")
        dr4 = Drone("Tester3")
        store = DroneStore()

        #Act
        store.add(dr)
        store.add(dr2)
        store.add(dr3)

        listy = []
        
        #Assert
        for i in store.list_all():
            listy.append(store.get(i))

        self.assertIn(dr, listy)
        self.assertIn(dr2, listy)
        self.assertIn(dr3, listy)
        self.assertNotIn(dr4, listy)
        
    def test_droneAddException(self):
        #Arrange
        store = DroneStore()
        dr = Drone("Dupe")

        store.add(dr)
        
        #Act and Assert
        with self.assertRaises(Exception):
            store.add(dr)

    def test_droneRemove(self):
        #Arrange
        store = DroneStore()
        dr = Drone("Test")
        dr2 = Drone("Test2")
        dr3 = Drone("Test3")
        
        store.add(dr)
        store.add(dr2)
        
        #Act
        store.remove(dr2)

        #Assert
        listy = []
        for i in store.list_all():
            listy.append(store.get(i))

        self.assertIn(dr, listy)
        self.assertNotIn(dr2, listy)

    def test_droneRemoveException(self):
        #Arrange
        store = DroneStore()
        dr = Drone("Test")
        store.add(dr)
        
        store.remove(dr)

        #Act and Assert
        with self.assertRaises(Exception):
            store.remove(dr)

if __name__ == '__main__':
    unittest.main()
