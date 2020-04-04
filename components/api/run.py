from api.app import create_app

# This indirection is useful when writing unit tests
app = create_app()
