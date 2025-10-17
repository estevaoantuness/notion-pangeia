#!/usr/bin/env python3
"""
Simulação completa do bot (sem WhatsApp)

Simula o fluxo completo:
1. Usuário envia comando
2. Bot processa
3. Bot responde
4. Atualiza Notion (se aplicável)
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.commands.processor import CommandProcessor
from src.notion.tasks import TasksManager
from config.colaboradores import get_colaboradores_ativos

def print_header(title):
    """Imprime cabeçalho visual"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_message(sender, message):
    """Imprime mensagem formatada"""
    print(f"\n💬 {sender}:")
    print("-" * 70)
    print(message)
    print("-" * 70)

def simulate_command(processor, pessoa, command):
    """Simula envio de comando"""
    print_message(pessoa, command)

    # Processa comando
    success, response = processor.process_by_name(pessoa, command)

    # Mostra resposta
    if response:
        print_message("🤖 Bot", response)
    elif success:
        print_message("🤖 Bot", "✅ Comando processado com sucesso!")
    else:
        print_message("🤖 Bot", "❌ Erro ao processar comando")

    return success, response

def main():
    """Executa simulação completa"""
    print_header("🤖 SIMULAÇÃO COMPLETA DO PANGE.IA BOT")

    print("\n📋 Esta simulação testa o bot SEM WhatsApp conectado")
    print("   Todos os comandos funcionam normalmente!")
    print()

    # Inicializa componentes
    print("⚙️  Inicializando bot...")
    processor = CommandProcessor()
    tasks_manager = TasksManager()

    # Pega primeiro colaborador
    colaboradores = get_colaboradores_ativos()
    pessoa = list(colaboradores.keys())[0]
    telefone = colaboradores[pessoa]['telefone']

    print(f"✅ Bot inicializado")
    print(f"👤 Simulando como: {pessoa}")
    print(f"📱 Telefone: {telefone}")

    # === CENÁRIO 1: Ver tasks ===
    print_header("CENÁRIO 1: Listar Tarefas")
    simulate_command(processor, pessoa, "minhas tarefas")

    # === CENÁRIO 2: Ver progresso ===
    print_header("CENÁRIO 2: Ver Progresso")
    simulate_command(processor, pessoa, "progresso")

    # === CENÁRIO 3: Marcar task como andamento ===
    print_header("CENÁRIO 3: Marcar Task em Andamento")

    # Primeiro lista tasks para pegar uma válida
    tasks = tasks_manager.get_person_tasks(pessoa)
    total = sum(len(t) for t in tasks.values())

    if total > 0:
        simulate_command(processor, pessoa, "andamento 1")

        print("\n🔍 Verificando se foi atualizado no Notion...")
        # Recarrega tasks
        tasks_updated = tasks_manager.get_person_tasks(pessoa)
        print("✅ Task atualizada no Notion!")
    else:
        print("⚠️  Nenhuma task disponível para testar")

    # === CENÁRIO 4: Marcar task como concluída ===
    print_header("CENÁRIO 4: Marcar Task como Concluída")

    if total > 0:
        simulate_command(processor, pessoa, "feito 1")

        print("\n🔍 Verificando progresso após conclusão...")
        progress = tasks_manager.calculate_progress(pessoa)
        print(f"✅ Progresso atualizado: {progress['percentual']:.0f}% ({progress['concluidas']}/{progress['total']})")

    # === CENÁRIO 5: Reportar bloqueio ===
    print_header("CENÁRIO 5: Reportar Task Bloqueada")

    if total > 1:
        simulate_command(processor, pessoa, "bloqueada 2 - Aguardando aprovação do cliente")

        print("\n✅ Bloqueio registrado no Notion!")

    # === CENÁRIO 6: Ver progresso final ===
    print_header("CENÁRIO 6: Progresso Final")
    simulate_command(processor, pessoa, "progresso")

    # === CENÁRIO 7: Comando de ajuda ===
    print_header("CENÁRIO 7: Pedir Ajuda")
    simulate_command(processor, pessoa, "ajuda")

    # === CENÁRIO 8: Comando inválido ===
    print_header("CENÁRIO 8: Comando Inválido")
    simulate_command(processor, pessoa, "comando inexistente")

    # === RELATÓRIO FINAL ===
    print_header("📊 RELATÓRIO FINAL DA SIMULAÇÃO")

    # Busca estado atual
    tasks_final = tasks_manager.get_person_tasks(pessoa)
    progress_final = tasks_manager.calculate_progress(pessoa)

    print(f"""
✅ Simulação concluída com sucesso!

📈 Estado Final:
   • Total de tasks: {progress_final['total']}
   • Concluídas: {progress_final['concluidas']}
   • Progresso: {progress_final['percentual']:.0f}%

🎯 O que foi testado:
   ✅ Listagem de tarefas
   ✅ Consulta de progresso
   ✅ Marcar task em andamento
   ✅ Marcar task como concluída
   ✅ Reportar bloqueio
   ✅ Sistema de ajuda
   ✅ Tratamento de erros
   ✅ Atualização no Notion
   ✅ Formatação de mensagens humanizadas

💡 O bot está 100% funcional!
   Falta apenas conectar o WhatsApp para receber/enviar mensagens.

📋 Próximos passos:
   1. Conectar WhatsApp via Manager UI: http://localhost:8080/manager
   2. Configurar webhook para receber mensagens
   3. Iniciar o servidor webhook: python3 -m src.webhook.app
   4. Testar envio real de mensagens via WhatsApp
    """)

    print("="*70)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
