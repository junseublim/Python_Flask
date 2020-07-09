#text로 실행할 sql 만든다.
from sqlalchemy import text

class UserDao:
    def __init__(self, database):
        self.db = database

    def insert_user(self, user):
        return self.db.execute(text("""
        insert into users 
        (name, email, profile, hashed_password) values ( :name, :email, :profile, :password)
        """), user).lastrowid

    def get_user_id_and_password(self, email):
        row = self.db.execute(text("""
        select id, hashed_password
        from users
        where email = :email
        """), {'email' : email}).fetchone()

        return {
            'id' : row['id'],
            'hashed_password' : row['hashed_password']
        } if row else None

    def insert_follow(self, user_id, follow_user_id):
        return self.db.execute(text("""
        insert into users_follow_list
        (user_id, follow_user_id) values (:user_id, :follow_user_id)
        """), {
            'user_id' : user_id,
            'follow_user_id' : follow_user_id
        }).rowcount

    def insert_unfollow(self, user_id, unfollow_user_id):
        return self.db.execute(text("""
               delete from users_follow_list
               where user_id = :id and follow_user_id = : unfollow_user_id
                
               """), {
            'user_id': user_id,
            'follow_user_id': unfollow_user_id
        }).rowcount