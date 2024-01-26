from flask import Flask, jsonify, request, Response
from pymongo import MongoClient
from bson import json_util, ObjectId
import json

from dotenv import load_dotenv
import os

load_dotenv()
mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING')

app = Flask(__name__)

# Crie uma conexão com o MongoDB Atlas
client = MongoClient(mongo_connection_string)

# Selecione o banco de dados
db = client['tinder2']

# Selecione a coleção
usuarios = db['usuarios']

@app.route('/usuarios', methods=['GET'])
def obter_usuarios():
    usuarios_list = list(usuarios.find())
    return Response(json.dumps(usuarios_list, default=json_util.default), mimetype='application/json')

@app.route('/usuario/<string:id>', methods=['GET'])
def obter_usuario_id(id):
    usuario = usuarios.find_one({'_id': ObjectId(id)})
    if usuario:
        return Response(json.dumps(usuario, default=json_util.default), mimetype='application/json')

@app.route('/usuario/<string:id>', methods=['PUT'])
def editar_usuario(id):
    usuario_editado = request.get_json()
    usuarios.update_one({'_id': ObjectId(id)}, {'$set': usuario_editado})
    return Response(json.dumps(usuarios.find_one({'_id': ObjectId(id)}), default=json_util.default), mimetype='application/json')

@app.route('/usuarios', methods=['POST'])   
def adicionar_usuario():
    novo_usuario = request.get_json()
    resultado = usuarios.insert_one(novo_usuario)
    return Response(json.dumps({'_id': str(resultado.inserted_id)}), mimetype='application/json')
    
@app.route('/usuario/<string:id>', methods=['DELETE'])    
def excluir_usuario(id):
    usuarios.delete_one({'_id': ObjectId(id)})
    usuarios_list = list(usuarios.find())
    return Response(json.dumps(usuarios_list, default=json_util.default), mimetype='application/json')