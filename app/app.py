from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import os

app = Flask(__name__)

# Charger les modèles
BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE, '..', 'data', 'models')
modele_appart = joblib.load(os.path.join(MODEL_DIR, 'model_appartement_v1.joblib'))
modele_maison = joblib.load(os.path.join(MODEL_DIR, 'model_maison_v1.joblib'))

FEATURES = [
    'surface_reelle_bati',
    'nombre_pieces_principales',
    'surface_terrain',
    'dept_num',
    'longitude',
    'latitude',
    'annee',
    'trimestre',
    'prix_m2_ref_zone'
]

# Prix de référence par département
PRIX_REF = {
    (75, 'Appartement'): 9500,
    (75, 'Maison'):      8000,
    (92, 'Appartement'): 6500,
    (92, 'Maison'):      5500,
    (94, 'Appartement'): 4200,
    (94, 'Maison'):      3800,
}


def get_coordonnee(dept):
    coords = {75: (2.35, 48.85), 92: (2.25, 48.85), 94: (2.45, 48.78)}
    return coords.get(int(dept), (2.35, 48.85))


def normalize_payload(payload):
    if not isinstance(payload, dict):
        return None, 'Le corps de la requête doit être un objet JSON valide.'

    required_fields = ['type_bien', 'surface', 'pieces', 'departement']
    missing = [field for field in required_fields if field not in payload or payload[field] in (None, '')]
    if missing:
        return None, 'Les champs type de bien, surface, pièces et département sont requis.'

    try:
        type_bien = payload['type_bien']
        if type_bien not in {'Appartement', 'Maison'}:
            raise ValueError('Le type de bien doit être Appartement ou Maison.')

        surface = float(payload['surface'])
        pieces = int(payload['pieces'])
        terrain = float(payload.get('terrain', 0) or 0)
        dept = int(payload['departement'])
    except (TypeError, ValueError):
        return None, 'Les champs surface, pièces et département doivent être des valeurs numériques valides.'

    if surface <= 0:
        return None, 'La surface doit être supérieure à 0 m².'
    if pieces <= 0:
        return None, 'Le nombre de pièces doit être supérieur à 0.'
    if dept not in {75, 92, 94}:
        return None, 'Le département doit être l’un des départements disponibles : 75, 92 ou 94.'
    if type_bien == 'Maison' and terrain < 0:
        return None, 'La surface du terrain ne peut pas être négative.'

    return {
        'type_bien': type_bien,
        'surface': surface,
        'pieces': pieces,
        'terrain': terrain,
        'departement': dept,
    }, None


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/estimer')
def estimate():
    return render_template('estimate.html')


@app.get('/a-propos')
def about():
    return render_template('about.html')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(silent=True)
    payload, error = normalize_payload(data)
    if error:
        return jsonify({'error': error}), 400

    type_bien = payload['type_bien']
    surface = payload['surface']
    pieces = payload['pieces']
    terrain = payload['terrain']
    dept = payload['departement']
    lon, lat = get_coordonnee(dept)
    prix_ref = PRIX_REF.get((dept, type_bien), 5000)

    X = pd.DataFrame([[
        surface,
        pieces,
        terrain,
        dept,
        lon,
        lat,
        2024,
        3,
        prix_ref,
    ]], columns=FEATURES)

    modele = modele_appart if type_bien == 'Appartement' else modele_maison
    prix = float(modele.predict(X)[0])

    return jsonify({
        'prix_estime': round(prix, 0),
        'prix_m2': round(prix / surface, 0),
        'type_bien': type_bien,
        'version': 'v1'
    })


@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'version': 'v1'})


@app.errorhandler(404)
def not_found(_error):
    return render_template('error.html', code=404, message='La page demandée est introuvable.'), 404


@app.errorhandler(500)
def internal_error(_error):
    return render_template('error.html', code=500, message='Une erreur interne est survenue lors du traitement de la demande.'), 500


if __name__ == '__main__':
    print('Application demarree !')
    print('Ouvre ton navigateur sur : http://localhost:5000')
    app.run(host='0.0.0.0', debug=True, port=5000)
