class TestDBQueries:
    """Utility class for reusable database queries in tests."""

    ### * Users
    @staticmethod
    def get_user_by_email(cursor, email):
        query = "SELECT * FROM users WHERE email = %s;"
        cursor.execute(query, (email,))
        return cursor.fetchone()

    @staticmethod
    def get_user_by_uuid(cursor, uuid):
        query = "SELECT * FROM users WHERE uuid = %s;"
        cursor.execute(query, (uuid,))
        return cursor.fetchone()

    @staticmethod
    def get_all_users(cursor):
        query = "SELECT * FROM users;"
        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def get_password_hash(cursor, uuid):
        query = "SELECT password_hash FROM users WHERE uuid = %s;"
        cursor.execute(query, (uuid,))
        return cursor.fetchone()

    ### * Projects
    @staticmethod
    def get_user_projects(cursor, user_uuid):
        query = """
        SELECT p.*
        FROM projects p
        JOIN user_projects up ON p.id = up.project_id
        WHERE up.user_uuid = %s;
        """
        cursor.execute(query, (user_uuid,))
        return cursor.fetchall()

    @staticmethod
    def get_project_by_uuid(cursor, uuid):
        query = "SELECT * FROM projects WHERE uuid = %s"
        cursor.execute(query, (uuid,))
        return cursor.fetchone()
    
    @staticmethod
    def update_project_sns_topic(cursor, project_uuid, sns_topic_arn):
        query = "UPDATE projects SET sns_topic_arn = %s WHERE uuid = %s"
        cursor.execute(query, (sns_topic_arn, project_uuid))
    
    ### * Project Users
    @staticmethod
    def get_project_users(cursor, project_uuid):
        query = """
        SELECT u.uuid
        FROM projects_users pu
        JOIN users u ON pu.user_id = u.id
        JOIN projects p ON pu.project_id = p.id
        WHERE p.uuid = %s;
        """
        cursor.execute(query, (project_uuid,))
        return cursor.fetchall()

    @staticmethod
    def get_project_user_association(cursor, project_uuid, user_uuid):
        query = """
        SELECT * FROM projects_users
        WHERE project_id = (SELECT id FROM projects WHERE uuid = %s)
        AND user_id = (SELECT id FROM users WHERE uuid = %s);
        """
        cursor.execute(query, (project_uuid, user_uuid))
        return cursor.fetchone()
    
    @staticmethod
    def get_user_by_uuid(cursor, user_uuid):
        query = "SELECT * FROM users WHERE uuid = %s;"
        cursor.execute(query, (user_uuid,))
        return cursor.fetchone()
    
    ### * Error and Rejection Logs
    @staticmethod
    def get_error_by_uuid(cursor, error_uuid):
        query = "SELECT * FROM error_logs WHERE uuid = %s;"
        cursor.execute(query, (error_uuid,))
        return cursor.fetchone()

    @staticmethod
    def get_rejection_by_uuid(cursor, rejection_uuid):
        query = "SELECT * FROM rejection_logs WHERE uuid = %s;"
        cursor.execute(query, (rejection_uuid,))
        return cursor.fetchone()

    @staticmethod
    def count_errors_by_project(cursor, project_uuid):
        query = """
        SELECT COUNT(*) FROM error_logs WHERE project_id = (SELECT id FROM projects WHERE uuid = %s);
        """
        cursor.execute(query, (project_uuid,))
        return cursor.fetchone()[0]

    @staticmethod
    def count_rejections_by_project(cursor, project_uuid):
        query = """
        SELECT COUNT(*) FROM rejection_logs WHERE project_id = (SELECT id FROM projects WHERE uuid = %s);
        """
        cursor.execute(query, (project_uuid,))
        return cursor.fetchone()[0]

    @staticmethod
    def update_error_resolved_status(cursor, error_uuid, resolved):
        query = "UPDATE error_logs SET resolved = %s WHERE uuid = %s;"
        cursor.execute(query, (resolved, error_uuid))

    @staticmethod
    def update_rejection_resolved_status(cursor, rejection_uuid, resolved):
        query = "UPDATE rejection_logs SET resolved = %s WHERE uuid = %s;"
        cursor.execute(query, (resolved, rejection_uuid))