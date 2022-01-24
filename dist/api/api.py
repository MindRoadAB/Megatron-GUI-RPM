import database
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/api/organization", methods = ['GET', 'POST'])
def list_organizations():
    try:
        if request.method == 'GET':
            return jsonify(database.list_organizations())
        elif request.method == 'POST':
            return database.add_organization(request.get_json())
    except Exception as e:
        return str(e), 500


@app.route("/api/organization/<org_id>", methods = ['GET', 'POST', 'DELETE'])
def get_organization(org_id):
    try:
        if request.method == 'GET':
            return jsonify(database.get_organization(int(org_id)))
        elif request.method == 'POST':
            return jsonify(database.update_organization(org_id, request.get_json()))
        elif request.method == 'DELETE':
            database.delete_organization(org_id)
            return jsonify(success=True)
    except Exception as e:
        return str(e), 500


@app.route("/api/table/<table_name>", methods = ['GET'])
def dump_table(table_name):
    try:
        return jsonify(database.dump_table(table_name))
    except Exception as e:
        return str(e), 500
