# Gephi, PyVis, and XGI Visualization Gallery

All appearance, layout, selection, and interaction settings are controlled by [`config/visualizations.json`](../../config/visualizations.json).

## Gephi projection files

The GraphML files are the complete projection networks intended for **Gephi** or another GraphML-compatible desktop application. Download a `.graphml` file first, install [Gephi](https://gephi.org/), and open the downloaded file with **File → Open**. These files are data sources, not browser-based interactive pages.

| Translation | Gephi target projection | Gephi attribute projection |
|---|---|---|
| George Chapman (1616) | [Download Gephi GraphML](../hypergraphs/chapman_1616_target_projection.graphml) | [Download Gephi GraphML](../hypergraphs/chapman_1616_attribute_projection.graphml) |
| Alexander Pope (1726) | [Download Gephi GraphML](../hypergraphs/pope_1726_target_projection.graphml) | [Download Gephi GraphML](../hypergraphs/pope_1726_attribute_projection.graphml) |
| William Cowper (1791) | [Download Gephi GraphML](../hypergraphs/cowper_1791_target_projection.graphml) | [Download Gephi GraphML](../hypergraphs/cowper_1791_attribute_projection.graphml) |
| S. H. Butcher and Andrew Lang (1879) | [Download Gephi GraphML](../hypergraphs/butcher_lang_1879_target_projection.graphml) | [Download Gephi GraphML](../hypergraphs/butcher_lang_1879_attribute_projection.graphml) |
| Samuel Butler (1900) | [Download Gephi GraphML](../hypergraphs/butler_1900_target_projection.graphml) | [Download Gephi GraphML](../hypergraphs/butler_1900_attribute_projection.graphml) |
| A. T. Murray (1919) | [Download Gephi GraphML](../hypergraphs/murray_1919_target_projection.graphml) | [Download Gephi GraphML](../hypergraphs/murray_1919_attribute_projection.graphml) |

## PyVis interactive projections

The HTML files below are standalone **PyVis** visualizations. Download an `.html` file and open it locally in a web browser. Hover over nodes and edges, drag nodes, zoom, and use the navigation controls configured in `config/visualizations.json`.

| Translation | PyVis target projection | PyVis attribute projection |
|---|---|---|
| George Chapman (1616) | [Download PyVis HTML](projection_pyvis/chapman_1616_target_projection.html) | [Download PyVis HTML](projection_pyvis/chapman_1616_attribute_projection.html) |
| Alexander Pope (1726) | [Download PyVis HTML](projection_pyvis/pope_1726_target_projection.html) | [Download PyVis HTML](projection_pyvis/pope_1726_attribute_projection.html) |
| William Cowper (1791) | [Download PyVis HTML](projection_pyvis/cowper_1791_target_projection.html) | [Download PyVis HTML](projection_pyvis/cowper_1791_attribute_projection.html) |
| S. H. Butcher and Andrew Lang (1879) | [Download PyVis HTML](projection_pyvis/butcher_lang_1879_target_projection.html) | [Download PyVis HTML](projection_pyvis/butcher_lang_1879_attribute_projection.html) |
| Samuel Butler (1900) | [Download PyVis HTML](projection_pyvis/butler_1900_target_projection.html) | [Download PyVis HTML](projection_pyvis/butler_1900_attribute_projection.html) |
| A. T. Murray (1919) | [Download PyVis HTML](projection_pyvis/murray_1919_target_projection.html) | [Download PyVis HTML](projection_pyvis/murray_1919_attribute_projection.html) |

## Static projections and native XGI hypergraphs

| Translation | Static target projection | Static attribute projection | Native XGI hypergraph |
|---|---|---|---|
| George Chapman (1616) | [PNG](projection_static/chapman_1616_target_projection.png) · [SVG](projection_static/chapman_1616_target_projection.svg) | [PNG](projection_static/chapman_1616_attribute_projection.png) · [SVG](projection_static/chapman_1616_attribute_projection.svg) | [PNG](xgi_native/chapman_1616_xgi_hypergraph.png) · [SVG](xgi_native/chapman_1616_xgi_hypergraph.svg) |
| Alexander Pope (1726) | [PNG](projection_static/pope_1726_target_projection.png) · [SVG](projection_static/pope_1726_target_projection.svg) | [PNG](projection_static/pope_1726_attribute_projection.png) · [SVG](projection_static/pope_1726_attribute_projection.svg) | [PNG](xgi_native/pope_1726_xgi_hypergraph.png) · [SVG](xgi_native/pope_1726_xgi_hypergraph.svg) |
| William Cowper (1791) | [PNG](projection_static/cowper_1791_target_projection.png) · [SVG](projection_static/cowper_1791_target_projection.svg) | [PNG](projection_static/cowper_1791_attribute_projection.png) · [SVG](projection_static/cowper_1791_attribute_projection.svg) | [PNG](xgi_native/cowper_1791_xgi_hypergraph.png) · [SVG](xgi_native/cowper_1791_xgi_hypergraph.svg) |
| S. H. Butcher and Andrew Lang (1879) | [PNG](projection_static/butcher_lang_1879_target_projection.png) · [SVG](projection_static/butcher_lang_1879_target_projection.svg) | [PNG](projection_static/butcher_lang_1879_attribute_projection.png) · [SVG](projection_static/butcher_lang_1879_attribute_projection.svg) | [PNG](xgi_native/butcher_lang_1879_xgi_hypergraph.png) · [SVG](xgi_native/butcher_lang_1879_xgi_hypergraph.svg) |
| Samuel Butler (1900) | [PNG](projection_static/butler_1900_target_projection.png) · [SVG](projection_static/butler_1900_target_projection.svg) | [PNG](projection_static/butler_1900_attribute_projection.png) · [SVG](projection_static/butler_1900_attribute_projection.svg) | [PNG](xgi_native/butler_1900_xgi_hypergraph.png) · [SVG](xgi_native/butler_1900_xgi_hypergraph.svg) |
| A. T. Murray (1919) | [PNG](projection_static/murray_1919_target_projection.png) · [SVG](projection_static/murray_1919_target_projection.svg) | [PNG](projection_static/murray_1919_attribute_projection.png) · [SVG](projection_static/murray_1919_attribute_projection.svg) | [PNG](xgi_native/murray_1919_xgi_hypergraph.png) · [SVG](xgi_native/murray_1919_xgi_hypergraph.svg) |

## User-controlled regeneration

This gallery was generated in **full** mode. Edit `config/visualizations.json`, then run:

```bash
make visualize
```

The exact source and plotted counts are recorded in [`visualization_inventory.csv`](visualization_inventory.csv).
