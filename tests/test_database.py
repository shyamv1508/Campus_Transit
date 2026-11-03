import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "test.db"
        self.patch = patch.object(database, "DB_PATH", self.db_path)
        self.patch.start()
        database.init_db()

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def test_demo_admin_can_login(self):
        user = database.authenticate("admin", "admin123")
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "admin")

    def test_demo_bus_exists(self):
        data = database.dashboard_data()
        self.assertEqual(data["buses"], 1)
        self.assertEqual(data["students"], 1)

    def test_location_is_saved(self):
        database.save_location(1, 13.0827, 80.2707)
        locations = database.latest_locations()
        self.assertEqual(len(locations), 1)
        self.assertAlmostEqual(locations[0]["latitude"], 13.0827)


if __name__ == "__main__":
    unittest.main()
