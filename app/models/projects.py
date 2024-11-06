from typing import List, Dict, Union
from app.utils import (
    db_read_connection,
    db_write_connection,
    calculate_total_project_pages,
)


@db_read_connection
def fetch_projects(
    page: int, limit: int, **kwargs
) -> Dict[str, Union[List[Dict[str, Union[int, str]]], int]]:
    cursor = kwargs["cursor"]
    offset = (page - 1) * limit if limit else 0

    query = """
    SELECT
        p.pid,
        p.name,
        COUNT(DISTINCT e.id) AS error_count,
        COUNT(DISTINCT r.id) AS rejection_count
    FROM
        projects p
    LEFT JOIN
        error_logs e ON e.project_id = p.id
    LEFT JOIN
        rejection_logs r ON r.project_id = p.id
    GROUP BY
        p.pid, p.name
    ORDER BY p.name
    LIMIT %s OFFSET %s
    """
    cursor.execute(query, [limit, offset])
    rows = cursor.fetchall()

    projects = [
        {
            "project_id": row[0],
            "project_name": row[1],
            "issue_count": row[2] + row[3],
        }
        for row in rows
    ]

    total_pages = calculate_total_project_pages(cursor, limit)

    return {
        "projects": projects,
        "total_pages": total_pages,
        "current_page": int(page),
    }


@db_write_connection
def add_project(pid: int, name: str, **kwargs) -> None:
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = "INSERT INTO projects (pid, name) VALUES (%s, %s)"
    cursor.execute(query, [pid, name])
    connection.commit()


@db_write_connection
def delete_project_by_id(pid: int, **kwargs) -> bool:
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = "DELETE FROM projects WHERE pid = %s"
    cursor.execute(query, [pid])
    rows_deleted = cursor.rowcount
    connection.commit()

    return rows_deleted > 0


@db_write_connection
def update_project_name(pid: int, new_name: str, **kwargs) -> bool:
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = "UPDATE projects SET name = %s WHERE pid = %s"

    cursor.execute(query, [new_name, pid])
    rows_updated = cursor.rowcount
    connection.commit()

    return rows_updated > 0
