"""
Dependency Mapper - Mapeamento de Dependências entre Tarefas.

Analisa e mapeia dependências entre subtarefas para otimizar ordem de execução.
"""

import logging
from typing import List, Dict, Set, Tuple

logger = logging.getLogger(__name__)


class DependencyMapper:
    """
    Mapeia dependências entre tarefas e subtarefas.

    Identifica:
    - Dependências diretas
    - Caminho crítico
    - Oportunidades de paralelização
    - Bloqueios potenciais
    """

    def __init__(self):
        """Inicializa o mapeador."""
        logger.info("DependencyMapper inicializado")

    def build_dependency_graph(
        self,
        subtasks: List[Dict]
    ) -> Dict:
        """
        Constrói grafo de dependências.

        Args:
            subtasks: Lista de subtasks com field 'dependencies'

        Returns:
            Dict com grafo e análises
        """
        # Construir grafo (adjacência)
        graph = {}
        reverse_graph = {}  # Quem depende de mim

        for subtask in subtasks:
            order = subtask.get("order")
            dependencies = subtask.get("dependencies", [])

            graph[order] = dependencies

            # Reverse graph
            for dep in dependencies:
                if dep not in reverse_graph:
                    reverse_graph[dep] = []
                reverse_graph[dep].append(order)

        return {
            "graph": graph,
            "reverse_graph": reverse_graph,
            "nodes": len(subtasks)
        }

    def find_critical_path(
        self,
        subtasks: List[Dict]
    ) -> List[int]:
        """
        Encontra caminho crítico (sequência mais longa).

        Args:
            subtasks: Lista de subtasks

        Returns:
            Lista de orders no caminho crítico
        """
        graph_data = self.build_dependency_graph(subtasks)
        graph = graph_data["graph"]

        # DFS para encontrar caminho mais longo
        def dfs_longest_path(node: int, visited: Set[int]) -> List[int]:
            visited.add(node)

            dependencies = graph.get(node, [])
            if not dependencies:
                # Nó folha
                return [node]

            # Explorar todos os caminhos
            max_path = []
            for dep in dependencies:
                if dep not in visited:
                    path = dfs_longest_path(dep, visited.copy())
                    if len(path) > len(max_path):
                        max_path = path

            return max_path + [node]

        # Encontrar todos os nós sem dependentes (finais)
        reverse_graph = graph_data["reverse_graph"]
        final_nodes = [
            subtask.get("order")
            for subtask in subtasks
            if subtask.get("order") not in reverse_graph
            or len(reverse_graph.get(subtask.get("order"), [])) == 0
        ]

        # Caminho mais longo entre todos os finais
        critical_path = []
        for final_node in final_nodes:
            path = dfs_longest_path(final_node, set())
            if len(path) > len(critical_path):
                critical_path = path

        return critical_path

    def find_parallel_opportunities(
        self,
        subtasks: List[Dict]
    ) -> List[List[int]]:
        """
        Encontra subtasks que podem ser executadas em paralelo.

        Args:
            subtasks: Lista de subtasks

        Returns:
            Lista de grupos de subtasks paralelas
        """
        graph_data = self.build_dependency_graph(subtasks)
        graph = graph_data["graph"]

        # Agrupar por nível (tasks com mesmas dependências)
        level_groups: Dict[int, List[int]] = {}

        for subtask in subtasks:
            order = subtask.get("order")
            dependencies = graph.get(order, [])

            # Nível = max(níveis das dependências) + 1
            if not dependencies:
                level = 0
            else:
                level = max(
                    level_groups.get(dep, [0])[0] if dep in level_groups else 0
                    for dep in dependencies
                ) + 1

            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(order)

        # Retornar apenas grupos com 2+ tasks
        parallel_groups = [
            group
            for group in level_groups.values()
            if len(group) >= 2
        ]

        return parallel_groups

    def validate_dependencies(
        self,
        subtasks: List[Dict]
    ) -> Dict:
        """
        Valida se dependências são válidas (sem ciclos).

        Args:
            subtasks: Lista de subtasks

        Returns:
            Dict com resultado da validação
        """
        graph_data = self.build_dependency_graph(subtasks)
        graph = graph_data["graph"]

        # Detectar ciclos usando DFS
        def has_cycle_dfs(node: int, visited: Set[int], stack: Set[int]) -> bool:
            visited.add(node)
            stack.add(node)

            for dep in graph.get(node, []):
                if dep not in visited:
                    if has_cycle_dfs(dep, visited, stack):
                        return True
                elif dep in stack:
                    # Ciclo detectado!
                    return True

            stack.remove(node)
            return False

        visited = set()
        has_cycle = False

        for subtask in subtasks:
            order = subtask.get("order")
            if order not in visited:
                if has_cycle_dfs(order, visited, set()):
                    has_cycle = True
                    break

        # Validar referências
        invalid_refs = []
        all_orders = {subtask.get("order") for subtask in subtasks}

        for subtask in subtasks:
            for dep in subtask.get("dependencies", []):
                if dep not in all_orders:
                    invalid_refs.append({
                        "from": subtask.get("order"),
                        "to": dep,
                        "error": "Dependência referencia subtask inexistente"
                    })

        return {
            "is_valid": not has_cycle and len(invalid_refs) == 0,
            "has_cycle": has_cycle,
            "invalid_references": invalid_refs,
            "total_dependencies": sum(len(graph.get(node, [])) for node in graph)
        }

    def get_next_available_tasks(
        self,
        subtasks: List[Dict],
        completed_orders: List[int]
    ) -> List[Dict]:
        """
        Retorna subtasks que podem ser iniciadas agora.

        Args:
            subtasks: Lista de subtasks
            completed_orders: Orders já concluídas

        Returns:
            Lista de subtasks disponíveis
        """
        available = []

        for subtask in subtasks:
            order = subtask.get("order")

            # Já foi feita?
            if order in completed_orders:
                continue

            # Dependências foram todas concluídas?
            dependencies = subtask.get("dependencies", [])
            all_deps_done = all(dep in completed_orders for dep in dependencies)

            if all_deps_done:
                available.append(subtask)

        return available
