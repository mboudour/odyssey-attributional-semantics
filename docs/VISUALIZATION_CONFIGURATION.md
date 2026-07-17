# Visualization Configuration Guide

The file [`config/visualizations.json`](../config/visualizations.json) is the single user-editable control panel for projection and native XGI figures. The renderer reads this file at runtime; routine design changes do not require editing Python.

> **Ownership rule:** Visual design parameters are project decisions. Change the JSON configuration, generate a preview, inspect it, and run the full build only after the design is approved.

## Safe editing workflow

From the repository root, edit `config/visualizations.json` in any text editor. Generate only the configured sample translation with:

```bash
make preview-visualizations
```

The preview is written to `outputs/hypergraph_visualization_preview/` and does not replace the complete visualization gallery. After approval, regenerate the full gallery with:

```bash
make visualize
```

Validate the complete gallery with:

```bash
make validate-visualizations
```

## Gephi and PyVis outputs

The complete target and attribute projections remain in `outputs/hypergraphs/` as `*_projection.graphml`. These files are labeled **Gephi** in the generated gallery. Download the selected GraphML file, install [Gephi](https://gephi.org/), and open it with **File → Open**.

The renderer separately creates **PyVis** interactive projections in `outputs/hypergraph_visualizations/projection_pyvis/`. Each standalone HTML file uses the background and interaction settings from this configuration. Download the HTML file and open it locally in a web browser. PyVis node scaling, edge scaling, physics, stabilization, navigation buttons, keyboard controls, canvas dimensions, and colors are all editable below.

## Configuration sections

| Section | Controls |
|---|---|
| `theme` | Figure, panel, text, edge, border, attribute, hyperedge, and community colors |
| `typography` | Font family and title, subtitle, panel, label, legend, note, and interactive text sizes |
| `projection.selection` | Number of projection nodes and edges retained in the readable weighted core |
| `projection.layout` | Layout algorithm, iteration count, spacing scale, and backbone density |
| `projection.static_figure` | Physical figure dimensions, raster resolution, and layout margins |
| `projection.nodes` | Node-size mapping, border width, and opacity |
| `projection.edges` | Edge-width and opacity mappings |
| `projection.labels` | Label count, offset, weight, box style, and box colors |
| `projection.legend` | Legend visibility and location |
| `projection.interactive` | White-background PyVis canvas size, node and edge scaling, navigation, keyboard controls, physics, and stabilization |
| `xgi.selection` | Number of target hyperedges and attribute nodes, plus minimum retained hyperedge size |
| `xgi.figure` | XGI figure dimensions, raster resolution, and layout margins |
| `xgi.native_layout` | Native hull-panel layout algorithm, iterations, and spacing |
| `xgi.bipartite_layout` | Incidence-panel layout algorithm, iterations, and spacing |
| `xgi.attribute_nodes` | Attribute-node sizes and borders in both panels |
| `xgi.hyperedges` | Hull display, opacity, borders, markers, and incidence-line width |
| `xgi.labels` | Attribute-label limit and sizes, plus target-hyperedge label visibility |
| `preview` | Translation and plot types used for quick review |
| `output_formats` | PNG, SVG, and interactive HTML generation |
| `translation_overrides` | Optional per-translation parameter replacements |

## White-background example

The supplied configuration uses white figure and panel backgrounds:

```json
"theme": {
  "figure_background": "#ffffff",
  "panel_background": "#ffffff",
  "text_color": "#111827"
}
```

Colors accept standard hexadecimal values such as `#ffffff`. Numeric values must remain JSON numbers, Boolean switches must be `true` or `false`, and every string must remain enclosed in double quotes.

## Preview controls

The default preview uses Pope’s 1726 translation because it is one of the denser cases. Change the identifier in the `preview` section to any corpus identifier listed in `config/corpus.json`:

```json
"preview": {
  "translation_id": "pope_1726",
  "include_target_projection": true,
  "include_attribute_projection": true,
  "include_xgi": true,
  "output_directory": "outputs/hypergraph_visualization_preview"
}
```

## Per-translation overrides

Use `translation_overrides` when one translation needs different limits or styling. The override is merged into the general configuration only for that translation. For example:

```json
"translation_overrides": {
  "pope_1726": {
    "projection": {
      "labels": {
        "maximum_labels": 12
      }
    },
    "xgi": {
      "selection": {
        "top_hyperedges": 8
      }
    }
  }
}
```

Delete an override block to return that translation to the general settings.

## Selection versus appearance

The `selection` sections change which nodes, edges, or hyperedges appear in the readable view. Theme, typography, size, opacity, and layout sections change only presentation. The original GraphML and hypergraph JSON artifacts remain the complete machine-readable results regardless of visualization settings.
