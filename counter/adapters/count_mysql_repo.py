from typing import List

import mysql.connector

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo


class CountMySQLRepo(ObjectCountRepo):

    def __init__(self, host, port, user, password, database):
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__database = database

        self.__create_table_if_not_exists()

    def __get_connection(self):
        return mysql.connector.connect(
            host=self.__host,
            port=self.__port,
            user=self.__user,
            password=self.__password,
            database=self.__database
        )

    def __create_table_if_not_exists(self):
        connection = self.__get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS object_counts (
                    object_class VARCHAR(255) PRIMARY KEY,
                    count INT NOT NULL
                )
            """)

            connection.commit()

        finally:
            cursor.close()
            connection.close()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        connection = self.__get_connection()
        cursor = connection.cursor()

        try:
            if object_classes:
                placeholders = ",".join(["%s"] * len(object_classes))
                query = f"""
                    SELECT object_class, count
                    FROM object_counts
                    WHERE object_class IN ({placeholders})
                """
                cursor.execute(query, object_classes)
            else:
                cursor.execute("""
                    SELECT object_class, count
                    FROM object_counts
                """)

            object_counts = [
                ObjectCount(
                    object_class=row[0],
                    count=row[1]
                )
                for row in cursor.fetchall()
            ]

            return object_counts

        finally:
            cursor.close()
            connection.close()

    def update_values(self, new_values: List[ObjectCount]):
        connection = self.__get_connection()
        cursor = connection.cursor()

        try:
            query = """
                INSERT INTO object_counts (object_class, count)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                    count = count + VALUES(count)
            """

            for value in new_values:
                cursor.execute(
                    query,
                    (value.object_class, value.count)
                )

            connection.commit()

        finally:
            cursor.close()
            connection.close()