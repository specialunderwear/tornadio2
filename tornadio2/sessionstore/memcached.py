import pylibmc

class MemcachedSessionStore(object):
    def __init__(self, servers, session_expire_seconds=1000):
        self._store = pylibmc.Client(servers, binary=True,
                                behaviors={"tcp_nodelay": True,
                                            "ketama": True,
                                            "verify_keys": True,
                                            "no_block": True,
                                            "remove_failed": 20})
                                })
        self.session_expire_seconds = session_expire_seconds

    def add(self, session):
        """Add session to the container.

        `session`
            Session object
        """
        session_seconds = session.expiry or 0
        self._store.set(session.session_id, session, time=session_seconds)

    def get(self, session_id):
        """Return session object or None if it is not available

        `session_id`
            Session identifier
        """
        return self._store.get(session_id)

    def remove(self, session_id):
        """Remove session object from the container

        `session_id`
            Session identifier
        """
        session = self._store.get(session_id)

        if session is not None:
            session.promoted = -1
            session.on_delete(True)
            del self._store[session_id]
            return True

        return False

    def expire(self, current_time=None):
        """session can perfectly well expire themselves."""
        pass