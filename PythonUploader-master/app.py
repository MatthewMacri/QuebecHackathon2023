from models import File, Session
from utils import allowed_file, generate_unique_number, encode
from bcryptmodule import encrypt, decrypt
from werkzeug.utils import secure_filename
from config import BASE62
from flask import Flask, jsonify, request, send_file
import io


app = Flask(__name__)


@app.route('/api/files', methods=['POST'])
def upload_file():
    uploaded_file = request.files.get('file')
    if uploaded_file and allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)
        file_data = uploaded_file.read()

        encrypted_data = encrypt("your_encryption_key", file_data)
        unique_number = generate_unique_number()
        base62_result = encode(unique_number, BASE62)

        session = Session()
        new_file = File(filename=filename, data=encrypted_data, base62_result=base62_result)
        session.add(new_file)
        session.commit()
        session.close()

        return jsonify({'message': 'File uploaded and encrypted successfully.'}), 201

    return jsonify({'message': 'File upload failed. Please check the file and try again.'}), 400


@app.route('/api/files', methods=['GET'])
def list_files():
    session = Session()
    files = session.query(File).all()
    return jsonify([file.id for file in files])


@app.route('/api/files/<int:file_id>', methods=['GET'])
def download_file(file_id):
    session = Session()
    file_record = session.query(File).filter_by(id=file_id).first()

    if file_record:
        decrypted_data = decrypt("your_encryption_key", file_record.data)
        return send_file(
            io.BytesIO(decrypted_data),
            as_attachment=True,
            download_name=file_record.filename
        )

    return jsonify({'message': 'File not found'}), 404


@app.route('/api/files/keyword/<string:keyword>', methods=['GET'])
def download_by_keyword(keyword):
    session = Session()
    file_record = session.query(File).filter_by(base62_result=keyword).first()

    if file_record:
        decrypted_data = decrypt("your_encryption_key", file_record.data)
        return send_file(
            io.BytesIO(decrypted_data),
            as_attachment=True,
            download_name=file_record.filename
        )

    return jsonify({'message': 'File not found for the specified keyword.'}), 404


@app.route('/api/serverinfo', methods=['GET'])
def server_info():
    unique_number = generate_unique_number()
    base62_result = encode(unique_number, BASE62)

    return jsonify({
        'unique_number': unique_number,
        'base62': base62_result
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001)
