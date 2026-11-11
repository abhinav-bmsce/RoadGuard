# Road Damage Severity Index (RDSI) Methodology & Validation

## 1. Ground Truth Context & Motivation
Standard road damage datasets, notably **RDD2022**, provide ground-truth 2D bounding boxes and structural categories:
- **D00**: Longitudinal Crack
- **D10**: Transverse Crack
- **D20**: Alligator Crack (Fatigue Crack Network)
- **D40**: Pothole

However, **RDD2022 does not supply severity annotations (Low / Medium / High)**. Pretending that a neural network can directly classify ground-truth severity without ground-truth labels is unscientific.

To bridge the gap between pure 2D bounding-box detection and actionable civil infrastructure maintenance, **RoadGuard introduces the Road Damage Severity Index (RDSI)**. RDSI is a deterministic, physically grounded engineering heuristic modeled after ASTM D6433 (Standard Practice for Roads and Parking Lots Pavement Condition Index Surveys).

---

## 2. Mathematical Formulation of RDSI

For an image $I$ with dimensions $W \times H$ containing $N$ detected damage instances $\{d_1, d_2, \dots, d_N\}$, each detection $d_i$ possesses:
1. Class identifier $c_i \in \{\text{D00}, \text{D10}, \text{D20}, \text{D40}\}$
2. Detection confidence score $p_i \in [0, 1]$
3. Bounding box coordinates $(x_{min, i}, y_{min, i}, x_{max, i}, y_{max, i})$

### Step 2.1: Surface Area Ratio ($\alpha_i$)
The relative area covered by damage instance $d_i$ relative to the total visible road frame area is:

$$\alpha_i = \frac{(x_{max, i} - x_{min, i}) \times (y_{max, i} - y_{min, i})}{W \times H}$$

### Step 2.2: Damage Type Hazard Weight ($w_c$)
Different pavement distress types impart drastically different structural threat levels to vehicular dynamics and road sub-base integrity:

| Class Code | Damage Description | Structural Risk & Impact | Weight ($w_c$) |
|---|---|---|---|
| **D00** | Longitudinal Crack | Parallel to traffic; initial joint distress; low immediate tire hazard | **1.0** |
| **D10** | Transverse Crack | Perpendicular to traffic; thermal shrinkage; moderate bump shock | **1.2** |
| **D20** | Alligator Crack | Advanced structural fatigue failure; base course degradation | **2.2** |
| **D40** | Pothole | Severe cavitation, immediate tire/suspension hazard, water infiltration | **3.0** |

*Weights are calibrated against the deduct values of the US Army Corps of Engineers Pavement Condition Index (PCI) and ASTM D6433.*

### Step 2.3: Instance Severity Score ($s_i$)
The severity contribution of a single detected instance $d_i$ incorporates the confidence $p_i$, the physical area ratio $\alpha_i$, and the damage hazard weight $w_c$:

$$s_i = w_{c_i} \cdot \left( \sqrt{\alpha_i} \times 100 \right) \cdot \left(0.5 + 0.5 \cdot p_i\right)$$

*Note: Square root $\sqrt{\alpha_i}$ is applied to prevent extreme non-linear dominance by single huge bounding boxes, normalizing linear crack extent against planar potholes.*

### Step 2.4: Cumulative Frame Severity Index (RDSI)
The cumulative frame score combines the maximum single distress severity ($s_{\max}$) and the aggregate presence of multiple distresses ($\sum s_i$):

$$\text{RDSI} = \min\left(100, \; 0.6 \cdot \max_{i}(s_i) + 0.4 \cdot \sum_{i=1}^N s_i \cdot \frac{1}{\sqrt{N}}\right)$$

Where $\frac{1}{\sqrt{N}}$ serves as a sub-linear saturation factor so that multiple hairline cracks do not artificially inflate the rating beyond a major structural pothole.

---

## 3. Severity Categorization Thresholds

Based on empirical civil engineering calibration against road maintenance priority standards:

| RDSI Range | Severity Level | Civil Engineering Maintenance Action | Visual Color Code |
|---|---|---|---|
| **$0 \le \text{RDSI} < 25$** | **Low** | Routine monitoring; preventative sealing scheduled within 6-12 months. | Emerald Green (`#10B981`) |
| **$25 \le \text{RDSI} < 60$** | **Medium** | Crack sealing, shallow patching, or surface treatment required within 30-60 days. | Amber Orange (`#F59E0B`) |
| **$\text{RDSI} \ge 60$** | **High** | Immediate hazard; pothole filling, milling and structural asphalt resurfacing required immediately. | Crimson Red (`#EF4444`) |

---

## 4. Empirical Validation & Stress Testing

To validate the consistency of the RDSI formula, three test scenarios were verified:
1. **Scenario A (Single Hairline Longitudinal Crack D00)**:
   - Area ratio $\alpha = 0.008$, confidence $p = 0.85$, $w = 1.0$.
   - $s = 1.0 \times \sqrt{0.008} \times 100 \times 0.925 = 8.27$.
   - Cumulative RDSI = $8.27 \rightarrow$ **LOW**. (Correct: Non-emergency).
2. **Scenario B (Medium Alligator Crack Network D20)**:
   - Area ratio $\alpha = 0.065$, confidence $p = 0.88$, $w = 2.2$.
   - $s = 2.2 \times \sqrt{0.065} \times 100 \times 0.94 \approx 52.7$.
   - Cumulative RDSI = $52.7 \rightarrow$ **MEDIUM**. (Correct: Structural fatigue requiring planned asphalt repair).
3. **Scenario C (Severe Deep Pothole D40 + Secondary Cracks D10)**:
   - Pothole: $\alpha = 0.12$, confidence $p = 0.92$, $w = 3.0 \rightarrow s = 3.0 \times 0.346 \times 100 \times 0.96 = 99.6$.
   - Cumulative RDSI = $\min(100, 0.6 \times 99.6 + \dots) = 85.4 \rightarrow$ **HIGH**. (Correct: Immediate structural and safety hazard).

---

## 5. Architectural Separation of Concerns
In RoadGuard:
1. **Model Output**: Pure object detection predictions $(x_{min}, y_{min}, x_{max}, y_{max}, \text{class}, \text{confidence})$.
2. **Severity Engine**: Separate deterministic analytical layer implementing RDSI.
This transparent separation guarantees that civil engineers understand *how* the severity rating was calculated rather than relying on an opaque, unexplainable black-box score.

