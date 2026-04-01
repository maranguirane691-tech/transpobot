from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
from database import get_connection
import os

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {"message": "TranspoBot API en ligne !"}

@app.get("/vehicules")
def get_vehicules():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicules")
    data = cursor.fetchall()
    conn.close()
    return data

@app.get("/chauffeurs")
def get_chauffeurs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chauffeurs")
    data = cursor.fetchall()
    conn.close()
    return data

@app.get("/trajets")
def get_trajets():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM trajets ORDER BY date_heure_depart DESC LIMIT 10")
    data = cursor.fetchall()
    conn.close()
    return data

@app.get("/incidents")
def get_incidents():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM incidents")
    data = cursor.fetchall()
    conn.close()
    return data

@app.get("/lignes")
def get_lignes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lignes")
    data = cursor.fetchall()
    conn.close()
    return data

@app.post("/chat")
def chat(question: dict):
    user_question = question.get("question")
    
    schema = """
    Tables:
    - vehicules(id, immatriculation, type, capacite, statut, kilometrage, date_acquisition)
    - chauffeurs(id, nom, prenom, telephone, numero_permis, categorie_permis, disponibilite, vehicule_id, date_embauche)
    - lignes(id, code, nom, origine, destination, distance_km, duree_minutes)
    - tarifs(id, ligne_id, type_client, prix)
    - trajets(id, ligne_id, chauffeur_id, vehicule_id, date_heure_depart, date_heure_arrivee, statut, nb_passagers, recette)
    - incidents(id, trajet_id, type, description, gravite, date_incident, resolu)
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1000,
        messages=[
            {"role": "system", "content": f"""Tu es un assistant SQL expert.
            Génère uniquement des requêtes SELECT valides pour MySQL.
            Schema de la base: {schema}
            Réponds UNIQUEMENT avec la requête SQL, rien d'autre."""},
            {"role": "user", "content": user_question}
        ]
    )
    
    sql_query = response.choices[0].message.content.strip()
    sql_query = sql_query.replace("sql", "").replace("", "").strip()
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        data = cursor.fetchall()
        conn.close()
        return {"question": user_question, "sql": sql_query, "resultat": data}
    except Exception as e:
        return {"erreur": str(e), "sql": sql_query}