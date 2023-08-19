from pymongo import MongoClient

__all__ = "get_database"


# Define getDatabase function
def get_database():
    try:
        connectionUrl = ()
        client = MongoClient(connectionUrl)
        print(client.server_info())
        return client.get_database()
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)

# if __name__ == "__main__":     
# Get the database
#     dbname = get_database()
