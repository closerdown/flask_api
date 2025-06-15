from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # CORS 허용

# 직접 JSON 딕셔너리로 Firebase 서비스 계정 정보 넣기
firebase_info = {
    "type": "service_account",
    "project_id": "capstoneappstore",
    "private_key_id": "297406c5770c72af04366e721317c64762a329a7",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCvl9Tdr43JLARt
gNGmmbDM7cJ1Yu5dHkIBr+49a3xvHkr6Hgn9v4EWe9qNHnmQQ06oL0GMLbDlmNVW
maPon0uxlRKs0fO7WOy/6NPdi31UBcmaYx4ARCGf68JV1iz8waXnwy8E0vMBzZ5e
GJgPZ4ZyLpesaRiGz+TxUJib7sY2YfgZG2hAZaNAuwbEgGj5N8OOxCkVN1u0cahT
SETTuCFOLpx+HpwSGuCvBaM1SjhT17ltOVSH98QTPeCtnc8oU+UgKbbbEFnRxyje
Nea3a7AB90CxIPKogSF5aiB6YzzNAkrvKfpjo14W2dGSPtW0ZYBDWZD1FAgDPMhx
ihJzV4+DAgMBAAECggEAKK600ufpocJhBD3kVQUmwVQUyb2yHED2ag2o1PIiUlxi
YrCy/+dusRbg+/EjmRj/EFhih2fOpGNUikvufebqUqqHOSMrpSxlLdFzxNCcqOru
Wqa8PLOMVtD4pYqJwcXb+mZubl+xjalmF8b69Ba4P5wr5/YxiIqCMKbLtNUNd2u4
V8CYaoOPIY+9wu/Mi1gPD49n5CEgpqpXKNyofYlO1VT39YUhgtyWQGJUW3fWEvtM
WSZG0HLIxZOro+Ub7zg3xYz2b4YTuqg/uuNZ6ejiUDja66IIemfoQ1+XcljuYgfZ
Y2jaCgS3xZF/7PqtqeMwvO+uZGskifggdWxnOjpBAQKBgQDwlS42ALyZRYqIYpyt
YhOqxqFua2VCC2k07z5haTwIkCeeTOU3lfVMvXpeP+6FiBRD3yVyxBev9rEI9LV5
GQGOGi2sl2i2MMYE6zAi8zX5JM3HSdMWivpCP+6Lrl9yL9YGF8nkavT8ijss19Tb
hMCC3vnBYKy19ZMlctRUgcPUSQKBgQC62HrQ8tjkqxcl21JXl5pYUO27JK2aNArq
TMZtFxltMwm8dt7nuN/TqEuG0QFNuWWYR1teR5/9lKb9F09i72uUS8Wd4YWYSWap
90lklpLYKQuc75VGusn/IrDPkkfCERBKlg5kbCiNE5ypnAW3v65Aj0I3XgWEaW+7
lY6u/sUtawKBgGLyWCEpyGeZbFKPjDTbI4+XRgmt7eVt4AU/aH6T03cKIuE+av+j
k1HOlCdzT9xnjT4k5rf+4mcipMk0K/b0S+lv5t0XIJ/eC3M2b4PQV6ByfJe8Sy74
VdkthiS4wNSry/CRlB13x+6dw5y73/Ww8aRhpILeCeqEZ9J9Gcrv2+TRAoGBAKXB
vtL3XesezR5Mf7QtTkPjJ8PKOih+2uAY1D+bKndxu8VyPzWbERYYS0iCyoFFZBe/
1hLBv/GamroUn9zJQcsBnYL+uyHqnCVUt8uAuS0C3MaQ1QE2XFT3VZwPzZEgyi8h
CAuW2DKvn1/ohjoI1nF3peqwgnyBfRoRB8+/PPWZAoGBAOPkqpiAhMZ/rXNx/Lns
Mox6SlNHH+nLg1uFZkr267bbyCNBpqDeV42fZ8OsP2m8VjyLrEsahkWzawdTvgdr
v3g6rp3hYkHMrHQpvfPsW9xtb3kdeclr+BR9cfnoubt3qlFYRhYtyHkp4ou722MU
NNSv3fLt3zTRcvzDVdCfMNaB
-----END PRIVATE KEY-----""",
    "client_email": "firebase-adminsdk-fbsvc@capstoneappstore.iam.gserviceaccount.com",
    "client_id": "113665010845116994866",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40capstoneappstore.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_info)
    firebase_admin.initialize_app(cred)

db = firestore.client()

USER_ID = "anonymous_user"

# API: 즐겨찾기 조회
@app.route("/favorites", methods=["GET"])
def get_favorites():
    doc = db.collection("favorites").document(USER_ID).get()
    favorites = doc.to_dict().get("favorite_buses", []) if doc.exists else []
    return jsonify({"favorites": favorites})

# API: 즐겨찾기 추가
@app.route("/favorites", methods=["POST"])
def add_favorite():
    bus_no = request.json.get("bus_no")
    if not bus_no:
        return jsonify({"error": "bus_no is required"}), 400

    ref = db.collection("favorites").document(USER_ID)
    doc = ref.get()
    favorites = doc.to_dict().get("favorite_buses", []) if doc.exists else []

    if bus_no not in favorites:
        favorites.append(bus_no)
        ref.set({"favorite_buses": favorites})

    return jsonify({"favorites": favorites})

# API: 즐겨찾기 삭제
@app.route("/favorites/<bus_no>", methods=["DELETE"])
def remove_favorite(bus_no):
    ref = db.collection("favorites").document(USER_ID)
    doc = ref.get()
    if doc.exists:
        favorites = doc.to_dict().get("favorite_buses", [])
        if bus_no in favorites:
            favorites.remove(bus_no)
            ref.set({"favorite_buses": favorites})
    return jsonify({"favorites": favorites})

# API: 최신 혼잡도 조회
@app.route("/congestion/<bus_no>", methods=["GET"])
def get_congestion(bus_no):
    try:
        docs = db.collection("bus_congestion")\
            .where("bus_number", "==", bus_no)\
            .order_by("timestamp", direction=firestore.Query.DESCENDING)\
            .limit(1).stream()
        doc = next(docs, None)
        if doc:
            data = doc.to_dict()
            data["timestamp"] = data["timestamp"].to_datetime().isoformat()
            return jsonify(data)
        else:
            return jsonify({"error": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: 혼잡도 히스토리 (24시간 기본)
@app.route("/congestion_history/<bus_no>", methods=["GET"])
def get_congestion_history(bus_no):
    hours = int(request.args.get("hours", 24))
    try:
        threshold = datetime.utcnow() - timedelta(hours=hours)
        docs = db.collection("bus_congestion")\
            .where("bus_number", "==", bus_no)\
            .where("timestamp", ">=", threshold)\
            .order_by("timestamp")\
            .stream()
        history = []
        for d in docs:
            d_dict = d.to_dict()
            history.append({
                "timestamp": d_dict["timestamp"].to_datetime().isoformat(),
                "total_congestion": d_dict.get("total_congestion", 0)
            })
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: 전체 정류장 조회
@app.route("/stations", methods=["GET"])
def get_stations():
    try:
        stations = []
        docs = db.collection("bus_stations").stream()
        for d in docs:
            d_dict = d.to_dict()
            stations.append({
                "name": d_dict.get("정류장명"),
                "lat": float(d_dict.get("위도", 0)),
                "lon": float(d_dict.get("경도", 0))
            })
        return jsonify(stations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
