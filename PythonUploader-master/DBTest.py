from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import File

DATABASE_URI = 'sqlite:///file_storage.db'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

def get_file_info():
    session = Session()
    try:
        files = session.query(File).all()

        if not files:
            return "No files found in the database."

        file_info = []
        for file in files:
            file_info.append(f"File ID: {file.id}, Filename: {file.filename}, Size: {len(file.data)} bytes, Base62 Result: {file.base62_result}")

        return "\n".join(file_info)
    finally:
        session.close()

if __name__ == '__main__':
    file_info = get_file_info()
    print(file_info)
