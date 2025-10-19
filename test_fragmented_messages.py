#!/usr/bin/env python3
"""
Teste específico de mensagens fracionadas.
Mostra exatamente como as mensagens ficam.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.notion.tasks import TasksManager
from src.coordination.team_coordinator import TeamCoordinator
from src.coordination.connection_detector import ConnectionDetector
from src.coordination.collaboration_recommender import CollaborationRecommender
from src.coordination.message_fragmenter import MessageFragmenter

def print_messages(title, messages):
    """Imprime mensagens de forma bonita."""
    print(f"\n{'='*80}")
    print(f"📱 {title}")
    print('='*80)

    for i, msg_data in enumerate(messages, 1):
        delay = msg_data['delay_seconds']
        text = msg_data['text']

        print(f"\nMensagem {i}/{len(messages)}:", end="")
        if delay > 0:
            print(f" (espera {delay:.1f}s)")
        else:
            print()

        print("┌" + "─" * 78 + "┐")
        for line in text.split('\n'):
            print(f"│ {line:<76} │")
        print("└" + "─" * 78 + "┘")

def main():
    print("=" * 80)
    print("📱 TESTE DE MENSAGENS FRACIONADAS")
    print("=" * 80)

    # Inicializa
    tasks_manager = TasksManager()
    team_coordinator = TeamCoordinator(tasks_manager=tasks_manager)
    connection_detector = ConnectionDetector(team_coordinator)
    collab_recommender = CollaborationRecommender(connection_detector)
    fragmenter = MessageFragmenter()

    # Sync
    print("\n🔄 Sincronizando...")
    team_coordinator.sync_all()

    # Gera recomendações
    print("💡 Gerando recomendações...")
    all_recs = collab_recommender.generate_all_recommendations()

    # Filtra só as do Saraiva
    saraiva_recs = [r for r in all_recs if r.target_person == "Saraiva"]
    print(f"✅ Encontradas {len(saraiva_recs)} recomendações para Saraiva\n")

    # Mostra cada tipo de mensagem
    shown_types = set()

    for rec in saraiva_recs:
        if rec.action_type in shown_types:
            continue

        shown_types.add(rec.action_type)

        # Fragmenta
        messages = fragmenter.fragment_recommendation(rec)
        messages_with_delay = fragmenter.add_delays_between_messages(messages)

        # Mostra
        title = f"{rec.action_type.upper()} - Prioridade: {rec.priority.value.upper()}"
        print_messages(title, messages_with_delay)

        if len(shown_types) >= 5:  # Mostra no máximo 5 tipos
            break

    # Mostra resumo do time
    print("\n\n" + "=" * 80)
    print("EXEMPLO: RESUMO DO TIME")
    print("=" * 80)

    messages = []
    messages.append("Oi Saraiva! Aqui vai um resumo do time 📊")
    messages.append("Temos 13 pessoas trabalhando em 8 projetos")
    messages.append("Tasks: 10 em andamento, 37 a fazer, 18 concluídas")
    messages.append("⚠️ 2 pessoas tão sobrecarregadas (workload >70%)")
    messages.append("Workload médio do time: 38%")

    messages_with_delay = fragmenter.add_delays_between_messages(messages)
    print_messages("RESUMO DO TIME", messages_with_delay)

    print("\n\n" + "=" * 80)
    print("✅ TESTE COMPLETO!")
    print("=" * 80)
    print("\n💬 Assim ficam as mensagens no WhatsApp:")
    print("   • 2-5 mensagens por insight")
    print("   • Tom natural e humano")
    print("   • Delays entre mensagens (simula digitação)")
    print("   • Emojis usados com moderação\n")

if __name__ == "__main__":
    main()
