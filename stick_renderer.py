import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines
import numpy as np

class StickRenderer:
    """Standard VLSI Stick Diagram Renderer"""

    def __init__(self):
        # Standard VLSI colors
        self.COLOR_N_DIFF = '#228B22'      # Forest Green (N-diffusion)
        self.COLOR_P_DIFF = '#DAA520'      # Goldenrod (P-diffusion)
        self.COLOR_POLY = '#DC143C'        # Crimson (Polysilicon)
        self.COLOR_METAL = '#4169E1'       # Royal Blue (Metal 1)
        self.COLOR_CONTACT = 'black'

        # Dimensions (in lambda units, standard VLSI)
        self.LAMBDA = 0.5
        self.POLY_WIDTH = 0.5
        self.DIFF_HEIGHT = 2.0
        self.GATE_PITCH = 4.0              # Distance between poly gates
        self.METAL_WIDTH = 0.5

    def draw_layout(self, euler_path, pdn_graph, pun_graph):
        """Draw standard stick diagram"""
        self.fig, (self.ax_pun, self.ax_pdn) = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.suptitle('CMOS Stick Diagram', fontsize=14, fontweight='bold')

        if not euler_path:
            self.ax_pdn.text(0.5, 0.5, "No Euler Path Found", ha='center', va='center',
                           transform=self.ax_pdn.transAxes, fontsize=14)
            return self.fig

        self.euler_path = euler_path
        self.num_inputs = len(euler_path)
        self.width = (self.num_inputs + 2) * self.GATE_PITCH

        # Draw PUN (top) and PDN (bottom)
        self._draw_pun()
        self._draw_pdn()

        # Add legend
        self._add_legend()

        plt.tight_layout()
        return self.fig

    def _draw_pun(self):
        """Draw Pull-Up Network (PMOS) - top section"""
        ax = self.ax_pun
        ax.set_xlim(-1, self.width + 1)
        ax.set_ylim(-1, 8)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Pull-Up Network (PMOS)', fontsize=11, color=self.COLOR_P_DIFF)

        y_pdiff = 4.0
        y_vcc = 7.0

        # VCC rail (Metal)
        self._draw_metal_line(ax, -1, y_vcc, self.width + 2, label='VCC')

        # P-Diffusion strip
        self._draw_diffusion(ax, 0, y_pdiff, self.width, self.COLOR_P_DIFF, 'P-Diff')

        # Draw PMOS transistors based on Euler path
        self._draw_transistors(ax, euler_path, y_pdiff, is_pmos=True)

        # Connect to VCC
        self._connect_to_rail(ax, y_pdiff, y_vcc, 'VCC', is_pmos=True)

        # Label transistors (A, B, C...) on polysilicon
        self._label_gates(ax, euler_path, y_pdiff)

    def _draw_pdn(self):
        """Draw Pull-Down Network (NMOS) - bottom section"""
        ax = self.ax_pdn
        ax.set_xlim(-1, self.width + 1)
        ax.set_ylim(-1, 5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Pull-Down Network (NMOS)', fontsize=11, color=self.COLOR_N_DIFF)

        y_ndiff = 1.0
        y_gnd = 0.0

        # GND rail (Metal)
        self._draw_metal_line(ax, -1, y_gnd, self.width + 2, label='GND')

        # N-Diffusion strip
        self._draw_diffusion(ax, 0, y_ndiff, self.width, self.COLOR_N_DIFF, 'N-Diff')

        # Draw NMOS transistors based on Euler path
        self._draw_transistors(ax, euler_path, y_ndiff, is_pmos=False)

        # Connect to GND
        self._connect_to_rail(ax, y_ndiff, y_gnd, 'GND', is_pmos=False)

        # Label output (Y)
        ax.text(self.width + 0.5, 2.5, 'Y', fontsize=14, fontweight='bold',
               color='black', va='center')

        # Draw output wire
        ax.plot([self.width, self.width], [2.0, 2.5], color=self.COLOR_METAL, linewidth=2)

        # Label transistors
        self._label_gates(ax, euler_path, y_ndiff)

    def _draw_diffusion(self, ax, x, y, width, color, label):
        """Draw diffusion strip"""
        rect = patches.Rectangle((x, y), width, self.DIFF_HEIGHT,
                                 linewidth=1.5, edgecolor='black',
                                 facecolor=color, alpha=0.6)
        ax.add_patch(rect)
        ax.text(x - 0.3, y + self.DIFF_HEIGHT/2, label, fontsize=9,
               va='center', ha='right', color=color, fontweight='bold')

    def _draw_metal_line(self, ax, x, y, width, label=None):
        """Draw metal wire (VCC, GND, Output)"""
        rect = patches.Rectangle((x, y), width, self.METAL_WIDTH,
                                 linewidth=1.5, edgecolor='black',
                                 facecolor=self.COLOR_METAL, alpha=0.8)
        ax.add_patch(rect)
        if label:
            ax.text(x - 0.3, y + self.METAL_WIDTH/2, label, fontsize=9,
                   va='center', ha='right', color=self.COLOR_METAL, fontweight='bold')

    def _draw_transistors(self, ax, euler_path, y_diff, is_pmos=True):
        """Draw transistor gates as polysilicon crossing diffusion"""
        color = self.COLOR_POLY
        transistor_color = self.COLOR_P_DIFF if is_pmos else self.COLOR_N_DIFF

        for i, label in enumerate(euler_path):
            x = (i + 1.5) * self.GATE_PITCH

            # Draw vertical polysilicon line (the gate)
            ax.plot([x, x], [y_diff - 0.5, y_diff + self.DIFF_HEIGHT + 0.5],
                   color=color, linewidth=self.POLY_WIDTH * 2, solid_capstyle='round')

            # Draw transistor symbol (gate crossover)
            # Standard transistor symbol: diffusion meets poly at right angles
            gate_height = self.DIFF_HEIGHT

            # Add small rectangle to show gate area
            gate = patches.Rectangle((x - self.POLY_WIDTH, y_diff),
                                     self.POLY_WIDTH * 2, gate_height,
                                     linewidth=1, edgecolor=color,
                                     facecolor=color, alpha=0.8)
            ax.add_patch(gate)

    def _label_gates(self, ax, euler_path, y_diff):
        """Label input variables above gates"""
        for i, label in enumerate(euler_path):
            x = (i + 1.5) * self.GATE_PITCH
            ax.text(x, y_diff + self.DIFF_HEIGHT + 0.8, label,
                   fontsize=12, fontweight='bold', color=self.COLOR_POLY,
                   ha='center', va='bottom')

    def _connect_to_rail(self, ax, y_diff, y_rail, rail_name, is_pmos=True):
        """Connect diffusion to VCC/GND rail with contacts"""
        # Find where poly gates are
        positions = [(i + 1.5) * self.GATE_PITCH for i in range(len(self.euler_path))]

        # Connect left end to rail
        x_left = positions[0] - self.GATE_PITCH / 2
        self._draw_contact(ax, x_left, y_diff)
        self._draw_via(ax, x_left, y_diff, y_rail)

        # Connect right end to rail (or output)
        x_right = positions[-1] + self.GATE_PITCH / 2

        if is_pmos:
            # PUN right side connects to output (middle)
            y_out = 4.5
            ax.text(self.width + 0.5, y_out, 'Y', fontsize=14, fontweight='bold', va='center')
            ax.plot([self.width, self.width], [y_diff + self.DIFF_HEIGHT/2, y_out],
                   color=self.COLOR_METAL, linewidth=2)
            self._draw_via(ax, self.width, y_diff + self.DIFF_HEIGHT/2, y_out)
        else:
            # PDN right side connects to output
            y_out = 2.5
            self._draw_via(ax, self.width, y_diff + self.DIFF_HEIGHT/2, y_out)

        # Draw contacts between transistors (showing series connection)
        for x in positions[1:-1]:
            self._draw_contact(ax, x, y_diff)

    def _draw_contact(self, ax, x, y):
        """Draw contact (diffusion to metal) - square with X"""
        size = 0.25
        # Square
        rect = patches.Rectangle((x - size, y - size), size * 2, size * 2,
                                 linewidth=1, edgecolor='black', facecolor='white')
        ax.add_patch(rect)
        # X mark
        ax.plot([x - size, x + size], [y - size, y + size], 'k-', linewidth=1)
        ax.plot([x - size, x + size], [y + size, y - size], 'k-', linewidth=1)

    def _draw_via(self, ax, x, y1, y2):
        """Draw via (metal to metal connection)"""
        if abs(y2 - y1) < 0.1:
            return
        # Draw vertical metal connection
        ax.plot([x, x], [y1, y2], color=self.COLOR_METAL, linewidth=2)
        # Via symbol (small square)
        size = 0.15
        mid_y = (y1 + y2) / 2
        rect = patches.Rectangle((x - size, mid_y - size), size * 2, size * 2,
                                 linewidth=1, edgecolor='black', facecolor=self.COLOR_METAL)
        ax.add_patch(rect)

    def _add_legend(self):
        """Add color legend"""
        legend_elements = [
            patches.Patch(facecolor=self.COLOR_POLY, alpha=0.8, label='Polysilicon (Gate)'),
            patches.Patch(facecolor=self.COLOR_N_DIFF, alpha=0.6, label='N-Diffusion (NMOS)'),
            patches.Patch(facecolor=self.COLOR_P_DIFF, alpha=0.6, label='P-Diffusion (PMOS)'),
            patches.Patch(facecolor=self.COLOR_METAL, alpha=0.8, label='Metal-1'),
            mlines.Line2D([0], [0], color='black', marker='x', linestyle='None',
                         markersize=8, label='Contact/Via')
        ]
        self.fig.legend(handles=legend_elements, loc='lower center', ncol=5,
                       fontsize=9, frameon=True)

if __name__ == "__main__":
    renderer = StickRenderer()
    # Test with simple NAND path
    renderer.draw_layout(['A', 'B'], None, None)
    plt.savefig('test_stick_diagram.png', dpi=150, bbox_inches='tight')
    print("Saved test_stick_diagram.png")
