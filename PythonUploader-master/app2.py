import connexion
import io
from werkzeug.utils import secure_filename
from models import File, Session
from utils import allowed_file, generate_unique_number, encode
from bcryptmodule import encrypt, decrypt
from config import BASE62
from flask import request, send_file, jsonify

from utils import allowed_file, generate_unique_number, encode  # Import functions from utils.py
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URI, BASE62, ALLOWED_EXTENSIONS  # Import variables from config.py
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
import io
from bcryptmodule import encrypt, decrypt


def upload_file():
    uploaded_file = request.files.get('file')
    encryption_key = request.form.get('encryption_key')

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
        return jsonify(message=message), 201

    message = 'File upload failed. Please check the file and try again.'
    return jsonify(message=message), 400


def list_files():
    session = Session()
    files = session.query(File).all()
    session.close()

    file_list = []
    for file in files:
        file_list.append({
            'id': file.id,
            'filename': file.filename,
            'base62_result': file.base62_result
        })

    return {'files': file_list}


def download_file(file_id):
    session = Session()
    file_record = session.query(File).filter_by(id=file_id).first()
    session.close()

    if file_record:
        decrypted_data = decrypt("your_encryption_key", file_record.data)
        return send_file(
            io.BytesIO(decrypted_data),
            as_attachment=True,
            download_name=file_record.filename
        )
    return jsonify(message='File not found'), 404


def download_by_keyword():
    keyword = request.form['keyword']
    encryption_key = request.form['encryption_key']

    session = Session()
    file_record = session.query(File).filter_by(base62_result=keyword).first()


    if file_record:
        try:
            decrypted_data = decrypt(encryption_key, file_record.data)
            return send_file(
                io.BytesIO(decrypted_data),
                as_attachment=True,
                download_name=file_record.filename
            )
        except:
            # This handles potential decryption errors due to incorrect keys or other issues.
            return jsonify(message="Decryption failed. Possibly wrong encryption key."), 400

    return jsonify(message='File not found for the specified keyword.'), 404


def server_info():
    unique_number = generate_unique_number()
    base62_result = encode(unique_number, BASE62)
    return {
        'unique_number': unique_number,
        'base62': base62_result
    }


app = connexion.App(__name__, specification_dir='./')
app.add_api('swagger.yaml')

if __name__ == '__main__':
    app.run(port=5001)
