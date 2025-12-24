from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import psycopg2
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# =====================
# CONFIGURAÇÕES
# =====================
DATA_INICIO = date(2025, 1, 10)

DATABASE_URL = os.getenv("DATABASE_URL")

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# =====================
# BANCO DE DADOS
# =====================
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def criar_tabela():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id SERIAL PRIMARY KEY,
            data DATE NOT NULL,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            foto_url TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

criar_tabela()

# =====================
# ROTAS
# =====================
@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM eventos ORDER BY data ASC")
    eventos = cur.fetchall()
    cur.close()
    conn.close()

    dias_juntos = (date.today() - DATA_INICIO).days

    return render_template(
        "index.html",
        eventos=eventos,
        dias_juntos=dias_juntos
    )

@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if request.method == "POST":
        data = request.form["data"]
        titulo = request.form["titulo"]
        descricao = request.form["descricao"]
        foto = request.files["foto"]

        foto_url = None
        if foto and foto.filename != "":
            upload = cloudinary.uploader.upload(foto)
            foto_url = upload["secure_url"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO eventos (data, titulo, descricao, foto_url)
            VALUES (%s, %s, %s, %s)
            """,
            (data, titulo, descricao, foto_url)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))

    return render_template("adicionar.html")

# =====================
# START
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)