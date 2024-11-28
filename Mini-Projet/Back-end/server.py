from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# Initialiser l'application Flask et SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://youssef:Tounes_12@minipro.mysql.database.azure.com/devopsminiprojet'  # Remplace par tes paramètres DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Définir le modèle de données correspondant à ta table 'students'
class Students(db.Model):
    __tablename__ = 'students'

    # Remplacer par la colonne qui agit comme clé primaire
    rentree_scolaire = db.Column(db.String(50), primary_key=True)
    region_academique = db.Column(db.String(50))
    academie = db.Column(db.String(50))
    departement = db.Column(db.String(50))
    commune = db.Column(db.String(50))
    denomination_complete = db.Column(db.String(100))
    nombre_filles = db.Column(db.Integer)
    nombre_garcons = db.Column(db.Integer)

# Route pour rendre la page HTML avec les filtres
@app.route('/')
def index():
    columns = ['rentree_scolaire', 'region_academique', 'academie', 'departement', 'commune', 'denomination_complete']
    distinct_values = {}
    
    for column in columns:
        distinct_values[column] = get_distinct_values_from_db(column)

    return render_template('index.html', distinct_values=distinct_values)

# Fonction pour récupérer les valeurs distinctes d'une colonne
def get_distinct_values_from_db(column_name):
    distinct_values = db.session.query(getattr(Students, column_name)).distinct().all()
    return [val[0] for val in distinct_values]

# Route pour obtenir les valeurs distinctes d'une colonne spécifique (API)
@app.route('/distinct_values', methods=['GET'])
def get_distinct_values():
    column_name = request.args.get('column')

    if not column_name:
        return jsonify({'error': 'Le paramètre "column" est requis'}), 400

    if not hasattr(Students, column_name):
        return jsonify({'error': f'La colonne "{column_name}" n\'existe pas dans la base de données'}), 400

    distinct_values = db.session.query(getattr(Students, column_name)).distinct().all()
    return jsonify([val[0] for val in distinct_values])

# Route pour effectuer une recherche avec des clauses WHERE (API)
@app.route('/search', methods=['GET'])
def search_data():
    filters = request.args

    # Construction de la requête pour COUNT et SUM
    query = db.session.query(
        db.func.sum(Students.nombre_filles).label("total_girls"),
        db.func.sum(Students.nombre_garcons).label("total_boys")
    )

    # Ajout dynamique des clauses WHERE
    for column, value in filters.items():
        if value:  # Si une valeur est spécifiée
            column_attr = getattr(Students, column, None)
            if column_attr is not None:  # Vérifier que la colonne existe
                query = query.filter(column_attr.ilike(f"%{value}%"))

    # Exécution de la requête
    result = query.one()
    print(result)

    # Préparation de la réponse JSON
    response = {
        "total_students": (result.total_girls or 0) + (result.total_boys or 0),
        "total_girls": result.total_girls or 0,
        "total_boys": result.total_boys or 0
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
