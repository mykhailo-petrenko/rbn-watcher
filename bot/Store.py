import sqlite3

from bot.types import SubscriptionDTO

class Store:
    def __init__(self, connection_string):
        self._connection = sqlite3.connect(connection_string)
        self._cursor = self._connection.cursor()
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription(
                chat_id varchar(255),
                callsign varchar(255),
                created DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

    def add_subscription(self, subscription: SubscriptionDTO):
        data = (
            subscription.chat_id,
            subscription.filter,
        )

        self._cursor.execute("""
            INSERT INTO subscription(chat_id, callsign)
            VALUES (?, ?)
        """, data)
        self._connection.commit()

    def has_subscription(self, chat_id: str, filter: str):
        data = [chat_id, filter]

        rows = self._cursor.execute("""
            SELECT chat_id, callsign, created
            FROM subscription
            WHERE chat_id LIKE ? and callsign LIKE ?
        """, data)

        return len(list(rows)) > 0

    def get_subscriptions(self, chat_id: str):
        data = [chat_id]

        rows = self._cursor.execute("""
            SELECT chat_id, callsign, created
            FROM subscription
            WHERE chat_id LIKE ?
        """, data)

        return list(rows)

    def remove_subscription(self, subscription: SubscriptionDTO):
        data = [
            subscription.chat_id,
            subscription.filter
        ]

        self._cursor.execute("""
            DELETE FROM subscription
            WHERE chat_id LIKE ? and callsign LIKE ?
        """, data)
        self._connection.commit()

    def remove_all_subscriptions(self, chat_id: str):
        data = [chat_id]

        self._cursor.execute("""
            DELETE FROM subscription
            WHERE chat_id LIKE ?
        """, data)
        self._connection.commit()

    def get_all_subscribers(self):
        rows = self._cursor.execute("""
                    SELECT distinct chat_id
                    FROM subscription
                    WHERE 1=1
                """)

        return list([x[0] for x in rows])

if __name__ == "__main__":
    store = Store('/tmp/chat.test.db.sqlite')

    rows = store.get_subscriptions("1231wq")
    assert len(rows) == 0

    if not store.has_subscription("1231wq", "UR3AMP"):
        subscription = SubscriptionDTO()
        subscription.chat_id = "1231wq"
        subscription.filter = "UR3AMP"
        store.add_subscription(subscription)

    assert store.has_subscription("1231wq", "UR3AMP")

    rows = store.get_subscriptions("1231wq")
    print(rows)
    assert len(rows) == 1

    store.remove_all_subscriptions("1231wq")
    rows = store.get_subscriptions("1231wq")
    print(rows)
    assert len(rows) == 0

    subscription = SubscriptionDTO()
    subscription.chat_id = "123123"
    subscription.filter = "UR3AMP"
    store.add_subscription(subscription)

    subscription = SubscriptionDTO()
    subscription.chat_id = "234234"
    subscription.filter = "PD5MI"
    store.add_subscription(subscription)

    rows = store.get_all_subscribers()
    print(rows)

    store.remove_all_subscriptions("123123")
    store.remove_all_subscriptions("234234")

