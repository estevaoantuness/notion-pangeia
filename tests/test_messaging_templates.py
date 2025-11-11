from src.messaging.templates import format_progress_report


def test_format_progress_report_structure():
    tasks_grouped = {
        "concluidas": [],
        "em_andamento": [
            {"nome": "Automações Notion x Whatsapp (CS PANGE.IA)"}
        ],
        "a_fazer": [
            {"nome": "Sistema de indicação"},
            {"nome": "Apoiar Sami desenvolvimento Oxy"},
            {"nome": "Automatizar social midia"},
            {"nome": "Criar apresentação final"},
        ],
    }

    progress = {
        "total": 14,
        "concluidas": 7,
        "em_andamento": 1,
        "pendentes": 6,
        "percentual": 50,
    }

    message = format_progress_report("Estevao Antunes", tasks_grouped, progress)

    assert "📊 *Relatório de Progresso* (Estevao)" in message
    assert "[█████" in message  # barra de progresso
    assert "✅ Concluídas: 7" in message
    assert "🔄 Automações Notion x Whatsapp" in message
    assert "⬜ Sistema de indicação" in message
    assert "_...e mais 1_" in message
