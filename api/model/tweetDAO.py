#text로 실행할 sql 만든다.
from sqlalchemy import text


class TweetDao:
    def __init__(self, database):
        self.db = database

    def insert_tweet(self, user_id, tweet):
        return self.db.execute(text("""
            insert into tweets
            (user_id, tweet) values ( :user_id, :tweet)
        """), {
            'user_id' : user_id,
            'tweet' : tweet
        }).rowcount
    #execute는 ResultProxy 객체를 반환함.

    def get_timeline(self, user_id):
        timeline = self.db.execute(text("""
        select t.user_id, t.tweet
        from tweets t left join users_follow_list u on u.user_id = :user_id 
        where t.user_id = u.user_id
        or t.user_id = u.follow_user_id
        """), {
            'user_id' : user_id
        }).fethall()

        return [{
            'user_id' : tweet['id'],
            'tweet' : tweet['tweet']
        } for tweet in timeline]
