from google.appengine.ext import db


class Accumulator(db.Model):
    """
    Unique identifiers (global).

    Usage:
        id = Accumulator.get_unique()
        sid = int_to_sid(id)
    """
    counter = db.IntegerProperty(default=0)

    @classmethod
    def get_unique(cls):
        def increment_counter(key):
            obj = db.get(key)
            obj.counter += 1
            obj.put()
            return obj.counter

        acc = db.GqlQuery("SELECT * FROM Accumulator").get()
        if acc is None:
            acc = Accumulator()
            acc.put()
        return db.run_in_transaction(increment_counter, acc.key())


short_chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def int_to_sid(i):
    s = ''
    while i != 0:
        b = i % len(short_chars)
        s = short_chars[b] + s
        i = i / len(short_chars)
    return s
