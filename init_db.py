from database.database import engine
from database.models import Base

print("Création de la base de données")
Base.metadata.create_all(bind=engine)
print("Base créée avec succés")