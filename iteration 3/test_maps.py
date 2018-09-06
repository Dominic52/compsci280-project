import unittest

from maps import Map, MapStore

class test_maps(unittest.TestCase):
    def test_add_map(self):
        #Arrange
        m = Map("mappy", "somefilepath")
        mStore = MapStore()
        
        #Act
        mStore.add(m)

        #Assert
        listy = []

        for i in mStore.list_all():
            listy.append(mStore.get(i))

        self.assertIn(m, listy)

    def test_add_map_exception(self):
        #Arrange
        m = Map("mappy", "somefilepath")
        mStore = MapStore()

        mStore.add(m)

        #Act and Assert
        with self.assertRaises(Exception):
            mStore.add(m)

    def test_remove_map(self):
        #Arrange
        m = Map("mappy", "somefilepath")
        n = Map("flappy", "anotherfilepath")
        mStore = MapStore()
        
        mStore.add(m)
        mStore.add(n)

        #Act
        mStore.remove(m)
        
        #Assert
        listy = []

        for i in mStore.list_all():
            listy.append(mStore.get(i))

        self.assertNotIn(m, listy)

    def test_remove_map_exception(self):
        #Arrange
        m = Map("mappy", "somefilepath")
        n = Map("flappy", "anotherfilepath")
        mStore = MapStore()
        
        mStore.add(m)
        mStore.add(n)

        mStore.remove(m)
        
        #Act and Assert
        with self.assertRaises(Exception):
            mStore.remove(m)

    def test_list_all(self):
        #Arrange
        m = Map("mappy", "somefilepath")
        n = Map("flappy", "anotherfilepath")
        mStore = MapStore()
        
        mStore.add(m)
        mStore.add(n)

        #Act and Assert
        listy = []
        
        for i in mStore.list_all():
            listy.append(mStore.get(i))

        self.assertIn(m, listy)
        self.assertIn(n, listy)

    def test_get(self):
         #Arrange
        m = Map("mappy", "somefilepath")
        n = Map("flappy", "anotherfilepath")
        mStore = MapStore()
        
        mStore.add(m)
        mStore.add(n)

        #Act and Assert
        self.assertEquals(m, mStore.get("mappy"))

    def test_get_fail(self):
         #Arrange
        m = Map("mappy", "somefilepath")
        n = Map("flappy", "anotherfilepath")
        mStore = MapStore()
        
        mStore.add(m)
        mStore.add(n)

        #Act and Assert
        self.assertIsNone(mStore.get("tappy"))

if __name__ == '__main__':
    unittest.main()
