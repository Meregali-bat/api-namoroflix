from flask import Flask, jsonify, request, Response
from pymongo import MongoClient
from bson import json_util, ObjectId
import json

from flask_cors import CORS, cross_origin

from dotenv import load_dotenv
import os

load_dotenv()
mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING')

app = Flask(__name__)

CORS(app)

client = MongoClient(mongo_connection_string)

db = client['tinder2-testes']

usuarios = db['usuarios']

@cross_origin
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

@app.route('/cadastrar', methods=['POST'])   
def adicionar_usuario():
    novo_usuario = request.get_json()
    novo_usuario['likes'] = []
    novo_usuario['matches'] = []
    resultado = usuarios.insert_one(novo_usuario)
    
    if resultado.inserted_id is not None:
        return Response(json.dumps({'success': True, '_id': str(resultado.inserted_id)}), mimetype='application/json')
    else:
        return Response(json.dumps({'success': False, 'message': 'Falha ao cadastrar o usuário'}), mimetype='application/json', status=400)
    
@app.route('/usuario/<string:id>', methods=['DELETE'])    
def excluir_usuario(id):
    usuarios.delete_one({'_id': ObjectId(id)})
    usuarios_list = list(usuarios.find())
    return Response(json.dumps(usuarios_list, default=json_util.default), mimetype='application/json')

@cross_origin
@app.route('/autenticar', methods=['POST'])
def autenticar_usuario():
    credenciais = request.get_json()
    usuario = usuarios.find_one({'email': credenciais['email'], 'senha': credenciais['senha']})
    if usuario:
        usuario['_id'] = str(usuario['_id'])
        usuario.pop('senha', None)
        return jsonify(success=True, usuario=usuario)
    else:
        return jsonify(success=False, error='Usuário ou senha inválidos'), 401

@app.route('/usuario/<string:id>/like', methods=['POST'])
def dar_like(id):
    id_like = request.get_json()['id_like']
    
    usuarios.update_one({'_id': ObjectId(id)}, {'$addToSet': {'likes': id_like}})
    
    usuario_like = usuarios.find_one({'_id': ObjectId(id_like)})
    if usuario_like and 'likes' in usuario_like and id in usuario_like['likes']:
        usuarios.update_one({'_id': ObjectId(id)}, {'$addToSet': {'matches': id_like}})
        usuarios.update_one({'_id': ObjectId(id_like)}, {'$addToSet': {'matches': id}})
        return jsonify(success=True, message='Match!')
    
    return jsonify(success=True, message='Like enviado')

@app.route('/usuario/<string:id>/matches', methods=['GET'])
def obter_matches(id):
    usuario = usuarios.find_one({'_id': ObjectId(id)})
    matches = [{'_id': str(match['_id']), 'nome': match['nome'], 'idade': match['idade'], 'imagem': match['imagem']} for id_match in usuario['matches'] for match in usuarios.find({'_id': ObjectId(id_match)})]
    return jsonify(matches)


@app.route('/usuario/<string:id>/sem-match', methods=['GET'])
def obter_usuarios_sem_match(id):
    usuario = usuarios.find_one({'_id': ObjectId(id)})
    matches_ids = [ObjectId(id_match) for id_match in usuario['matches']]
    usuarios_list = list(usuarios.find({'_id': {'$ne': ObjectId(id), '$nin': matches_ids}}))
    usuarios_list = [{key: (str(value) if isinstance(value, ObjectId) else value) for key, value in usuario.items()} for usuario in usuarios_list]
    return jsonify(usuarios_list)

@app.route('/usuarios/sem-imagem', methods=['DELETE'])
def apagar_usuarios_sem_imagem():
    resultado = usuarios.delete_many({'imagem': {'$in': [None, '']}})
    return jsonify(success=True, message=f'{resultado.deleted_count} usuários apagados')

@app.route('/usuario/<string:id>/remover-duplicados', methods=['PUT'])
def remover_duplicados(id):
    usuario = usuarios.find_one({'_id': ObjectId(id)})
    if usuario:
        likes_unicos = list(set(usuario.get('likes', [])))
        matches_unicos = list(set(usuario.get('matches', [])))
        usuarios.update_one({'_id': ObjectId(id)}, {'$set': {'likes': likes_unicos, 'matches': matches_unicos}})
        return jsonify(success=True, message='Likes e matches duplicados removidos')
    else:
        return jsonify(success=False, message='Usuário não encontrado')

# app.run(port=5000, host="localhost", debug=True)