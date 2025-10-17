"""
Script de teste para webhook Flask.

Testa o webhook localmente simulando requisições do Twilio.
"""

import requests
import sys
from config.colaboradores import COLABORADORES

# URL do webhook (assumindo que está rodando localmente)
# Porta 5001 (5000 é usada pelo AirPlay no macOS)
WEBHOOK_URL = "http://localhost:5001/webhook/whatsapp"
HEALTH_URL = "http://localhost:5001/health"


def test_health():
    """Testa endpoint de health check."""
    print("=" * 60)
    print("🏥 TESTANDO HEALTH CHECK")
    print("=" * 60)
    print()

    try:
        response = requests.get(HEALTH_URL, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK!")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor!")
        print("   Execute: python3 -m src.webhook.app")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_webhook_command(from_number: str, person_name: str, command: str):
    """
    Testa webhook com um comando específico.

    Args:
        from_number: Número do WhatsApp
        person_name: Nome da pessoa (para log)
        command: Comando a testar
    """
    print("=" * 60)
    print(f"🧪 TESTANDO COMANDO: '{command}'")
    print("=" * 60)
    print(f"De: {person_name} ({from_number})")
    print()

    # Simula payload do Twilio
    payload = {
        'From': from_number,
        'To': 'whatsapp:+14155238886',  # Twilio Sandbox
        'Body': command,
        'MessageSid': f'SM_TEST_{command.replace(" ", "_")}',
        'AccountSid': 'AC_TEST',
        'NumMedia': '0'
    }

    try:
        response = requests.post(WEBHOOK_URL, data=payload, timeout=30)

        print(f"Status Code: {response.status_code}")
        print()

        if response.status_code == 200:
            print("✅ Webhook respondeu com sucesso!")
            print()
            print("Resposta TwiML:")
            print("-" * 60)
            print(response.text)
            print("-" * 60)
        else:
            print(f"❌ Webhook retornou erro: {response.status_code}")
            print(response.text)

        return response.status_code == 200

    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor!")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def main():
    """Executa testes do webhook."""
    print()
    print("=" * 60)
    print("🧪 TESTE DE WEBHOOK - Sistema de Comandos")
    print("=" * 60)
    print()

    # Testa health primeiro
    if not test_health():
        print()
        print("⚠️  O servidor não está respondendo!")
        print("   Execute em outro terminal:")
        print("   python3 -m src.webhook.app")
        print()
        sys.exit(1)

    print()
    input("Pressione ENTER para continuar com os testes de comando...")
    print()

    # Pega Estevao Antunes para testes
    pessoa = "Estevao Antunes"
    telefone = COLABORADORES[pessoa]["telefone"]

    # Lista de comandos para testar
    comandos_teste = [
        ("ajuda", "Comando de ajuda"),
        ("minhas tarefas", "Listar tasks"),
        ("progresso", "Ver progresso"),
        ("andamento 1", "Marcar task 1 em andamento"),
    ]

    resultados = []

    for comando, descricao in comandos_teste:
        print()
        sucesso = test_webhook_command(telefone, pessoa, comando)
        resultados.append((comando, descricao, sucesso))

        print()
        input("Pressione ENTER para próximo teste...")

    # Resumo
    print()
    print("=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    print()

    sucessos = sum(1 for _, _, s in resultados if s)
    falhas = len(resultados) - sucessos

    for comando, descricao, sucesso in resultados:
        status = "✅" if sucesso else "❌"
        print(f"{status} {descricao}: '{comando}'")

    print()
    print(f"Total: {sucessos} sucessos, {falhas} falhas")
    print()

    if falhas == 0:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")

    print()


if __name__ == "__main__":
    main()
