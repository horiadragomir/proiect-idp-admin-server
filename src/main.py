from flask import Flask, jsonify, request
from mysql import connector

import time

app = Flask(__name__)

@app.route("/", methods=["GET"])
def wait_for_connection():
	return jsonify({"status": "OK"}), 200

@app.route("/trips", methods=["POST"])
def add_trip():
	# Se reseteaza conexiunea si obtine un cursor nou
	db.cmd_reset_connection()
	cursor = db.cursor()

	# Se obtine corpul cererii
	data = request.get_json()

	# Se insereaza o noua intrare in tabela 'trips'
	entry = (data["id"], data["src"], data["dst"], int(data["hour"]), int(data["day"]), int(data["trip_time"]), int(data["total_seats"]), 0, 0)
	try:
		cursor.execute("insert into trips values ('{}', '{}', '{}', {}, {}, {}, {}, {}, {}, false)".format(*entry))
	except:
		cursor.close()
		return jsonify({"status" : "[ERROR] Trip already exists"}), 400

	cursor.close()
	db.commit()

	return jsonify({"status" : "Trip has been added"}), 200

@app.route("/trips/<string:identifier>", methods=["DELETE"])
def cancel_trip(identifier):
	# Se reseteaza conexiunea si obtine un cursor nou
	db.cmd_reset_connection()
	cursor = db.cursor()

	# Calatoria exista in tabela 'trips'?
	cursor.execute("select id from trips where id = '{}'".format(identifier))
	if len(cursor.fetchall()) == 0:
		cursor.close()
		return jsonify({"status": "[ERROR] Trip doesn't exist"}), 400

	# Se anuleaza calatoria in tabela 'trips'
	cursor.execute("update trips set cancelled = true where id = '{}'".format(identifier))
	if cursor.rowcount == 0:
		cursor.close()
		return jsonify({"status": "Trip is already cancelled"}), 200

	cursor.close()
	db.commit()

	return jsonify({"status" : "Trip has been cancelled"}), 200

if __name__ == "__main__":
	# Conectarea la baza de date
	while True:
		try:
			db = connector.MySQLConnection(
				host="mysql",
				database="trains",
				user="admin",
				passwd="admin")
			break
		except:
			time.sleep(1)

	app.run(host="0.0.0.0", port=20000)
