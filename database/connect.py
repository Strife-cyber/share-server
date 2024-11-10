import json
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URI
DATABASE_URI = 'postgresql+psycopg2://postgres:admin@localhost:5432/sharechat'

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URI)

# Create the base class for ORM models
Base = declarative_base()

# Define the Files model
class Files(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    uploaded = Column(Boolean, default=False)


    # CRUD methods
    @classmethod
    def create(cls, db_session, file_name, uploaded=False):
        """Creates and saves a new file record."""
        new_file = cls(file_name=file_name, uploaded=uploaded)
        db_session.add(new_file)
        db_session.commit()
        return new_file

    @classmethod
    def get_by_name(cls, db_session, file_name):
        """Retrieves a file record by its ID."""
        return db_session.query(cls).filter_by(file_name=file_name).first()

    @classmethod
    def update_uploaded_status(cls, db_session, file_id, uploaded_status):
        """Updates the 'uploaded' status of a file record."""
        file_record = db_session.query(cls).filter_by(id=file_id).first()
        if file_record:
            file_record.uploaded = uploaded_status
            db_session.commit()
        return file_record

    @classmethod
    def delete(cls, db_session, file_id):
        """Deletes a file record by its ID."""
        file_record = db_session.query(cls).filter_by(id=file_id).first()
        if file_record:
            db_session.delete(file_record)
            db_session.commit()
        return file_record

    def destructure(self):
        """Returns a JSON representation of the file object."""
        return json.dumps({
            'id': self.id,
            'file_name': self.file_name,
            'uploaded': self.uploaded
        })


# Set up the database session
Session = sessionmaker(bind=engine)
session = Session()

# Create the tables in the database (if not already existing)
Base.metadata.create_all(engine)
