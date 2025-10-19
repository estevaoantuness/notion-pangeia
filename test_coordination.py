#!/usr/bin/env python3
"""
Teste do Sistema de Coordenação Inteligente.

Mostra:
- Todas as pessoas e seus workloads
- Todos os projetos
- Conexões detectadas
- Recomendações de colaboração
- Insights específicos pro Saraiva
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.notion.tasks import TasksManager
from src.coordination.team_coordinator import TeamCoordinator
from src.coordination.connection_detector import ConnectionDetector
from src.coordination.collaboration_recommender import CollaborationRecommender

def main():
    print("=" * 80)
    print("🌍 SISTEMA DE COORDENAÇÃO INTELIGENTE - PANGEIA")
    print("=" * 80)
    print()

    # Inicializa componentes
    print("🔧 Inicializando componentes...")
    tasks_manager = TasksManager()
    team_coordinator = TeamCoordinator(tasks_manager=tasks_manager)
    connection_detector = ConnectionDetector(team_coordinator=team_coordinator)
    collab_recommender = CollaborationRecommender(connection_detector=connection_detector)

    print("✅ Componentes prontos!\n")

    # SYNC COMPLETO
    print("=" * 80)
    print("🔄 SINCRONIZANDO TUDO...")
    print("=" * 80)
    team_map = team_coordinator.sync_all()
    print()

    # VISÃO GERAL DO TIME
    print("=" * 80)
    print("👥 VISÃO GERAL DO TIME")
    print("=" * 80)
    summary = team_coordinator.get_team_summary()
    print(f"Total de pessoas: {summary['total_people']}")
    print(f"Total de projetos: {summary['total_projects']}")
    print(f"Total de tasks: {summary['total_tasks']}")
    print(f"  • Em Andamento: {summary['tasks_em_andamento']}")
    print(f"  • A Fazer: {summary['tasks_a_fazer']}")
    print(f"  • Concluídas: {summary['tasks_concluidas']}")
    print(f"\nWorkload médio: {summary['avg_workload']*100:.0f}%")
    print(f"Pessoas sobrecarregadas: {summary['overloaded_count']}")
    print(f"Pessoas subutilizadas: {summary['underutilized_count']}")
    print()

    # PESSOAS
    print("=" * 80)
    print("👤 PESSOAS (ordenadas por workload)")
    print("=" * 80)
    people = team_coordinator.get_all_people()
    for i, person in enumerate(people, 1):
        workload_bar = "█" * int(person.workload_score * 20)
        print(f"\n{i}. {person.name}")
        print(f"   Workload: [{workload_bar:<20}] {person.workload_score*100:.0f}%")
        print(f"   Tasks: {person.tasks_total} total | {person.tasks_em_andamento} em andamento | {person.tasks_a_fazer} a fazer | {person.tasks_concluidas} concluídas")
        print(f"   Projetos: {', '.join(person.projects) if person.projects else 'Nenhum'}")
        print(f"   Colaboradores: {', '.join(person.collaborators) if person.collaborators else 'Nenhum'}")

    print()

    # PROJETOS
    print("=" * 80)
    print("📁 PROJETOS (ordenados por completion)")
    print("=" * 80)
    projects = team_coordinator.get_all_projects()
    for i, project in enumerate(projects, 1):
        completion_bar = "█" * int(project.completion_rate * 20)
        print(f"\n{i}. {project.name}")
        print(f"   Completion: [{completion_bar:<20}] {project.completion_rate*100:.0f}%")
        print(f"   Tasks: {project.tasks_total} total | {project.tasks_pending} pendentes | {project.tasks_completed} concluídas")
        print(f"   Time: {', '.join(project.people)}")

    print()

    # CONEXÕES DETECTADAS
    print("=" * 80)
    print("🔗 CONEXÕES DETECTADAS")
    print("=" * 80)
    connections = connection_detector.detect_all_connections()
    print(f"Total de conexões: {len(connections)}\n")

    # Mostra top 10 conexões mais fortes
    print("Top 10 conexões mais fortes:")
    for i, conn in enumerate(connections[:10], 1):
        strength_bar = "█" * int(conn.strength * 20)
        print(f"\n{i}. {conn.person_a} ↔ {conn.person_b}")
        print(f"   Força: [{strength_bar:<20}] {conn.strength*100:.0f}%")
        print(f"   Tipo: {conn.connection_type.value}")
        print(f"   Razão: {conn.reason}")

    print()

    # RECOMENDAÇÕES
    print("=" * 80)
    print("💡 RECOMENDAÇÕES DE COLABORAÇÃO")
    print("=" * 80)
    recommendations = collab_recommender.generate_all_recommendations()
    print(f"Total de recomendações: {len(recommendations)}\n")

    # Agrupa por prioridade
    critical = [r for r in recommendations if r.priority.value == "critical"]
    high = [r for r in recommendations if r.priority.value == "high"]

    print(f"🚨 Críticas (bloqueios ativos): {len(critical)}")
    print(f"⚡ Importantes: {len(high)}\n")

    if critical:
        print("\n🚨 RECOMENDAÇÕES CRÍTICAS:")
        for i, rec in enumerate(critical, 1):
            print(f"\n{i}. Para: {rec.target_person}")
            print(f"   Envolve: {', '.join(rec.involves)}")
            print(f"   Ação: {rec.action_type}")
            print(f"   Mensagem:")
            for line in rec.message.split('\n'):
                print(f"      {line}")

    if high:
        print("\n⚡ RECOMENDAÇÕES IMPORTANTES (Top 5):")
        for i, rec in enumerate(high[:5], 1):
            print(f"\n{i}. Para: {rec.target_person}")
            print(f"   Envolve: {', '.join(rec.involves)}")
            print(f"   Ação: {rec.action_type}")
            print(f"   Mensagem:")
            for line in rec.message.split('\n'):
                print(f"      {line}")

    print()

    # INSIGHTS PARA O SARAIVA
    print("=" * 80)
    print("🎯 INSIGHTS ESPECÍFICOS PARA SARAIVA")
    print("=" * 80)

    # Overview do Saraiva
    saraiva = team_coordinator.get_person_overview("Saraiva")
    if saraiva:
        print(f"\n👤 SARAIVA")
        workload_bar = "█" * int(saraiva.workload_score * 20)
        print(f"Workload: [{workload_bar:<20}] {saraiva.workload_score*100:.0f}%")
        print(f"Tasks: {saraiva.tasks_total} total | {saraiva.tasks_em_andamento} em andamento | {saraiva.tasks_a_fazer} a fazer")
        print(f"Projetos: {', '.join(saraiva.projects)}")
        print(f"Colaboradores: {', '.join(saraiva.collaborators)}")

    # Recomendações para o Saraiva
    saraiva_recs = collab_recommender.get_recommendations_for_person("Saraiva")
    print(f"\n💡 Recomendações para Saraiva: {len(saraiva_recs)}")

    if saraiva_recs:
        for i, rec in enumerate(saraiva_recs, 1):
            print(f"\n{i}. Prioridade: {rec.priority.value.upper()}")
            print(f"   Envolve: {', '.join(rec.involves)}")
            print(f"   Ação: {rec.action_type}")
            print(f"   Mensagem:")
            for line in rec.message.split('\n'):
                print(f"      {line}")

    print()

    # TEAM INSIGHTS
    print("=" * 80)
    print("📊 INSIGHTS GERAIS DO TIME")
    print("=" * 80)
    team_insights = collab_recommender.generate_team_insights()
    print(team_insights)

    print()
    print("=" * 80)
    print("✅ ANÁLISE COMPLETA!")
    print("=" * 80)

if __name__ == "__main__":
    main()
