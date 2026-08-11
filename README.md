# scaffold-inverse-design
Computational framework for inverse design of tunable rectangular scaffolds based on target effective elastic modulus.
# Inverse Design of Tunable Auxetic Scaffolds

## Overview

This repository contains a computational workflow for the **inverse design of tunable rectangular auxetic scaffolds based on a target effective elastic modulus**.

The workflow converts a CAD wireframe into a parameterized 3D scaffold, with strut width determined from a target effective modulus.

**CAD wireframe → CSV → normalization → inverse design → Blender scaffold → Boolean union → mesh validation → FEA**

---

## Workflow

### 1. Create Wireframe in SolidWorks

Create the scaffold as a **3D sketch** in SolidWorks, with each line representing a scaffold strut.

Export the 3D sketch coordinates using:

```text
code/solidworks/3d_sketch_to_csv_VBA_macro
```

### 2. Normalize the CSV

Normalize the exported coordinates so that the characteristic unit distance of the lattice is equal to **1**.

For the lattice used in this work, each unit cell is rectangular. The coordinates can be quickly scaled in Excel before being imported into Blender.

### 3. Inverse Design and Scaffold Generation

For generating a scaffold with a predetermined strut dimensions, use:

```text
code/blender/scaffold_generator.py
```

This script generates an auxetic scaffold based on the wireframe csv with the user designated strut and wireframe dimensions. 

For generating a scaffold with a desired effective elastic modulus, use:

```text
code/blender/predict_strut
```

The script predicts the required strut width from the target effective elastic modulus and generates the corresponding 3D scaffold.

The simulation-derived relationship is:

`E_eff = 27.986 * sw^3.8649`

where (E_{\mathrm{eff}}) is in kPa and (sw) is in mm.

Experimental calibration can be applied using an experimentally measured modulus at a known strut width.

### 4. Boolean Union in Blender

In Blender:

1. Open **Geometry Nodes** and click **New**.
2. Add **Mesh Boolean**.
3. Set the operation to **Union**.
4. Set the solver to **Exact**.
5. Enable **Self Intersection**.
6. Apply the Geometry Nodes modifier.

This creates a unified scaffold solid.

### 5. Check Mesh

Enter **Edit Mode** and use:

**Select → Select All by Trait → Non-Manifold**

If no geometry is selected, the scaffold can be exported for finite element analysis.

### 6. FEA

The resulting scaffold can be exported to FEBio or another FEA package for mechanical simulation and validation.

---

## Citation

If you use this code or workflow in your research, please cite the associated publication:

**[Publication citation to be added]**
