import unittest
from ..employee import Employee
from ..department import Department
from ..review import Review
from .. import CURSOR, CONN

class TestEmployeeReviews(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup tables for testing
        Department.create_table()
        Employee.create_table()
        Review.create_table()

    @classmethod
    def tearDownClass(cls):
        # Clean up tables after tests
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CONN.commit()

    def setUp(self):
        # Clean up data before each test
        CURSOR.execute("DELETE FROM reviews")
        CURSOR.execute("DELETE FROM employees")
        CURSOR.execute("DELETE FROM departments")
        CONN.commit()

    def test_employee_reviews(self):
        # Create department
        dept = Department.create("Sales", "NY")

        # Create employee
        emp = Employee.create("John Doe", "Salesperson", dept.id)

        # Create reviews associated with employee
        rev1 = Review("2023", "Excellent performance", emp.id)
        rev1.save() if hasattr(rev1, 'save') else None  # save method assumed
        rev2 = Review("2024", "Outstanding achievement", emp.id)
        rev2.save() if hasattr(rev2, 'save') else None

        # Fetch reviews using employee.reviews()
        reviews = emp.reviews()
        self.assertEqual(len(reviews), 2)
        self.assertEqual(reviews[0].summary, "Excellent performance")
        self.assertEqual(reviews[1].summary, "Outstanding achievement")

if __name__ == "__main__":
    unittest.main()
