from flask import Flask, jsonify, request
from mysql import connector

import time

app = Flask(__name__)

@app.route("/", methods=["GET"])
def wait_for_connection():
	return jsonify({"status": "OK"})

@app.route("/login", methods=["GET"])
def login_admin():
	# Se reseteaza conexiunea si obtine un cursor nou
	db.cmd_reset_connection()
	cursor = db.cursor()

	username = request.args.get("username");

	cursor.execute("select password, first_name, last_name from admins where username = '{}'".format(username));

	login_info = cursor.fetchall();

	cursor.close()

	return jsonify({"status": login_info})

@app.route("/view", methods=["GET"])
def view_trips():
	# Se reseteaza conexiunea si obtine un cursor nou
	db.cmd_reset_connection()
	cursor = db.cursor()

	src = request.args.get("src")
	dst = request.args.get("dst")
	departureDay = request.args.get("departure_day")
	status = request.args.get("status")

	append_status = ""

	if status == "Activ":
		append_status = "and cancelled = false"	
	elif status == "Anulat":
		append_status = "and cancelled = true"

	if departureDay == "%":
		cursor.execute("select * from trips where src like '{}' and dst like '{}'".format(src, dst) + append_status);
	else:
		cursor.execute("select * from trips where src like '{}' and dst like '{}' and day = {}".format(src, dst, int(departureDay)) + append_status);

	trips_info = cursor.fetchall()

	cursor.close()

	return jsonify({"status": trips_info})

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
		return jsonify({"status" : "[EROARE] Calatoria cu ID-ul \'{}\' exista deja in baza de date!".format(data["id"])})

	cursor.close()
	db.commit()

	return jsonify({"status" : "Calatoria cu ID-ul \'{}\' a fost adaugata cu succes.".format(data["id"])})

@app.route("/trips/<string:identifier>", methods=["DELETE"])
def cancel_trip(identifier):
	# Se reseteaza conexiunea si obtine un cursor nou
	db.cmd_reset_connection()
	cursor = db.cursor()

	# Calatoria exista in tabela 'trips'?
	cursor.execute("select id from trips where id = '{}'".format(identifier))
	if len(cursor.fetchall()) == 0:
		cursor.close()
		return jsonify({"status" : "[EROARE] Calatoria cu ID-ul \'{}\' nu exista in baza de date!".format(identifier)})

	# Se anuleaza calatoria in tabela 'trips'
	cursor.execute("update trips set cancelled = true where id = '{}'".format(identifier))
	if cursor.rowcount == 0:
		cursor.close()
		return jsonify({"status" : "[EROARE] Calatoria cu ID-ul \'{}\' este deja anulata!".format(identifier)})

	cursor.close()
	db.commit()

	return jsonify({"status" : "Calatoria cu ID-ul \'{}\' a fost anulata.".format(identifier)})

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

	app.run(host="0.0.0.0", port=20001)
