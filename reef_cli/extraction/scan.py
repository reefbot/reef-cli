import logging
import pathlib
import typing as ty

from pprint import pformat
import libcst as cst
from libcst.metadata import MetadataWrapper
import matplotlib.pyplot as plt
import networkx as nx

from reef_cli.extraction.extractor import Extractor, Node, Edge
from reef_cli.extraction.utils import get_all_files

handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger("reef")
logger.addHandler(handler)
logger.setLevel(level=logging.DEBUG)


def scan_file(
    file_path: pathlib.Path, project_root: pathlib.Path
) -> tuple[list[Node], list[Edge]]:
    visitor = Extractor(file_path=file_path, project_root=project_root)
    with open(file_path, "rb") as f:
        syntax_tree = MetadataWrapper(cst.parse_module(f.read()))
        syntax_tree.visit(visitor)

    nodes, edges = visitor.finalize()
    """
    logger.debug(f"Found {len(nodes)} nodes and {len(edges)} edges")

    if len(nodes) > 0:
        logger.debug(
            f"Nodes:\n {'\n\n'.join([pformat(nd.__str__()) for nd in nodes])}\n\n"
        )
    if len(edges) > 0:
        logger.debug(
            f"Edges:\n {'\n\n'.join([pformat(ed.__str__()) for ed in edges])}"
        )
    """
    return nodes, edges


def scan_project(
    project_root: pathlib.Path,
) -> tuple[list[Node], list[Edge]]:
    nodes = []
    edges = []
    for file in get_all_files(root_dir=project_root, ext=".py"):
        logger.info(f"Scanning {file}")
        file_nodes, file_edges = scan_file(file_path=file, project_root=project_root)
        nodes.extend(file_nodes)
        edges.extend(file_edges)

    return nodes, edges


def build_graph(nodes, edges):
    G = nx.DiGraph()
    for node in nodes:
        #logger.debug(f"Adding {node}")
        G.add_node(node.qualified_name, data=node)
    for edge in edges:
        logger.debug(f"Adding {edge}")
        G.add_edge(edge.source, edge.target, kind=edge.kind)

    return G


def plot_graph(graph: nx.DiGraph):
    # G is your existing graph
    # Assume each node has 'data', and each edge has 'kind'

    # Use graphviz layout (if installed) for better layout
    # Otherwise fallback to spring layout
    try:
        pos = nx.nx_agraph.graphviz_layout(graph, prog='dot')
    except:
        pos = nx.spring_layout(graph)

    # Draw nodes with labels
    nx.draw_networkx_nodes(graph, pos, node_size=700, node_color='lightblue')
    node_labels = {n: (graph.nodes[n]["data"].__class__.__name__+ ": " + graph.nodes[n]["data"].name) for n in graph.nodes}
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=8)

    # Draw edges with labels
    nx.draw_networkx_edges(graph, pos, arrowstyle="->", arrowsize=15)
    edge_labels = {(u, v): d['kind'] for u, v, d in graph.edges(data=True)}
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='red', font_size=6)

    plt.title("Dependency Graph with Edge Kinds")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    nodes, edges = scan_project(pathlib.Path("/Users/tomcarter/reef/reef-cli/tests/dummy_proj/hello_world/"))
    graph = build_graph(nodes, edges)




    #plot_graph(graph)