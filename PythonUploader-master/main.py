from utils import allowed_file, generate_unique_number, encode  # Import functions from utils.py
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URI, BASE62, ALLOWED_EXTENSIONS  # Import variables from config.py
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
import io
from bcryptmodule import encrypt, decrypt

app = Flask(__name__)

engine = create_engine(DATABASE_URI)
Base = declarative_base()
Session = sessionmaker(bind=engine)


# Define the SQLAlchemy model for the file table
class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    data = Column(LargeBinary, nullable=False)
    base62_result = Column(String(255), nullable=True)  # New column for Base62 result

# Create the table in the database (Run this once to initialize the database)
Base.metadata.create_all(engine)

@app.route('/')
def main_page():
    return render_template('main_page.html')
@app.route('/upload', methods=['GET'])
def show_upload_form():
    return render_template('upload.html')

@app.route('/download', methods=['GET'])
def show_download_page():
    session = Session()
    files = session.query(File).all()
    return render_template('download.html', files=files)

@app.route('/downloadbykeyword', methods=['GET'])
def download_by_keyword_form():
    return render_template('downloadbykeyword.html')

@app.route('/downloadbykeyworddecrypted', methods=['GET'])
def download_by_keyword_form_decrypted():
    return render_template('downloadbykeyworddecrypted.html')


@app.route('/upload', methods=['POST'])
def handle_upload():
    uploaded_file = request.files['file']
    encryption_key = request.form['encryption_key']

    message = ''

    if uploaded_file and allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)
        file_data = uploaded_file.read()

        encrypted_data = encrypt(encryption_key, file_data)
        unique_number = generate_unique_number()
        base62_result = encode(unique_number, BASE62)

        session = Session()
        new_file = File(filename=filename, data=encrypted_data, base62_result=base62_result)
        session.add(new_file)
        session.commit()
        session.close()

        message = f'File uploaded and encrypted successfully. File can be retrieved with {base62_result}.'
    else:
        message = 'File upload failed. Please check the file and try again.'

    return render_template('result.html', message=message)


from flask import render_template

@app.route('/download', methods=['POST'])
def handle_download():
    file_id = request.form['file_id']
    encryption_key = request.form['encryption_key']  # retrieve the provided encryption key

    session = Session()
    file_record = session.query(File).filter_by(id=file_id).first()

    if file_record:
        try:
            # Use the provided encryption key for decryption
            decrypted_data = decrypt(encryption_key, file_record.data)

            # Send the decrypted file data as a response with a custom filename
            return send_file(
                io.BytesIO(decrypted_data),
                as_attachment=True,
                download_name=file_record.filename
            )
        except:  # This exception handles a wrong encryption key or any other decryption error.
            message = "Decryption failed. Possibly wrong encryption key."
            return render_template('result.html', message=message)
    else:
        message = 'File not found'
        return render_template('result.html', message=message), 404










from flask import render_template

@app.route('/downloadbykeyword', methods=['POST'])
def download_file_by_keyword():
    if request.method == 'POST':
        keyword = request.form['keyword']
        session = Session()
        file_record = session.query(File).filter_by(base62_result=keyword).first()

        if file_record:
            # Send the file data as a response with a custom filename
            return send_file(
                io.BytesIO(file_record.data),
                as_attachment=True,  # Treat as an attachment
                download_name=file_record.filename  # Custom filename
            )
        else:
            message = 'File not found for the specified keyword.'
            return render_template('result.html', message=message), 404





@app.route('/downloadbykeyworddecrypted', methods=['POST'])
def download_file_by_keyword_decrypted():
    keyword = request.form['keyword']
    encryption_key = request.form['encryption_key']  # retrieve the provided encryption key

    session = Session()
    file_record = session.query(File).filter_by(base62_result=keyword).first()

    if file_record:
        try:
            # Use the provided encryption key for decryption
            decrypted_data = decrypt(encryption_key, file_record.data)

            # Send the decrypted file data as a response with a custom filename
            return send_file(
                io.BytesIO(decrypted_data),
                as_attachment=True,
                download_name=file_record.filename
            )
        except:  # This exception handles a wrong encryption key or any other decryption error.
            message = "Decryption failed. Possibly wrong encryption key."
            return render_template('result.html', message=message), 400
    else:
        message = 'File not found for the specified keyword.'
        return render_template('result.html', message=message), 404


@app.route('/serverinfo')
def print_server_info():
    # Call the generate_unique_number function
    unique_number = generate_unique_number()

    # Print the generated unique number to the console
    print(f"Unique Number: {unique_number}")

    # Convert the unique identifier to base 62
    base62_result = encode(unique_number, BASE62)

    # Print the base 62 representation
    print("Base 62 Representation:", base62_result)

    return "Unique Number printed to console."




if __name__ == '__main__':
    app.run(debug=True)
