from app import mongo
from controller.MongoMigration import drop_and_create_new

drop_and_create_new(mongo)
