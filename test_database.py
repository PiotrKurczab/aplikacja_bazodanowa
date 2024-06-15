import unittest
import sqlite3
import csv
import os
from database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database()

    def tearDown(self):
        self.db.conn.close()

    def test_fetch_all_customers(self):
        customers = self.db.fetch_all_customers()
        self.assertEqual(len(customers), 4)
        self.assertEqual(customers[0][1], "Michał Kowalski")

    def test_fetch_customer_orders(self):
        orders = self.db.fetch_customer_orders()
        self.assertEqual(len(orders), 4)

    def test_delete_record(self):
        self.db.delete_record('customers', 1)
        customers = self.db.fetch_all_customers()
        self.assertEqual(len(customers), 3)

    def test_update_record(self):
        self.db.update_record('customers', 1, 'name', 'Jan Kowalski')
        customers = self.db.fetch_all_customers()
        self.assertEqual(customers[0][1], 'Jan Kowalski')

    def test_export_to_csv(self):
        self.db.export_to_csv('test.csv')
        with open('test.csv', 'r', encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)
            self.assertEqual(rows[0][0], 'Customers')
            self.assertEqual(rows[1][1], 'Michał Kowalski')
        os.remove('test.csv')

    def test_import_from_csv(self):
        with open('test_import.csv', 'w', encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Customers'])
            writer.writerow([1, 'Test User', 'test.user@example.com', '123-456-789', 'Test City'])
            writer.writerow(['Orders'])
            writer.writerow([])
            writer.writerow(['Products'])
            writer.writerow([])
            writer.writerow(['Suppliers'])
            writer.writerow([])
        
        self.db.import_from_csv('test_import.csv')
        customers = self.db.fetch_all_customers()
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0][1], 'Test User')
        os.remove('test_import.csv')

if __name__ == '__main__':
    unittest.main()