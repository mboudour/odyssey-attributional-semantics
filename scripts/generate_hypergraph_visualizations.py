#!/usr/bin/env python3
"""Generate configurable Gephi, PyVis, projection, and native XGI views."""

from __future__ import annotations

import argparse
import copy
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--config", type=Path, default=None, help="Visualization JSON; defaults to config/visualizations.json")
    parser.add_argument("--mode", choices=("full", "preview"), default="full")
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--translation", action="append", default=[], help="Restrict generation to one or more translation IDs")
    return parser.parse_args()


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def load_config(root: Path, config_path: Path | None) -> dict[str, Any]:
    path = config_path or root / "config" / "visualizations.json"
    if not path.is_absolute():
        path = root / path
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["_config_path"] = str(path)
    return payload


def config_for_translation(config: dict[str, Any], identifier: str) -> dict[str, Any]:
    override = config.get("translation_overrides", {}).get(identifier, {})
    return deep_merge(config, override)


def load_translation_labels(root: Path) -> dict[str, str]:
    payload = json.loads((root / "config" / "corpus.json").read_text(encoding="utf-8"))
    return {item["id"]: f"{item['translator']} ({item['year']})" for item in payload["translations"]}


def chosen_translations(args: argparse.Namespace, config: dict[str, Any], labels: dict[str, str]) -> list[str]:
    if args.translation:
        requested = args.translation
    elif args.mode == "preview":
        requested = [config["preview"]["translation_id"]]
    else:
        configured = config.get("translations", ["all"])
        requested = list(labels) if "all" in configured else configured
    unknown = sorted(set(requested) - set(labels))
    if unknown:
        raise ValueError(f"Unknown translation IDs: {', '.join(unknown)}")
    return [identifier for identifier in labels if identifier in requested]


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
        return {str(node): index for index, node in enumerate(sorted(graph.nodes, key=str))}
    communities = list(nx.community.greedy_modularity_communities(graph, weight="weight"))
    communities.sort(key=lambda group: (-len(group), min(str(item) for item in group)))
    return {
        str(node): index
        for index, group in enumerate(communities)
        for node in sorted(group, key=str)
    }


def general_layout(graph: nx.Graph, layout_config: dict[str, Any], seed: int) -> dict[Any, np.ndarray]:
    algorithm = layout_config.get("algorithm", "spring")
    if graph.number_of_nodes() <= 2 or algorithm == "circular":
        return nx.circular_layout(graph)
    if algorithm == "kamada_kawai":
        return nx.kamada_kawai_layout(graph, weight="weight")
    if algorithm == "spectral":
        return nx.spectral_layout(graph, weight="weight")
    if algorithm == "shell":
        return nx.shell_layout(graph)
    if algorithm != "spring":
        raise ValueError(f"Unsupported layout algorithm: {algorithm}")
    return nx.spring_layout(
        graph,
        seed=seed,
        weight="weight",
        iterations=int(layout_config["iterations"]),
        k=float(layout_config["k_scale"]) / math.sqrt(max(graph.number_of_nodes(), 1)),
    )


def projection_layout(graph: nx.Graph, layout_config: dict[str, Any], seed: int) -> dict[Any, np.ndarray]:
    if layout_config.get("algorithm", "spring") != "spring":
        return general_layout(graph, layout_config, seed)
    backbone = nx.maximum_spanning_tree(graph, weight="weight")
    edge_count = max(
        int(layout_config["backbone_extra_edges_minimum"]),
        graph.number_of_nodes() * int(layout_config["backbone_extra_edges_per_node"]),
    )
    extras = sorted(
        graph.edges(data=True),
        key=lambda item: (-float(item[2].get("weight", 1.0)), str(item[0]), str(item[1])),
    )[:edge_count]
    layout_input = backbone.copy()
    layout_input.add_edges_from(extras)
    return general_layout(layout_input, layout_config, seed)


def projection_kind(path: Path) -> str:
    return "attribute" if "attribute_projection" in path.name else "target"


def translation_id(path: Path) -> str:
    return path.name.replace("_attribute_projection.graphml", "").replace("_target_projection.graphml", "")


def set_matplotlib_style(config: dict[str, Any]) -> None:
    theme = config["theme"]
    typography = config["typography"]
    plt.style.use(theme["matplotlib_style"])
    plt.rcParams.update(
        {
            "font.family": typography["font_family"],
            "svg.fonttype": "none",
            "svg.hashsalt": "odyssey-attribution-v1",
        }
    )


def save_figure(figure: plt.Figure, output_base: Path, config: dict[str, Any], dpi: int) -> None:
    formats = config["output_formats"]
    if formats.get("png", True):
        figure.savefig(output_base.with_suffix(".png"), dpi=dpi, facecolor=figure.get_facecolor(), bbox_inches="tight")
    if formats.get("svg", True):
        figure.savefig(
            output_base.with_suffix(".svg"),
            facecolor=figure.get_facecolor(),
            bbox_inches="tight",
            metadata={"Date": None},
        )


def draw_projection_static(
    graph: nx.Graph,
    source_graph: nx.Graph,
    source_path: Path,
    output_base: Path,
    label: str,
    strengths: dict[str, float],
    config: dict[str, Any],
) -> None:
    theme = config["theme"]
    typography = config["typography"]
    projection = config["projection"]
    figure_config = projection["static_figure"]
    nodes_config = projection["nodes"]
    edges_config = projection["edges"]
    labels_config = projection["labels"]
    palette = theme["community_palette"]
    set_matplotlib_style(config)
    figure, axis = plt.subplots(
        figsize=(figure_config["width_inches"], figure_config["height_inches"]),
        facecolor=theme["figure_background"],
    )
    axis.set_facecolor(theme["panel_background"])
    axis.axis("off")

    positions = projection_layout(graph, projection["layout"], int(config["seed"]))
    communities = community_map(graph)
    plotted_strength = np.asarray([strengths[str(node)] for node in graph.nodes], dtype=float)
    maximum_strength = float(plotted_strength.max()) if len(plotted_strength) else 1.0
    node_sizes = [
        float(nodes_config["size_minimum"])
        + float(nodes_config["size_scale"])
        * (strengths[str(node)] / maximum_strength) ** float(nodes_config["size_exponent"])
        for node in graph.nodes
    ]
    node_colors = [palette[communities[str(node)] % len(palette)] for node in graph.nodes]

    edge_weights = np.asarray([float(data.get("weight", 1.0)) for _, _, data in graph.edges(data=True)], dtype=float)
    maximum_edge = float(edge_weights.max()) if len(edge_weights) else 1.0
    for left, right, data in graph.edges(data=True):
        relative_weight = float(data.get("weight", 1.0)) / maximum_edge
        width = float(edges_config["width_minimum"]) + float(edges_config["width_scale"]) * relative_weight ** float(edges_config["width_exponent"])
        alpha = float(edges_config["opacity_minimum"]) + float(edges_config["opacity_scale"]) * relative_weight ** float(edges_config["opacity_exponent"])
        nx.draw_networkx_edges(
            graph,
            positions,
            edgelist=[(left, right)],
            width=width,
            alpha=alpha,
            edge_color=theme["edge_color"],
            ax=axis,
        )
    nx.draw_networkx_nodes(
        graph,
        positions,
        node_size=node_sizes,
        node_color=node_colors,
        linewidths=float(nodes_config["border_width"]),
        edgecolors=theme["border_color"],
        alpha=float(nodes_config["opacity"]),
        ax=axis,
    )

    label_nodes = sorted(graph.nodes, key=lambda node: (-strengths[str(node)], str(node)))[
        : int(labels_config["maximum_labels"])
    ]
    label_positions = {
        node: positions[node] + np.array([0.0, float(labels_config["vertical_offset"])])
        for node in label_nodes
    }
    nx.draw_networkx_labels(
        graph,
        label_positions,
        labels={node: str(node) for node in label_nodes},
        font_size=float(typography["label_size"]),
        font_color=theme["text_color"],
        font_weight=labels_config["font_weight"],
        bbox={
            "boxstyle": labels_config["box_style"],
            "facecolor": labels_config["box_background"],
            "edgecolor": labels_config["box_border"],
            "alpha": float(labels_config["box_opacity"]),
        },
        ax=axis,
    )

    title_kind = "Attribute projection" if projection_kind(source_path) == "attribute" else "Target projection"
    figure.suptitle(
        f"{label} — {title_kind}",
        x=0.055,
        y=0.965,
        ha="left",
        fontsize=float(typography["title_size"]),
        fontweight="bold",
        color=theme["text_color"],
    )
    axis.set_title(
        f"Weighted core view: {graph.number_of_nodes()} of {source_graph.number_of_nodes()} nodes; "
        f"{graph.number_of_edges()} of {source_graph.number_of_edges()} edges",
        loc="left",
        fontsize=float(typography["subtitle_size"]),
        color=theme["muted_text_color"],
        pad=18,
    )
    if projection["legend"]["show"]:
        legend = [
            Line2D([0], [0], marker="o", color="none", markerfacecolor=palette[0], markeredgecolor=theme["border_color"], markersize=10, label="Node size = weighted strength"),
            Line2D([0], [0], color=theme["edge_color"], linewidth=2.5, label="Edge width = shared-incidence weight"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=palette[1], markersize=10, label="Color = modularity community"),
        ]
        axis.legend(
            handles=legend,
            loc=projection["legend"]["location"],
            frameon=False,
            labelcolor=theme["text_color"],
            fontsize=float(typography["legend_size"]),
        )
    figure.text(
        0.055,
        0.025,
        "Configurable weighted-core visualization; the complete Gephi GraphML remains the canonical projection.",
        color=theme["muted_text_color"],
        fontsize=float(typography["note_size"]),
    )
    figure.tight_layout(rect=figure_config["tight_layout_rect"])
    save_figure(figure, output_base, config, int(figure_config["dpi"]))
    plt.close(figure)


def draw_projection_pyvis(
    graph: nx.Graph,
    source_graph: nx.Graph,
    source_path: Path,
    output_path: Path,
    label: str,
    strengths: dict[str, float],
    config: dict[str, Any],
) -> None:
    if not config["output_formats"].get("interactive_html", True):
        return
    theme = config["theme"]
    typography = config["typography"]
    interactive = config["projection"]["interactive"]
    palette = theme["community_palette"]
    communities = community_map(graph)
    maximum_strength = max((strengths[str(node)] for node in graph.nodes), default=1.0)
    maximum_edge = max((float(data.get("weight", 1.0)) for _, _, data in graph.edges(data=True)), default=1.0)
    network = Network(
        height=interactive["height"],
        width=interactive["width"],
        bgcolor=theme["figure_background"],
        font_color=theme["text_color"],
        directed=False,
        cdn_resources="in_line",
    )
    for node in sorted(graph.nodes, key=str):
        strength = strengths[str(node)]
        network.add_node(
            str(node),
            label=str(node),
            title=f"<b>{node}</b><br>Weighted strength: {strength:.3f}<br>Displayed degree: {graph.degree(node)}",
            value=float(interactive["node_size_minimum"]) + float(interactive["node_size_scale"]) * math.sqrt(strength / maximum_strength),
            color={"background": palette[communities[str(node)] % len(palette)], "border": theme["border_color"]},
            borderWidth=float(interactive["node_border_width"]),
        )
    for left, right, data in sorted(graph.edges(data=True), key=lambda item: (str(item[0]), str(item[1]))):
        weight = float(data.get("weight", 1.0))
        network.add_edge(
            str(left),
            str(right),
            value=float(interactive["edge_width_minimum"]) + float(interactive["edge_width_scale"]) * (weight / maximum_edge) ** float(interactive["edge_width_exponent"]),
            title=f"Shared-incidence weight: {weight:.3f}",
            color={"color": theme["edge_color"], "opacity": float(interactive["edge_opacity"])},
        )
    network.set_options(
        json.dumps(
            {
                "nodes": {"font": {"color": theme["text_color"], "size": interactive["label_size"], "face": typography["font_family"]}},
                "edges": {"smooth": {"enabled": False}, "selectionWidth": 2},
                "interaction": {
                    "hover": True,
                    "navigationButtons": interactive["navigation_buttons"],
                    "keyboard": interactive["keyboard_controls"],
                },
                "physics": {
                    "enabled": interactive["physics_enabled"],
                    "solver": interactive["physics_solver"],
                    "forceAtlas2Based": {
                        "gravitationalConstant": interactive["gravitational_constant"],
                        "centralGravity": interactive["central_gravity"],
                        "springLength": interactive["spring_length"],
                        "springConstant": interactive["spring_constant"],
                        "damping": interactive["damping"],
                        "avoidOverlap": interactive["avoid_overlap"],
                    },
                    "stabilization": {
                        "enabled": True,
                        "iterations": interactive["stabilization_iterations"],
                        "updateInterval": interactive["stabilization_update_interval"],
                    },
                },
            }
        )
    )
    network.write_html(str(output_path), notebook=False, open_browser=False)
    html = output_path.read_text(encoding="utf-8")
    title = f"{label} — PyVis interactive {projection_kind(source_path)} projection"
    explanatory = (
        f"<div data-renderer='PyVis' style='font-family:{typography['font_family']},sans-serif;color:{theme['text_color']};"
        f"background:{theme['figure_background']};padding:14px 18px 10px;'>"
        f"<h1 style='font-size:{typography['interactive_title_size']}px;line-height:1.2;margin:0 0 7px 0;color:{theme['text_color']};'>{title}</h1>"
        f"<p style='font-size:{typography['interactive_text_size']}px;line-height:1.4;margin:0;color:{theme['muted_text_color']};'>"
        f"PyVis weighted core: {graph.number_of_nodes()} of {source_graph.number_of_nodes()} nodes and "
        f"{graph.number_of_edges()} of {source_graph.number_of_edges()} edges. Hover for weights, drag nodes, zoom, and use the navigation controls."
        "</p></div>"
    )
    html = html.replace("<body>", f"<body style='margin:0;background:{theme['figure_background']};'>{explanatory}", 1)
    output_path.write_text(html, encoding="utf-8")


def weighted_hypergraph_core(
    payload: dict[str, Any],
    top_hyperedges: int,
    top_nodes: int,
    minimum_hyperedge_size: int,
) -> tuple[dict[str, set[str]], dict[str, float], dict[str, float]]:
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
    hyperedges = {target: members for target, members in hyperedges.items() if len(members) >= minimum_hyperedge_size}
    retained_nodes = {node for members in hyperedges.values() for node in members}
    return hyperedges, {node: node_weights[node] for node in retained_nodes}, edge_weights


def draw_xgi_native(payload: dict[str, Any], output_base: Path, label: str, config: dict[str, Any]) -> dict[str, int]:
    theme = config["theme"]
    typography = config["typography"]
    xgi_config = config["xgi"]
    selection = xgi_config["selection"]
    figure_config = xgi_config["figure"]
    node_config = xgi_config["attribute_nodes"]
    edge_config = xgi_config["hyperedges"]
    label_config = xgi_config["labels"]
    hyperedge_dictionary, node_weights, edge_weights = weighted_hypergraph_core(
        payload,
        int(selection["top_hyperedges"]),
        int(selection["top_nodes"]),
        int(selection["minimum_hyperedge_size"]),
    )
    canonical_hyperedges = {edge: sorted(hyperedge_dictionary[edge]) for edge in sorted(hyperedge_dictionary)}
    hypergraph = xgi.Hypergraph(canonical_hyperedges)
    set_matplotlib_style(config)
    figure, axes = plt.subplots(
        1,
        2,
        figsize=(figure_config["width_inches"], figure_config["height_inches"]),
        facecolor=theme["figure_background"],
    )
    for axis in axes:
        axis.set_facecolor(theme["panel_background"])
        axis.axis("off")

    node_order = sorted(hypergraph.nodes, key=lambda node: (-node_weights[str(node)], str(node)))
    weighted_projection = nx.Graph()
    weighted_projection.add_nodes_from(node_order)
    for edge in sorted(canonical_hyperedges):
        for left, right in combinations(canonical_hyperedges[edge], 2):
            previous = float(weighted_projection.get_edge_data(left, right, {}).get("weight", 0.0))
            weighted_projection.add_edge(left, right, weight=previous + edge_weights[edge])
    native_positions = general_layout(weighted_projection, xgi_config["native_layout"], int(config["seed"]))
    label_nodes = set(node_order[: int(label_config["maximum_attribute_labels"])])
    node_labels = {node: str(node) for node in label_nodes}
    xgi.draw(
        hypergraph,
        pos=native_positions,
        ax=axes[0],
        node_fc=theme["attribute_color"],
        node_ec=theme["border_color"],
        node_lw=float(node_config["border_width"]),
        node_size=float(node_config["size"]),
        edge_fc=theme["hyperedge_color"],
        edge_ec=theme["hyperedge_border_color"],
        edge_lw=float(edge_config["border_width"]),
        alpha=float(edge_config["hull_opacity"]),
        hull=bool(edge_config["hull"]),
        node_labels=node_labels,
        hyperedge_labels=False,
        font_size_nodes=float(label_config["attribute_label_size"]),
        font_color_nodes=theme["text_color"],
    )
    axes[0].set_title(
        "XGI native hyperedge-hull view",
        loc="left",
        fontsize=float(typography["panel_title_size"]),
        fontweight="bold",
        color=theme["text_color"],
        pad=14,
    )

    incidence_graph = nx.Graph()
    node_keys = [("attribute", node) for node in node_order]
    edge_order = sorted(canonical_hyperedges, key=lambda edge: (-edge_weights[edge], edge))
    edge_keys = [("target", edge) for edge in edge_order]
    incidence_graph.add_nodes_from(node_keys)
    incidence_graph.add_nodes_from(edge_keys)
    for edge in edge_order:
        for node in canonical_hyperedges[edge]:
            incidence_graph.add_edge(("attribute", node), ("target", edge), weight=edge_weights[edge])
    incidence_positions = general_layout(incidence_graph, xgi_config["bipartite_layout"], int(config["seed"]))
    bipartite_positions = (
        {node: incidence_positions[("attribute", node)] for node in node_order},
        {edge: incidence_positions[("target", edge)] for edge in edge_order},
    )
    hyperedge_labels = {edge: str(edge) for edge in edge_order} if label_config["show_hyperedge_labels"] else False
    xgi.draw_bipartite(
        hypergraph,
        pos=bipartite_positions,
        ax=axes[1],
        node_fc=theme["attribute_color"],
        node_ec=theme["border_color"],
        node_lw=float(node_config["border_width"]),
        node_size=float(node_config["bipartite_size"]),
        edge_marker_fc=theme["hyperedge_color"],
        edge_marker_ec=theme["border_color"],
        edge_marker_lw=float(edge_config["bipartite_marker_border_width"]),
        edge_marker_size=float(edge_config["bipartite_marker_size"]),
        dyad_color=theme["edge_color"],
        dyad_lw=float(edge_config["incidence_line_width"]),
        node_labels=node_labels,
        hyperedge_labels=hyperedge_labels,
        font_size_nodes=float(label_config["bipartite_attribute_label_size"]),
        font_color_nodes=theme["text_color"],
    )
    axes[1].set_title(
        "XGI bipartite incidence view",
        loc="left",
        fontsize=float(typography["panel_title_size"]),
        fontweight="bold",
        color=theme["text_color"],
        pad=14,
    )

    total_incidences = sum(len(records) for records in payload["hyperedges"].values())
    figure.suptitle(
        f"{label} — Native target-as-hyperedge visualization",
        x=0.035,
        y=0.97,
        ha="left",
        fontsize=float(typography["title_size"]),
        fontweight="bold",
        color=theme["text_color"],
    )
    figure.text(
        0.035,
        0.925,
        f"Readable weighted core: {len(hypergraph.nodes)} of {len(payload['vertices'])} attribute nodes; "
        f"{len(hypergraph.edges)} of {len(payload['hyperedges'])} target hyperedges; "
        f"{sum(len(hypergraph.edges.members(edge)) for edge in hypergraph.edges)} of {total_incidences} incidences.",
        color=theme["muted_text_color"],
        fontsize=float(typography["subtitle_size"]),
    )
    figure.text(
        0.035,
        0.025,
        "Attribute circles and target hyperedges use the colors specified in config/visualizations.json.",
        color=theme["muted_text_color"],
        fontsize=float(typography["note_size"]),
    )
    figure.tight_layout(rect=figure_config["tight_layout_rect"])
    save_figure(figure, output_base, config, int(figure_config["dpi"]))
    plt.close(figure)
    return {
        "source_nodes": len(payload["vertices"]),
        "source_hyperedges": len(payload["hyperedges"]),
        "source_incidences": total_incidences,
        "plotted_nodes": len(hypergraph.nodes),
        "plotted_hyperedges": len(hypergraph.edges),
        "plotted_incidences": sum(len(hypergraph.edges.members(edge)) for edge in hypergraph.edges),
    }


def artifact_link(path: str, label: str) -> str:
    return f"[{label}]({path})" if path else "—"


def write_gallery(output_root: Path, labels: dict[str, str], rows: list[dict[str, Any]], config: dict[str, Any], mode: str) -> None:
    row_map = {(row["translation_id"], row["visualization"]): row for row in rows}
    identifiers = [identifier for identifier in labels if any(key[0] == identifier for key in row_map)]
    lines = [
        "# Gephi, PyVis, and XGI Visualization Gallery",
        "",
        "All appearance, layout, selection, and interaction settings are controlled by [`config/visualizations.json`](../../config/visualizations.json).",
        "",
        "## Gephi projection files",
        "",
        "The GraphML files are the complete projection networks intended for **Gephi** or another GraphML-compatible desktop application. Download a `.graphml` file first, install [Gephi](https://gephi.org/), and open the downloaded file with **File → Open**. These files are data sources, not browser-based interactive pages.",
        "",
        "| Translation | Gephi target projection | Gephi attribute projection |",
        "|---|---|---|",
    ]
    for identifier in identifiers:
        target_graphml = f"../hypergraphs/{identifier}_target_projection.graphml"
        attribute_graphml = f"../hypergraphs/{identifier}_attribute_projection.graphml"
        lines.append(f"| {labels[identifier]} | [Download Gephi GraphML]({target_graphml}) | [Download Gephi GraphML]({attribute_graphml}) |")
    lines.extend(
        [
            "",
            "## PyVis interactive projections",
            "",
            "The HTML files below are standalone **PyVis** visualizations. Download an `.html` file and open it locally in a web browser. Hover over nodes and edges, drag nodes, zoom, and use the navigation controls configured in `config/visualizations.json`.",
            "",
            "| Translation | PyVis target projection | PyVis attribute projection |",
            "|---|---|---|",
        ]
    )
    for identifier in identifiers:
        target = row_map.get((identifier, "target_projection"), {})
        attribute = row_map.get((identifier, "attribute_projection"), {})
        lines.append(
            f"| {labels[identifier]} | {artifact_link(target.get('html', ''), 'Download PyVis HTML')} "
            f"| {artifact_link(attribute.get('html', ''), 'Download PyVis HTML')} |"
        )
    lines.extend(
        [
            "",
            "## Static projections and native XGI hypergraphs",
            "",
            "| Translation | Static target projection | Static attribute projection | Native XGI hypergraph |",
            "|---|---|---|---|",
        ]
    )
    for identifier in identifiers:
        target = row_map.get((identifier, "target_projection"), {})
        attribute = row_map.get((identifier, "attribute_projection"), {})
        native = row_map.get((identifier, "xgi_native_hypergraph"), {})
        lines.append(
            f"| {labels[identifier]} "
            f"| {artifact_link(target.get('png', ''), 'PNG')} · {artifact_link(target.get('svg', ''), 'SVG')} "
            f"| {artifact_link(attribute.get('png', ''), 'PNG')} · {artifact_link(attribute.get('svg', ''), 'SVG')} "
            f"| {artifact_link(native.get('png', ''), 'PNG')} · {artifact_link(native.get('svg', ''), 'SVG')} |"
        )
    command = "make preview-visualizations" if mode == "preview" else "make visualize"
    lines.extend(
        [
            "",
            "## User-controlled regeneration",
            "",
            f"This gallery was generated in **{mode}** mode. Edit `config/visualizations.json`, then run:",
            "",
            "```bash",
            command,
            "```",
            "",
            "The exact source and plotted counts are recorded in [`visualization_inventory.csv`](visualization_inventory.csv).",
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
    config = load_config(root, args.config)
    labels = load_translation_labels(root)
    identifiers = chosen_translations(args, config, labels)
    source_root = root / "outputs" / "hypergraphs"
    if args.output_root:
        output_root = args.output_root if args.output_root.is_absolute() else root / args.output_root
    elif args.mode == "preview":
        output_root = root / config["preview"]["output_directory"]
    else:
        output_root = root / "outputs" / "hypergraph_visualizations"
    if output_root.exists():
        shutil.rmtree(output_root)
    static_root = output_root / "projection_static"
    pyvis_root = output_root / "projection_pyvis"
    xgi_root = output_root / "xgi_native"
    for directory in (static_root, pyvis_root, xgi_root):
        directory.mkdir(parents=True, exist_ok=True)

    inventory: list[dict[str, Any]] = []
    preview = config["preview"]
    for path in sorted(source_root.glob("*_projection.graphml")):
        identifier = translation_id(path)
        if identifier not in identifiers:
            continue
        kind = projection_kind(path)
        if args.mode == "preview" and not preview[f"include_{kind}_projection"]:
            continue
        local_config = config_for_translation(config, identifier)
        selection = local_config["projection"]["selection"]
        graph = nx.read_graphml(path)
        core, strengths = weighted_core(graph, int(selection["top_nodes"]), int(selection["top_edges"]))
        stem = path.stem
        draw_projection_static(core, graph, path, static_root / stem, labels[identifier], strengths, local_config)
        html_path = pyvis_root / f"{stem}.html"
        draw_projection_pyvis(core, graph, path, html_path, labels[identifier], strengths, local_config)
        inventory.append(
            {
                "translation_id": identifier,
                "translation": labels[identifier],
                "visualization": f"{kind}_projection",
                "renderer": "NetworkX/Matplotlib static; PyVis interactive; Gephi GraphML source",
                "source_nodes": graph.number_of_nodes(),
                "source_edges": graph.number_of_edges(),
                "source_hyperedges": "",
                "source_incidences": "",
                "plotted_nodes": core.number_of_nodes(),
                "plotted_edges": core.number_of_edges(),
                "plotted_hyperedges": "",
                "plotted_incidences": "",
                "gephi_graphml": f"../hypergraphs/{path.name}",
                "png": f"projection_static/{stem}.png" if local_config["output_formats"]["png"] else "",
                "svg": f"projection_static/{stem}.svg" if local_config["output_formats"]["svg"] else "",
                "html": f"projection_pyvis/{stem}.html" if local_config["output_formats"]["interactive_html"] else "",
                "selection_rule": f"top {selection['top_nodes']} nodes by weighted strength and top {selection['top_edges']} induced edges by weight",
            }
        )

    for path in sorted(source_root.glob("*_hypergraph.json")):
        identifier = path.name.replace("_hypergraph.json", "")
        if identifier not in identifiers or (args.mode == "preview" and not preview["include_xgi"]):
            continue
        local_config = config_for_translation(config, identifier)
        payload = json.loads(path.read_text(encoding="utf-8"))
        counts = draw_xgi_native(payload, xgi_root / f"{identifier}_xgi_hypergraph", labels[identifier], local_config)
        selection = local_config["xgi"]["selection"]
        inventory.append(
            {
                "translation_id": identifier,
                "translation": labels[identifier],
                "visualization": "xgi_native_hypergraph",
                "renderer": "XGI native hull and bipartite incidence",
                "source_nodes": counts["source_nodes"],
                "source_edges": "",
                "source_hyperedges": counts["source_hyperedges"],
                "source_incidences": counts["source_incidences"],
                "plotted_nodes": counts["plotted_nodes"],
                "plotted_edges": "",
                "plotted_hyperedges": counts["plotted_hyperedges"],
                "plotted_incidences": counts["plotted_incidences"],
                "gephi_graphml": "",
                "png": f"xgi_native/{identifier}_xgi_hypergraph.png" if local_config["output_formats"]["png"] else "",
                "svg": f"xgi_native/{identifier}_xgi_hypergraph.svg" if local_config["output_formats"]["svg"] else "",
                "html": "",
                "selection_rule": f"top {selection['top_hyperedges']} target hyperedges and top {selection['top_nodes']} attributes by summed incidence weight",
            }
        )

    write_gallery(output_root, labels, inventory, config, args.mode)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "translations": identifiers,
                "projection_graphs": sum(row["visualization"].endswith("_projection") for row in inventory),
                "native_xgi_hypergraphs": sum(row["visualization"] == "xgi_native_hypergraph" for row in inventory),
                "png_files": len(list(output_root.rglob("*.png"))),
                "svg_files": len(list(output_root.rglob("*.svg"))),
                "pyvis_html_files": len(list(output_root.rglob("*.html"))),
                "inventory_rows": len(inventory),
                "configuration": config["_config_path"],
                "output_root": str(output_root),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
