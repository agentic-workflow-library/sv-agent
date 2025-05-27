#!/usr/bin/env python3
"""Generate a visual diagram of the Ploidy Estimation workflow."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import matplotlib.lines as mlines

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(5, 9.5, 'Ploidy Estimation Workflow', 
        fontsize=16, fontweight='bold', ha='center')

# Input files
input_box = FancyBboxPatch((0.5, 7), 3, 1.2, 
                          boxstyle="round,pad=0.1",
                          facecolor='lightblue', 
                          edgecolor='darkblue',
                          linewidth=2)
ax.add_patch(input_box)
ax.text(2, 7.6, 'Inputs:', fontweight='bold', ha='center')
ax.text(2, 7.3, 'bincov_matrix.bed.gz', fontsize=9, ha='center')

# BuildPloidyMatrix task
build_box = FancyBboxPatch((1, 4.5), 3.5, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor='lightgreen',
                          edgecolor='darkgreen',
                          linewidth=2)
ax.add_patch(build_box)
ax.text(2.75, 5.5, 'BuildPloidyMatrix', fontweight='bold', ha='center')
ax.text(2.75, 5.2, 'Aggregates coverage', fontsize=9, ha='center')
ax.text(2.75, 4.9, 'to 1Mb bins', fontsize=9, ha='center')

# PloidyScore task
score_box = FancyBboxPatch((5.5, 4.5), 3.5, 1.5,
                          boxstyle="round,pad=0.1",
                          facecolor='lightcoral',
                          edgecolor='darkred',
                          linewidth=2)
ax.add_patch(score_box)
ax.text(7.25, 5.5, 'PloidyScore', fontweight='bold', ha='center')
ax.text(7.25, 5.2, 'Estimates ploidy', fontsize=9, ha='center')
ax.text(7.25, 4.9, 'Generates plots', fontsize=9, ha='center')

# Output files
output1_box = FancyBboxPatch((0.5, 1.5), 3.5, 1,
                            boxstyle="round,pad=0.1",
                            facecolor='lightyellow',
                            edgecolor='orange',
                            linewidth=2)
ax.add_patch(output1_box)
ax.text(2.25, 2, 'ploidy_matrix.bed.gz', fontsize=9, ha='center')

output2_box = FancyBboxPatch((6, 1.5), 3.5, 1,
                            boxstyle="round,pad=0.1",
                            facecolor='lightyellow',
                            edgecolor='orange',
                            linewidth=2)
ax.add_patch(output2_box)
ax.text(7.75, 2, 'ploidy_plots.tar.gz', fontsize=9, ha='center')

# Arrows
# Input to BuildPloidyMatrix
ax.arrow(2, 7, 0, -0.8, head_width=0.15, head_length=0.1, 
         fc='black', ec='black')

# BuildPloidyMatrix to PloidyScore
ax.arrow(4.5, 5.25, 0.9, 0, head_width=0.15, head_length=0.1,
         fc='black', ec='black')

# BuildPloidyMatrix to output
ax.arrow(2.75, 4.5, 0, -1.8, head_width=0.15, head_length=0.1,
         fc='black', ec='black', linestyle='--')

# PloidyScore to output
ax.arrow(7.25, 4.5, 0, -1.8, head_width=0.15, head_length=0.1,
         fc='black', ec='black')

# Docker containers (side annotations)
ax.text(0.2, 5.25, 'sv-base-mini', fontsize=8, rotation=90, va='center',
        style='italic', color='gray')
ax.text(9.8, 5.25, 'sv-pipeline-qc', fontsize=8, rotation=270, va='center',
        style='italic', color='gray')

# Legend
legend_elements = [
    mlines.Line2D([0], [0], color='darkblue', lw=2, 
                  label='Input Data', marker='s', markersize=8,
                  markerfacecolor='lightblue', linestyle=''),
    mlines.Line2D([0], [0], color='darkgreen', lw=2,
                  label='Processing Step', marker='s', markersize=8,
                  markerfacecolor='lightgreen', linestyle=''),
    mlines.Line2D([0], [0], color='orange', lw=2,
                  label='Output File', marker='s', markersize=8,
                  markerfacecolor='lightyellow', linestyle='')
]
ax.legend(handles=legend_elements, loc='lower center', ncol=3, 
          bbox_to_anchor=(0.5, -0.1))

# Save figure
plt.tight_layout()
plt.savefig('workflow_diagram.png', dpi=300, bbox_inches='tight')
plt.savefig('workflow_diagram.pdf', bbox_inches='tight')
print("Workflow diagram saved as workflow_diagram.png and workflow_diagram.pdf")