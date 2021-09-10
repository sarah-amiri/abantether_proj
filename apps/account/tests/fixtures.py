import pytest
import mongoengine


@pytest.fixture
def mongo(request):
    db = mongoengine.connect('testdb', host='mongodb://localhost')
    yield db
    db.drop_database('testdb')
    db.close()
