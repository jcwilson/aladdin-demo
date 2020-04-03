import logging

from elasticsearch_connection import connection


def main():
    logging.basicConfig(
        format="%(levelname)-8s %(name)s(%(lineno)d) %(message)s", level=logging.INFO
    )

    populate(connection)


def populate(connection):
    logging.info("Populating elasticsearch...")
    connection.index(
        index="messages",
        doc_type="song",
        id=1,
        body={
            "author": "Aladdin",
            "song": "A Whole New World",
            "lyrics": ["I can show you the world"],
            "awesomeness": 42,
        },
    )
    logging.info("Populated elasticsearch")


if __name__ == "__main__":
    main()
