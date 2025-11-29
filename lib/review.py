# lib/review.py

from __future__ import annotations
from typing import Optional, List
import sqlite3

from lib import CONN, CURSOR

class Review:

    all: dict[int, Review] = {}

    def __init__(self, year, summary: str, employee_id: int, id: Optional[int] = None):
        self.id = id
        self.year = year
        self.summary = summary
        self._employee_id = employee_id

    def __repr__(self) -> str:
        return (
            f"<Review {self.id}, {self.year}, "
            + f"{self.employee_id}, {self.summary}>"
        )

    @property
    def year(self) -> int:
        return self._year

    @year.setter
    def year(self, year) -> None:
        if isinstance(year, (int, str)) and int(year) >= 2000:
            self._year = int(year)
        else:
            raise ValueError(
                "year must be an integer that is greater than or equal to 2000"
            )

    @property
    def summary(self) -> str:
        return self._summary

    @summary.setter
    def summary(self, summary: str) -> None:
        if isinstance(summary, str) and len(summary):
            self._summary = summary
        else:
            raise ValueError("summary must be a non-empty string")

    @property
    def employee(self):
        if not hasattr(self, "_employee") and self._employee_id is not None:
            self._employee = Employee.find_by_id(self._employee_id)
        return getattr(self, "_employee", None)

    @employee.setter
    def employee(self, employee) -> None:
        from lib.employee import Employee
        if isinstance(employee, Employee) and employee.id:
            self._employee = employee
            self._employee_id = employee.id
        else:
            raise ValueError(
                "employee must be an instance of Employee that has been persisted to the database"
            )

    @property
    def employee_id(self) -> int:
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id: int) -> None:
        from lib.employee import Employee
        if isinstance(employee_id, int) and Employee.find_by_id(employee_id):
            self._employee_id = employee_id
            if hasattr(self, "_employee"):
                del self._employee
        else:
            raise ValueError(
                "employee_id must be the id of an Employee instance that has been persisted to the database"
            )

    @classmethod
    def create_table(cls) -> None:
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            summary TEXT,
            employee_id INTEGER)
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls) -> None:
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self) -> None:
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, year, summary: str, employee_id: int) -> "Review":
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row: sqlite3.Row) -> "Review":
        review = cls.all.get(row[0])
        if review:
            review._year = row[1]
            review._summary = row[2]
            review._employee_id = row[3]
        else:
            review = cls(row[1], row[2], row[3], row[0])
            cls.all[review.id] = review
        return review

    @classmethod
    def get_all(cls) -> List["Review"]:
        sql = """
            SELECT * FROM reviews
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id: int) -> Optional["Review"]:
        sql = """
            SELECT * FROM reviews WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self) -> None:
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self) -> None:
        sql = """
            DELETE FROM reviews WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None