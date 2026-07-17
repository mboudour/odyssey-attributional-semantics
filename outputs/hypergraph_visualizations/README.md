# Hypergraph Visualization Gallery

This directory provides deterministic static, vector, and interactive views of every projection GraphML file, plus native XGI views of each target-as-hyperedge JSON artifact.

> The projection files are dense. Visualizations therefore show a documented weighted core for legibility; the original GraphML and hypergraph JSON files remain the complete machine-readable results.

## Visualization index

| Translation | Target projection | Attribute projection | Native XGI hypergraph |
|---|---|---|---|
| George Chapman (1616) | [PNG](projection_static/chapman_1616_target_projection.png) · [SVG](projection_static/chapman_1616_target_projection.svg) · [interactive](projection_interactive/chapman_1616_target_projection.html) | [PNG](projection_static/chapman_1616_attribute_projection.png) · [SVG](projection_static/chapman_1616_attribute_projection.svg) · [interactive](projection_interactive/chapman_1616_attribute_projection.html) | [PNG](xgi_native/chapman_1616_xgi_hypergraph.png) · [SVG](xgi_native/chapman_1616_xgi_hypergraph.svg) |
| Alexander Pope (1726) | [PNG](projection_static/pope_1726_target_projection.png) · [SVG](projection_static/pope_1726_target_projection.svg) · [interactive](projection_interactive/pope_1726_target_projection.html) | [PNG](projection_static/pope_1726_attribute_projection.png) · [SVG](projection_static/pope_1726_attribute_projection.svg) · [interactive](projection_interactive/pope_1726_attribute_projection.html) | [PNG](xgi_native/pope_1726_xgi_hypergraph.png) · [SVG](xgi_native/pope_1726_xgi_hypergraph.svg) |
| William Cowper (1791) | [PNG](projection_static/cowper_1791_target_projection.png) · [SVG](projection_static/cowper_1791_target_projection.svg) · [interactive](projection_interactive/cowper_1791_target_projection.html) | [PNG](projection_static/cowper_1791_attribute_projection.png) · [SVG](projection_static/cowper_1791_attribute_projection.svg) · [interactive](projection_interactive/cowper_1791_attribute_projection.html) | [PNG](xgi_native/cowper_1791_xgi_hypergraph.png) · [SVG](xgi_native/cowper_1791_xgi_hypergraph.svg) |
| S. H. Butcher and Andrew Lang (1879) | [PNG](projection_static/butcher_lang_1879_target_projection.png) · [SVG](projection_static/butcher_lang_1879_target_projection.svg) · [interactive](projection_interactive/butcher_lang_1879_target_projection.html) | [PNG](projection_static/butcher_lang_1879_attribute_projection.png) · [SVG](projection_static/butcher_lang_1879_attribute_projection.svg) · [interactive](projection_interactive/butcher_lang_1879_attribute_projection.html) | [PNG](xgi_native/butcher_lang_1879_xgi_hypergraph.png) · [SVG](xgi_native/butcher_lang_1879_xgi_hypergraph.svg) |
| Samuel Butler (1900) | [PNG](projection_static/butler_1900_target_projection.png) · [SVG](projection_static/butler_1900_target_projection.svg) · [interactive](projection_interactive/butler_1900_target_projection.html) | [PNG](projection_static/butler_1900_attribute_projection.png) · [SVG](projection_static/butler_1900_attribute_projection.svg) · [interactive](projection_interactive/butler_1900_attribute_projection.html) | [PNG](xgi_native/butler_1900_xgi_hypergraph.png) · [SVG](xgi_native/butler_1900_xgi_hypergraph.svg) |
| A. T. Murray (1919) | [PNG](projection_static/murray_1919_target_projection.png) · [SVG](projection_static/murray_1919_target_projection.svg) · [interactive](projection_interactive/murray_1919_target_projection.html) | [PNG](projection_static/murray_1919_attribute_projection.png) · [SVG](projection_static/murray_1919_attribute_projection.svg) · [interactive](projection_interactive/murray_1919_attribute_projection.html) | [PNG](xgi_native/murray_1919_xgi_hypergraph.png) · [SVG](xgi_native/murray_1919_xgi_hypergraph.svg) |

## Reading the figures

In projection figures, node size encodes weighted strength, edge width encodes shared-incidence weight, and node color encodes a weighted modularity community. The top weighted nodes are labeled. Interactive HTML files support hover inspection, dragging, zooming, and navigation controls.

In native XGI figures, blue circles represent normalized attributes. Amber hulls in the left panel and amber square markers in the right panel represent target hyperedges. The two panels display the same weighted core: XGI’s native hull representation and its bipartite incidence representation.

## Selection parameters

The exact source and plotted counts are recorded in [`visualization_inventory.csv`](visualization_inventory.csv). The renderer uses a fixed random seed and deterministic ranking rules. Reproduce all files with:

```bash
make visualize
```
