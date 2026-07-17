#!/usr/bin/env python3
"""Generate publication-ready and interactive hypergraph visualizations.

The GraphML projections are dense, so static and interactive views use a
transparent, deterministic weighted core: the strongest nodes plus the
strongest edges among them. The original GraphML files remain the canonical
complete projections. Native XGI figures use a readable weighted core of the
original target-as-hyperedge JSON representation.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from itertools import combinations
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
import numpy as np
from pyvis.network import Network
import xgi

SEED = 20260717
BACKGROUND = "#0b1220"
PANEL = "#111827"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"
EDGE = "#94a3b8"
PALETTE = [
    "#38bdf8",
    "#f59e0b",
    "#34d399",
    "#f472b6",
    "#a78bfa",
    "#fb7185",
    "#22d3ee",
    "#facc15",
    "#4ade80",
    "#c084fc",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--top-nodes", type=int, default=70)
    parser.add_argument("--top-edges", type=int, default=700)
    parser.add_argument("--xgi-hyperedges", type=int, default=10)
    parser.add_argument("--xgi-nodes", type=int, default=34)
    return parser.parse_args()


def load_translation_labels(root: Path) -> dict[str, str]:
    payload = json.loads((root / "config" / "corpus.json").read_text(encoding="utf-8"))
    return {
        item["id"]: f"{item['translator']} ({item['year']})"
        for item in payload["translations"]
    }


def weighted_strength(graph: nx.Graph) -> dict[str, float]:
    return {
        str(node): float(sum(float(data.get("weight", 1.0)) for _, _, data in graph.edges(node, data=True)))
        for node in graph.nodes
    }


def weighted_core(graph: nx.Graph, top_nodes: int, top_edges: int) -> tuple[nx.Graph, dict[str, float]]:
    strengths = weighted_strength(graph)
    ordered_nodes = sorted(graph.nodes, key=lambda node: (-strengths[str(node)], str(node)))
    selected_nodes = ordered_nodes[: min(top_nodes, len(ordered_nodes))]
    induced = graph.subgraph(selected_nodes).copy()
    ordered_edges = sorted(
        induced.edges(data=True),
        key=lambda item: (-float(item[2].get("weight", 1.0)), str(item[0]), str(item[1])),
    )
    core = nx.Graph(**graph.graph)
    for node in selected_nodes:
        core.add_node(node, **graph.nodes[node])
    for left, right, data in ordered_edges[: min(top_edges, len(ordered_edges))]:
        core.add_edge(left, right, **data)
    core.remove_nodes_from(list(nx.isolates(core)))
    return core, strengths


def community_map(graph: nx.Graph) -> dict[str, int]:
    if graph.number_of_edges() == 0:
        return {str(node): index for index, node in enumerate(sorted(graph.nodes))}
    communities = list(nx.community.greedy_modularity_communities(graph, weight="weight"))
    communities.sort(key=lambda group: (-len(group), min(str(item) for item in group)))
    return {
        str(node): index
        for index, group in enumerate(communities)
        for node in sorted(group, key=str)
    }


def layout_graph(graph: nx.Graph) -> dict[Any, np.ndarray]:
    if graph.number_of_nodes() <= 2:
        return nx.circular_layout(graph)
    backbone = nx.maximum_spanning_tree(graph, weight="weight")
    extras = sorted(
        graph.edges(data=True),
        key=lambda item: (-float(item[2].get("weight", 1.0)), str(item[0]), str(item[1])),
    )[: max(80, graph.number_of_nodes() * 3)]
    layout_input = backbone.copy()
    layout_input.add_edges_from(extras)
    return nx.spring_layout(
        layout_input,
        seed=SEED,
        weight="weight",
        iterations=220,
        k=1.5 / math.sqrt(max(graph.number_of_nodes(), 1)),
    )


def projection_kind(path: Path) -> str:
    return "attribute" if "attribute_projection" in path.name else "target"


def translation_id(path: Path) -> str:
    return path.name.replace("_attribute_projection.graphml", "").replace("_target_projection.graphml", "")


def draw_projection_static(
    graph: nx.Graph,
    source_graph: nx.Graph,
    source_path: Path,
    output_base: Path,
    label: str,
    strengths: dict[str, float],
) -> None:
    plt.style.use("dark_background")
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "svg.hashsalt": "odyssey-attribution-v1"})
    figure, axis = plt.subplots(figsize=(16, 11), facecolor=BACKGROUND)
    axis.set_facecolor(PANEL)
    axis.axis("off")

    positions = layout_graph(graph)
    communities = community_map(graph)
    plotted_strength = np.asarray([strengths[str(node)] for node in graph.nodes], dtype=float)
    maximum_strength = float(plotted_strength.max()) if len(plotted_strength) else 1.0
    node_sizes = [150 + 1250 * math.sqrt(strengths[str(node)] / maximum_strength) for node in graph.nodes]
    node_colors = [PALETTE[communities[str(node)] % len(PALETTE)] for node in graph.nodes]

    edge_weights = np.asarray([float(data.get("weight", 1.0)) for _, _, data in graph.edges(data=True)], dtype=float)
    maximum_edge = float(edge_weights.max()) if len(edge_weights) else 1.0
    edge_widths = [0.25 + 3.2 * (float(data.get("weight", 1.0)) / maximum_edge) ** 0.65 for _, _, data in graph.edges(data=True)]
    edge_alphas = [0.06 + 0.46 * (float(data.get("weight", 1.0)) / maximum_edge) ** 0.55 for _, _, data in graph.edges(data=True)]

    for (left, right, _), width, alpha in zip(graph.edges(data=True), edge_widths, edge_alphas):
        nx.draw_networkx_edges(
            graph,
            positions,
            edgelist=[(left, right)],
            width=width,
            alpha=alpha,
            edge_color=EDGE,
            ax=axis,
        )
    nx.draw_networkx_nodes(
        graph,
        positions,
        node_size=node_sizes,
        node_color=node_colors,
        linewidths=0.8,
        edgecolors="#f8fafc",
        alpha=0.94,
        ax=axis,
    )

    label_nodes = sorted(graph.nodes, key=lambda node: (-strengths[str(node)], str(node)))[:18]
    label_positions = {node: positions[node] + np.array([0.0, 0.018]) for node in label_nodes}
    nx.draw_networkx_labels(
        graph,
        label_positions,
        labels={node: str(node) for node in label_nodes},
        font_size=8.2,
        font_color=TEXT,
        font_weight="semibold",
        bbox={"boxstyle": "round,pad=0.18", "facecolor": BACKGROUND, "edgecolor": "none", "alpha": 0.72},
        ax=axis,
    )

    kind = projection_kind(source_path)
    title_kind = "Attribute projection" if kind == "attribute" else "Target projection"
    figure.suptitle(f"{label} — {title_kind}", x=0.055, y=0.965, ha="left", fontsize=22, fontweight="bold", color=TEXT)
    axis.set_title(
        f"Weighted core view: {graph.number_of_nodes()} of {source_graph.number_of_nodes()} nodes; "
        f"{graph.number_of_edges()} of {source_graph.number_of_edges()} edges",
        loc="left",
        fontsize=11,
        color=MUTED,
        pad=18,
    )
    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PALETTE[0], markeredgecolor="white", markersize=10, label="Node size = weighted strength"),
        Line2D([0], [0], color=EDGE, linewidth=2.5, label="Edge width = shared-incidence weight"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PALETTE[1], markersize=10, label="Color = modularity community"),
    ]
    axis.legend(handles=legend, loc="lower left", frameon=False, labelcolor=TEXT, fontsize=9)
    figure.text(
        0.055,
        0.025,
        "Deterministic weighted-core visualization; the complete projection remains in the source GraphML file.",
        color=MUTED,
        fontsize=9,
    )
    figure.tight_layout(rect=(0.035, 0.05, 0.985, 0.94))
    figure.savefig(output_base.with_suffix(".png"), dpi=220, facecolor=figure.get_facecolor(), bbox_inches="tight")
    figure.savefig(output_base.with_suffix(".svg"), facecolor=figure.get_facecolor(), bbox_inches="tight", metadata={"Date": None})
    plt.close(figure)


def draw_projection_interactive(
    graph: nx.Graph,
    source_graph: nx.Graph,
    source_path: Path,
    output_path: Path,
    label: str,
    strengths: dict[str, float],
) -> None:
    communities = community_map(graph)
    maximum_strength = max((strengths[str(node)] for node in graph.nodes), default=1.0)
    maximum_edge = max((float(data.get("weight", 1.0)) for _, _, data in graph.edges(data=True)), default=1.0)
    network = Network(
        height="900px",
        width="100%",
        bgcolor=BACKGROUND,
        font_color=TEXT,
        directed=False,
        cdn_resources="in_line",
    )
    for node in sorted(graph.nodes, key=str):
        strength = strengths[str(node)]
        network.add_node(
            str(node),
            label=str(node),
            title=(
                f"<b>{node}</b><br>Weighted strength: {strength:.3f}"
                f"<br>Displayed degree: {graph.degree(node)}"
            ),
            value=8 + 42 * math.sqrt(strength / maximum_strength),
            color={"background": PALETTE[communities[str(node)] % len(PALETTE)], "border": "#f8fafc"},
            borderWidth=1,
        )
    for left, right, data in sorted(graph.edges(data=True), key=lambda item: (str(item[0]), str(item[1]))):
        weight = float(data.get("weight", 1.0))
        network.add_edge(
            str(left),
            str(right),
            value=0.5 + 7.5 * (weight / maximum_edge) ** 0.65,
            title=f"Shared-incidence weight: {weight:.3f}",
            color={"color": EDGE, "opacity": 0.32},
        )
    network.set_options(
        json.dumps(
            {
                "nodes": {"font": {"color": TEXT, "size": 13, "face": "DejaVu Sans"}},
                "edges": {"smooth": {"enabled": False}, "selectionWidth": 2},
                "interaction": {"hover": True, "navigationButtons": True, "keyboard": True},
                "physics": {
                    "enabled": True,
                    "solver": "forceAtlas2Based",
                    "forceAtlas2Based": {
                        "gravitationalConstant": -70,
                        "centralGravity": 0.015,
                        "springLength": 120,
                        "springConstant": 0.055,
                        "damping": 0.45,
                        "avoidOverlap": 0.4,
                    },
                    "stabilization": {"enabled": True, "iterations": 700, "updateInterval": 50},
                },
            }
        )
    )
    network.write_html(str(output_path), notebook=False, open_browser=False)
    html = output_path.read_text(encoding="utf-8")
    title = f"{label} — {projection_kind(source_path).title()} projection"
    explanatory = (
        f"<div style='font-family:Arial,sans-serif;color:{TEXT};background:{BACKGROUND};padding:14px 18px 10px;'>"
        f"<h1 style='font-size:25px;line-height:1.2;margin:0 0 7px 0;color:{TEXT};'>{title}</h1>"
        f"<p style='font-size:13px;line-height:1.4;margin:0;color:{MUTED};'>"
        f"Weighted core: {graph.number_of_nodes()} of {source_graph.number_of_nodes()} nodes and "
        f"{graph.number_of_edges()} of {source_graph.number_of_edges()} edges. "
        "Hover for weights; drag nodes; use navigation controls. The source GraphML retains the complete projection."
        "</p></div>"
    )
    html = html.replace("<body>", f"<body style='margin:0;background:{BACKGROUND};'>{explanatory}", 1)
    output_path.write_text(html, encoding="utf-8")


def weighted_hypergraph_core(payload: dict[str, Any], top_hyperedges: int, top_nodes: int) -> tuple[dict[str, set[str]], dict[str, float], dict[str, float]]:
    edge_weights = {
        target: float(sum(float(record["weight"]) for record in records))
        for target, records in payload["hyperedges"].items()
    }
    selected_targets = sorted(edge_weights, key=lambda target: (-edge_weights[target], target))[:top_hyperedges]
    node_weights: dict[str, float] = {}
    for target in selected_targets:
        for record in payload["hyperedges"][target]:
            attribute = str(record["attribute"])
            node_weights[attribute] = node_weights.get(attribute, 0.0) + float(record["weight"])
    selected_nodes = set(sorted(node_weights, key=lambda node: (-node_weights[node], node))[:top_nodes])
    hyperedges = {
        target: {
            str(record["attribute"])
            for record in payload["hyperedges"][target]
            if str(record["attribute"]) in selected_nodes
        }
        for target in selected_targets
    }
    hyperedges = {target: members for target, members in hyperedges.items() if len(members) >= 2}
    retained_nodes = {node for members in hyperedges.values() for node in members}
    return hyperedges, {node: node_weights[node] for node in retained_nodes}, edge_weights


def draw_xgi_native(
    payload: dict[str, Any],
    output_base: Path,
    label: str,
    top_hyperedges: int,
    top_nodes: int,
) -> dict[str, int]:
    hyperedge_dictionary, node_weights, edge_weights = weighted_hypergraph_core(payload, top_hyperedges, top_nodes)
    canonical_hyperedges = {
        edge: sorted(hyperedge_dictionary[edge])
        for edge in sorted(hyperedge_dictionary)
    }
    hypergraph = xgi.Hypergraph(canonical_hyperedges)
    plt.style.use("dark_background")
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "svg.hashsalt": "odyssey-attribution-v1"})
    figure, axes = plt.subplots(1, 2, figsize=(20, 11), facecolor=BACKGROUND)
    for axis in axes:
        axis.set_facecolor(PANEL)
        axis.axis("off")

    node_order = sorted(hypergraph.nodes, key=lambda node: (-node_weights[str(node)], str(node)))
    weighted_projection = nx.Graph()
    weighted_projection.add_nodes_from(node_order)
    for edge in sorted(canonical_hyperedges):
        for left, right in combinations(canonical_hyperedges[edge], 2):
            previous = float(weighted_projection.get_edge_data(left, right, {}).get("weight", 0.0))
            weighted_projection.add_edge(left, right, weight=previous + edge_weights[edge])
    native_positions = nx.spring_layout(
        weighted_projection,
        seed=SEED,
        weight="weight",
        iterations=260,
        k=1.35 / math.sqrt(max(weighted_projection.number_of_nodes(), 1)),
    )
    label_nodes = set(node_order[:16])
    node_labels = {node: str(node) for node in label_nodes}
    xgi.draw(
        hypergraph,
        pos=native_positions,
        ax=axes[0],
        node_fc="#38bdf8",
        node_ec="#f8fafc",
        node_lw=0.8,
        node_size=12,
        edge_fc="#f59e0b",
        edge_ec="#fbbf24",
        edge_lw=0.8,
        alpha=0.13,
        hull=True,
        node_labels=node_labels,
        hyperedge_labels=False,
        font_size_nodes=8.2,
        font_color_nodes=TEXT,
    )
    axes[0].set_title("XGI native hyperedge-hull view", loc="left", fontsize=15, fontweight="bold", color=TEXT, pad=14)

    incidence_graph = nx.Graph()
    node_keys = [("attribute", node) for node in node_order]
    edge_order = sorted(canonical_hyperedges, key=lambda edge: (-edge_weights[edge], edge))
    edge_keys = [("target", edge) for edge in edge_order]
    incidence_graph.add_nodes_from(node_keys)
    incidence_graph.add_nodes_from(edge_keys)
    for edge in edge_order:
        for node in canonical_hyperedges[edge]:
            incidence_graph.add_edge(("attribute", node), ("target", edge), weight=edge_weights[edge])
    incidence_positions = nx.spring_layout(
        incidence_graph,
        seed=SEED,
        weight="weight",
        iterations=320,
        k=1.55 / math.sqrt(max(incidence_graph.number_of_nodes(), 1)),
    )
    bipartite_positions = (
        {node: incidence_positions[("attribute", node)] for node in node_order},
        {edge: incidence_positions[("target", edge)] for edge in edge_order},
    )
    hyperedge_labels = {edge: str(edge) for edge in edge_order}
    xgi.draw_bipartite(
        hypergraph,
        pos=bipartite_positions,
        ax=axes[1],
        node_fc="#38bdf8",
        node_ec="#f8fafc",
        node_lw=0.8,
        node_size=10,
        edge_marker_fc="#f59e0b",
        edge_marker_ec="#f8fafc",
        edge_marker_lw=0.8,
        edge_marker_size=13,
        dyad_color=EDGE,
        dyad_lw=0.65,
        node_labels=node_labels,
        hyperedge_labels=hyperedge_labels,
        font_size_nodes=7.6,
        font_color_nodes=TEXT,
    )
    axes[1].set_title("XGI bipartite incidence view", loc="left", fontsize=15, fontweight="bold", color=TEXT, pad=14)

    total_incidences = sum(len(records) for records in payload["hyperedges"].values())
    figure.suptitle(f"{label} — Native target-as-hyperedge visualization", x=0.035, y=0.97, ha="left", fontsize=22, fontweight="bold", color=TEXT)
    figure.text(
        0.035,
        0.925,
        f"Readable weighted core: {len(hypergraph.nodes)} of {len(payload['vertices'])} attribute nodes; "
        f"{len(hypergraph.edges)} of {len(payload['hyperedges'])} target hyperedges; "
        f"{sum(len(hypergraph.edges.members(edge)) for edge in hypergraph.edges)} of {total_incidences} incidences.",
        color=MUTED,
        fontsize=11,
    )
    figure.text(
        0.035,
        0.025,
        "Blue circles are attributes; amber hulls or squares are target hyperedges. Selection is ranked by summed incidence weight.",
        color=MUTED,
        fontsize=9,
    )
    figure.tight_layout(rect=(0.02, 0.05, 0.985, 0.91))
    figure.savefig(output_base.with_suffix(".png"), dpi=220, facecolor=figure.get_facecolor(), bbox_inches="tight")
    figure.savefig(output_base.with_suffix(".svg"), facecolor=figure.get_facecolor(), bbox_inches="tight", metadata={"Date": None})
    plt.close(figure)
    return {
        "source_nodes": len(payload["vertices"]),
        "source_hyperedges": len(payload["hyperedges"]),
        "source_incidences": total_incidences,
        "plotted_nodes": len(hypergraph.nodes),
        "plotted_hyperedges": len(hypergraph.edges),
        "plotted_incidences": sum(len(hypergraph.edges.members(edge)) for edge in hypergraph.edges),
    }


def write_gallery(root: Path, output_root: Path, labels: dict[str, str], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Hypergraph Visualization Gallery",
        "",
        "This directory provides deterministic static, vector, and interactive views of every projection GraphML file, plus native XGI views of each target-as-hyperedge JSON artifact.",
        "",
        "> The projection files are dense. Visualizations therefore show a documented weighted core for legibility; the original GraphML and hypergraph JSON files remain the complete machine-readable results.",
        "",
        "## Visualization index",
        "",
        "| Translation | Target projection | Attribute projection | Native XGI hypergraph |",
        "|---|---|---|---|",
    ]
    for identifier, label in labels.items():
        target = f"projection_static/{identifier}_target_projection.png"
        attribute = f"projection_static/{identifier}_attribute_projection.png"
        xgi_path = f"xgi_native/{identifier}_xgi_hypergraph.png"
        lines.append(
            f"| {label} | [PNG]({target}) · [SVG](projection_static/{identifier}_target_projection.svg) · [interactive](projection_interactive/{identifier}_target_projection.html) "
            f"| [PNG]({attribute}) · [SVG](projection_static/{identifier}_attribute_projection.svg) · [interactive](projection_interactive/{identifier}_attribute_projection.html) "
            f"| [PNG]({xgi_path}) · [SVG](xgi_native/{identifier}_xgi_hypergraph.svg) |"
        )
    lines.extend(
        [
            "",
            "## Reading the figures",
            "",
            "In projection figures, node size encodes weighted strength, edge width encodes shared-incidence weight, and node color encodes a weighted modularity community. The top weighted nodes are labeled. Interactive HTML files support hover inspection, dragging, zooming, and navigation controls.",
            "",
            "In native XGI figures, blue circles represent normalized attributes. Amber hulls in the left panel and amber square markers in the right panel represent target hyperedges. The two panels display the same weighted core: XGI’s native hull representation and its bipartite incidence representation.",
            "",
            "## Selection parameters",
            "",
            "The exact source and plotted counts are recorded in [`visualization_inventory.csv`](visualization_inventory.csv). The renderer uses a fixed random seed and deterministic ranking rules. Reproduce all files with:",
            "",
            "```bash",
            "make visualize",
            "```",
            "",
        ]
    )
    (output_root / "README.md").write_text("\n".join(lines), encoding="utf-8")
    fieldnames = sorted({key for row in rows for key in row})
    with (output_root / "visualization_inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    source_root = root / "outputs" / "hypergraphs"
    output_root = root / "outputs" / "hypergraph_visualizations"
    if output_root.exists():
        shutil.rmtree(output_root)
    static_root = output_root / "projection_static"
    interactive_root = output_root / "projection_interactive"
    xgi_root = output_root / "xgi_native"
    for directory in (static_root, interactive_root, xgi_root):
        directory.mkdir(parents=True, exist_ok=True)

    labels = load_translation_labels(root)
    inventory: list[dict[str, Any]] = []
    for path in sorted(source_root.glob("*_projection.graphml")):
        identifier = translation_id(path)
        graph = nx.read_graphml(path)
        core, strengths = weighted_core(graph, args.top_nodes, args.top_edges)
        stem = path.stem
        draw_projection_static(graph=core, source_graph=graph, source_path=path, output_base=static_root / stem, label=labels[identifier], strengths=strengths)
        draw_projection_interactive(graph=core, source_graph=graph, source_path=path, output_path=interactive_root / f"{stem}.html", label=labels[identifier], strengths=strengths)
        inventory.append(
            {
                "translation_id": identifier,
                "translation": labels[identifier],
                "visualization": f"{projection_kind(path)}_projection",
                "source_nodes": graph.number_of_nodes(),
                "source_edges": graph.number_of_edges(),
                "source_hyperedges": "",
                "source_incidences": "",
                "plotted_nodes": core.number_of_nodes(),
                "plotted_edges": core.number_of_edges(),
                "plotted_hyperedges": "",
                "plotted_incidences": "",
                "png": f"projection_static/{stem}.png",
                "svg": f"projection_static/{stem}.svg",
                "html": f"projection_interactive/{stem}.html",
                "selection_rule": f"top {args.top_nodes} nodes by weighted strength and top {args.top_edges} induced edges by weight",
            }
        )

    for path in sorted(source_root.glob("*_hypergraph.json")):
        identifier = path.name.replace("_hypergraph.json", "")
        payload = json.loads(path.read_text(encoding="utf-8"))
        counts = draw_xgi_native(
            payload=payload,
            output_base=xgi_root / f"{identifier}_xgi_hypergraph",
            label=labels[identifier],
            top_hyperedges=args.xgi_hyperedges,
            top_nodes=args.xgi_nodes,
        )
        inventory.append(
            {
                "translation_id": identifier,
                "translation": labels[identifier],
                "visualization": "xgi_native_hypergraph",
                "source_nodes": counts["source_nodes"],
                "source_edges": "",
                "source_hyperedges": counts["source_hyperedges"],
                "source_incidences": counts["source_incidences"],
                "plotted_nodes": counts["plotted_nodes"],
                "plotted_edges": "",
                "plotted_hyperedges": counts["plotted_hyperedges"],
                "plotted_incidences": counts["plotted_incidences"],
                "png": f"xgi_native/{identifier}_xgi_hypergraph.png",
                "svg": f"xgi_native/{identifier}_xgi_hypergraph.svg",
                "html": "",
                "selection_rule": f"top {args.xgi_hyperedges} target hyperedges and top {args.xgi_nodes} attributes by summed incidence weight",
            }
        )

    write_gallery(root, output_root, labels, inventory)
    print(
        json.dumps(
            {
                "projection_graphs": 12,
                "native_xgi_hypergraphs": 6,
                "png_files": len(list(output_root.rglob("*.png"))),
                "svg_files": len(list(output_root.rglob("*.svg"))),
                "interactive_html_files": len(list(output_root.rglob("*.html"))),
                "inventory_rows": len(inventory),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
