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

# Route test
@app.get("/")
def index():
    return {"message": "TranspoBot API en ligne !"}

# Liste des véhicules
@app.get("/vehicules")
def get_vehicules():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicules")
    data = cursor.fetchall()
    conn.close()
    return data

# Liste des chauffeurs
@app.get("/chauffeurs")
def get_chauffeurs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chauffeurs")
    data = cursor.fetchall()
    conn.close()
    return data

# Liste des trajets
@app.get("/trajets")
def get_trajets():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM trajets")
    data = cursor.fetchall()
    conn.close()
    return data

# Chatbot IA
@app.post("/chat")
def chat(question: dict):
    user_question = question.get("question")
    
    schema = """
    Tables: vehicules(id, immatriculation, marque, modele, capacite, kilometrage, statut, date_mise_en_service),
    chauffeurs(id, nom, prenom, telephone, email, numero_permis, statut, date_embauche),
    lignes(id, numero, nom, depart, arrivee, distance_km),
    tarifs(id, ligne_id, type_passager, prix),
    trajets(id, vehicule_id, chauffeur_id, ligne_id, date_heure_depart, date_heure_arrivee, statut, nombre_passagers),
    incidents(id, trajet_id, type_incident, description, date_incident, gravite)
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"""Tu es un assistant SQL expert. 
            Génère uniquement des requêtes SELECT valides pour MySQL.
            Schema de la base: {schema}
            Réponds UNIQUEMENT avec la requête SQL, rien d'autre."""},
            {"role": "user", "content": user_question}
        ]
    )
    
    sql_query = response.choices[0].message.content.strip()
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        data = cursor.fetchall()
        conn.close()
        return {"question": user_question, "sql": sql_query, "resultat": data}
    except Exception as e:
        return {"erreur": str(e), "sql": sql_query}