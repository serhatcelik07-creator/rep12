"""ZIVER_PETROL_LPG_KK_PROJE.dxf -> 1/50 ölçekli, pafta çerçevesi ölçüsünde (özel sayfa) vektör PDF."""
import os
import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy, LineweightPolicy

HERE = os.path.dirname(os.path.abspath(__file__))
DXF = os.path.join(HERE, "ZIVER_PETROL_LPG_KK_PROJE_R1.dxf")
PDF = os.path.join(HERE, "ZIVER_PETROL_LPG_KK_PROJE_R1_1-50.pdf")
OLCEK = 50                                   # 1/50
X0, Y0, X1, Y1 = -12.26, -0.71, 97.60, 37.30  # pafta çerçevesi (m)
W_MM, H_MM = (X1 - X0) * 1000 / OLCEK, (Y1 - Y0) * 1000 / OLCEK

doc = ezdxf.readfile(DXF)
fig = plt.figure(figsize=(W_MM / 25.4, H_MM / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR,
                    lineweight_policy=LineweightPolicy.ABSOLUTE, lineweight_scaling=1.0)
Frontend(RenderContext(doc), MatplotlibBackend(ax, adjust_figure=False), config=cfg).draw_layout(doc.modelspace())
ax.set_xlim(X0, X1)
ax.set_ylim(Y0, Y1)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(PDF, format="pdf", metadata={"Title": "Ziver Petrol - LPG Katodik Koruma Projesi R1", "Author": "SMA Mühendislik", "Creator": "SMA Mühendislik", "Producer": "SMA Mühendislik"})
print(f"PDF: {PDF}  sayfa {W_MM:.1f} x {H_MM:.1f} mm (1/{OLCEK})")
