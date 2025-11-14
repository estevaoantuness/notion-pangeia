#!/usr/bin/env python3
"""
Adicionar Arthur e Julio ao banco de dados de usuários
"""

from dotenv import load_dotenv
load_dotenv()

from src.database.connection import get_db_engine
from sqlalchemy import text

print("=" * 100)
print("➕ ADICIONANDO ARTHUR E JULIO AO BANCO DE DADOS")
print("=" * 100)
print()

engine = get_db_engine()

# Dados
usuarios = [
    {
        "name": "Arthur Leuzzi",
        "phone": "55 48 8842-8246"
    },
    {
        "name": "Julio Inoue",
        "phone": "55 11 99932-2027"
    }
]

with engine.connect() as conn:
    for user in usuarios:
        # Verificar se já existe
        result = conn.execute(
            text("SELECT id FROM users WHERE name = :name"),
            {"name": user["name"]}
        )
        existing_id = result.scalar()

        if existing_id:
            print(f"⚠️  {user['name']} já existe (ID: {existing_id})")
        else:
            # Inserir
            result = conn.execute(
                text("""
                    INSERT INTO users (name, phone, onboarding_complete)
                    VALUES (:name, :phone, FALSE)
                    RETURNING id
                """),
                {"name": user["name"], "phone": user["phone"]}
            )
            new_id = result.scalar()
            conn.commit()
            print(f"✅ {user['name']} adicionado (ID: {new_id})")

print()
print("=" * 100)
print("✅ CONCLUÍDO")
print("=" * 100)
print()
print("Agora execute: python3 test_arthur_julio_checkins.py")
