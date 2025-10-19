#!/usr/bin/env python3
"""
Teste do Sistema de Alertas Automáticos.

Mostra como as mensagens fracionadas ficam.
NÃO envia de verdade (dry_run=True).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.notion.tasks import TasksManager
from src.coordination.team_coordinator import TeamCoordinator
from src.coordination.auto_alerter import AutoAlerter

def main():
    print("=" * 80)
    print("📱 TESTE DE ALERTAS AUTOMÁTICOS - MODO DRY RUN")
    print("=" * 80)
    print()

    # Inicializa
    print("🔧 Inicializando componentes...")
    tasks_manager = TasksManager()
    team_coordinator = TeamCoordinator(tasks_manager=tasks_manager)
    auto_alerter = AutoAlerter(
        team_coordinator=team_coordinator,
        whatsapp_sender=None  # None = não envia de verdade
    )
    print("✅ Componentes prontos!\n")

    # Executa verificação (dry run)
    print("=" * 80)
    print("🔍 VERIFICANDO ALERTAS (DRY RUN - NÃO ENVIA DE VERDADE)")
    print("=" * 80)
    print()

    stats = auto_alerter.check_and_send_alerts(dry_run=True)

    print()
    print("=" * 80)
    print("📊 ESTATÍSTICAS")
    print("=" * 80)
    print(f"🚨 Críticos: {stats['critical']}")
    print(f"⚡ Importantes: {stats['high']}")
    print(f"📌 Médios: {stats['medium']}")
    print(f"👥 Para: {stats['people']} pessoas")
    print(f"✅ Enviados (dry run): {stats['sent']}")

    print()
    print("=" * 80)
    print("🧪 TESTE DE MENSAGENS ESPECÍFICAS")
    print("=" * 80)
    print()

    # Teste 1: Resumo do time
    print("\n--- Teste 1: Resumo do Time ---")
    auto_alerter.send_team_summary(
        target_person="Saraiva",
        dry_run=True
    )

    # Teste 2: Insights da pessoa
    print("\n--- Teste 2: Insights do Saraiva ---")
    auto_alerter.send_person_insights(
        target_person="Saraiva",
        about_person="Saraiva",
        dry_run=True
    )

    # Teste 3: Insights de outra pessoa
    print("\n--- Teste 3: Insights do Julio (enviado pro Saraiva) ---")
    auto_alerter.send_person_insights(
        target_person="Saraiva",
        about_person="Julio",
        dry_run=True
    )

    print()
    print("=" * 80)
    print("✅ TESTE COMPLETO!")
    print("=" * 80)
    print()
    print("💡 Para enviar de verdade:")
    print("   1. Configure WhatsAppSender no auto_alerter")
    print("   2. Chame check_and_send_alerts(dry_run=False)")
    print()

if __name__ == "__main__":
    main()
