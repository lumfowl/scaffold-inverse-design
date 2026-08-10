import bpy
import csv
import math
import bmesh
from mathutils import Vector

# =====================================================
# USER SETTINGS
# =====================================================

csv_path = r"Your CSV Path"

scale = 0.01       # SolidWorks mm -> Blender
unitscale = 4.9    # Wireframe interval

# Target effective elastic modulus
target_modulus_kPa = 57.027


# =====================================================
# EXPERIMENTAL CALIBRATION
# =====================================================

calibration_enabled = True

# Experimental calibration point
calibration_strut_width_mm = 1.0
calibration_modulus_kPa = 19.61225

# =====================================================
# SIMULATION EQUATION
# =====================================================

SIM_COEFFICIENT = 27.986
SIM_EXPONENT = 3.8649


# =====================================================
# CALIBRATION
# =====================================================

def calculate_calibration_factor(
    calibration_strut_width_mm,
    calibration_modulus_kPa
):

    simulated_modulus = (
        SIM_COEFFICIENT
        * calibration_strut_width_mm ** SIM_EXPONENT
    )

    return calibration_modulus_kPa / simulated_modulus


calibration_factor = 1.0

if calibration_enabled:
    calibration_factor = calculate_calibration_factor(
        calibration_strut_width_mm,
        calibration_modulus_kPa
    )


# =====================================================
# PREDICT STRUT WIDTH
# =====================================================

def predict_strut_width(target_modulus_kPa):
    
    return (
        target_modulus_kPa
        / (calibration_factor * SIM_COEFFICIENT)
    ) ** (1.0 / SIM_EXPONENT)

# =====================================================
# CALCULATE STRUT WIDTH
# =====================================================

strut_width_mm = predict_strut_width(target_modulus_kPa)

# Convert to Blender units
strut_width = strut_width_mm * scale
strut_height = strut_width_mm * scale

# =====================================================
# READ EDGES
# =====================================================

edges = []
nodes = {}


def node_key(p):
    return (
        round(p[0],8),
        round(p[1],8),
        round(p[2],8)
    )


with open(csv_path,newline="") as f:

    reader = csv.DictReader(f)

    for row in reader:

        p1 = (
            float(row["StartX"])*scale*unitscale,
            float(row["StartY"])*scale*unitscale,
            float(row["StartZ"])*scale*unitscale
        )

        p2 = (
            float(row["EndX"])*scale*unitscale,
            float(row["EndY"])*scale*unitscale,
            float(row["EndZ"])*scale*unitscale
        )

        k1 = node_key(p1)
        k2 = node_key(p2)

        nodes[k1] = Vector(p1)
        nodes[k2] = Vector(p2)

        edges.append((k1,k2))


print("Nodes:",len(nodes))
print("Edges:",len(edges))


# =====================================================
# CREATE MESH ARRAYS
# =====================================================

verts=[]
faces=[]


def add_box(center,size):

    x,y,z = center
    sx,sy,sz = size

    start=len(verts)

    verts.extend([

        (x-sx/2,y-sy/2,z-sz/2),
        (x+sx/2,y-sy/2,z-sz/2),
        (x+sx/2,y+sy/2,z-sz/2),
        (x-sx/2,y+sy/2,z-sz/2),

        (x-sx/2,y-sy/2,z+sz/2),
        (x+sx/2,y-sy/2,z+sz/2),
        (x+sx/2,y+sy/2,z+sz/2),
        (x-sx/2,y+sy/2,z+sz/2),

    ])


    faces.extend([

        (start,start+1,start+2,start+3),
        (start+4,start+7,start+6,start+5),

        (start,start+4,start+5,start+1),
        (start+1,start+5,start+6,start+2),

        (start+2,start+6,start+7,start+3),
        (start+4,start,start+3,start+7)

    ])



# =====================================================
# CREATE JUNCTION BLOCKS
# =====================================================

for p in nodes.values():

    add_box(
        p,
        (
            strut_width,
            strut_width,
            strut_height
        )
    )



# =====================================================
# CREATE BEAMS
# =====================================================

def create_beam(a,b):

    a = Vector(a)
    b = Vector(b)


    direction = b-a
    length = direction.length


    if length <= 0:
        return


    direction.normalize()


    # enter junction cube
    offset = strut_width/2


    start = a + direction*offset
    end = b - direction*offset


    length = (end-start).length


    if length <= 0:
        return


    center=(start+end)/2


    x_axis=direction


    if abs(x_axis.z)<0.9:
        temp=Vector((0,0,1))
    else:
        temp=Vector((0,1,0))


    y_axis=x_axis.cross(temp).normalized()
    z_axis=x_axis.cross(y_axis).normalized()



    hx=length/2
    hy=strut_width/2
    hz=strut_height/2


    local_points=[

        (-hx,-hy,-hz),
        ( hx,-hy,-hz),
        ( hx, hy,-hz),
        (-hx, hy,-hz),

        (-hx,-hy, hz),
        ( hx,-hy, hz),
        ( hx, hy, hz),
        (-hx, hy, hz)

    ]


    start_index=len(verts)


    for p in local_points:

        world = (
            center
            +
            x_axis*p[0]
            +
            y_axis*p[1]
            +
            z_axis*p[2]
        )

        verts.append(tuple(world))


    faces.extend([

        (
            start_index,
            start_index+1,
            start_index+2,
            start_index+3
        ),

        (
            start_index+4,
            start_index+7,
            start_index+6,
            start_index+5
        ),

        (
            start_index,
            start_index+4,
            start_index+5,
            start_index+1
        ),

        (
            start_index+1,
            start_index+5,
            start_index+6,
            start_index+2
        ),

        (
            start_index+2,
            start_index+6,
            start_index+7,
            start_index+3
        ),

        (
            start_index+4,
            start_index,
            start_index+3,
            start_index+7
        )

    ])



for a,b in edges:

    create_beam(
        nodes[a],
        nodes[b]
    )


print("Generated raw mesh")
print("Vertices:",len(verts))
print("Faces:",len(faces))



# =====================================================
# CREATE BLENDER OBJECT
# =====================================================

mesh=bpy.data.meshes.new("AuxeticMesh")

mesh.from_pydata(
    verts,
    [],
    faces
)

mesh.update()


obj=bpy.data.objects.new(
    "Auxetic_Direct",
    mesh
)

bpy.context.collection.objects.link(obj)



# =====================================================
# REMOVE INTERNAL FACES USING CSV CENTERLINES
# =====================================================

bm=bmesh.new()
bm.from_mesh(mesh)

bm.faces.ensure_lookup_table()



def point_inside_quad(point, face, tol=1e-6):

    verts = [v.co for v in face.verts]

    if len(verts) != 4:
        return False

    normal = face.normal

    for i in range(4):

        a = verts[i]
        b = verts[(i + 1) % 4]

        edge = b - a
        vp = point - a

        if edge.cross(vp).dot(normal) < -tol:
            return False

    return True



def segment_face_intersection(p1,p2,face):

    normal=face.normal
    plane_point=face.verts[0].co


    direction=p2-p1

    denom=direction.dot(normal)


    if abs(denom)<1e-10:
        return None


    t=(plane_point-p1).dot(normal)/denom


    if t<0 or t>1:
        return None


    return p1+direction*t



delete_faces=[]


for face in bm.faces:

    for a,b in edges:

        hit=segment_face_intersection(
            nodes[a],
            nodes[b],
            face
        )


        if hit is not None:

            if point_inside_quad(hit,face):

                delete_faces.append(face)
                break

print(
    "Internal faces removed:",
    len(delete_faces)
)


bmesh.ops.delete(
    bm,
    geom=delete_faces,
    context='FACES'
)


bm.to_mesh(mesh)
bm.free()

mesh.update()



# =====================================================
# CLEAN
# =====================================================

bpy.context.view_layer.objects.active=obj
obj.select_set(True)


bpy.ops.object.mode_set(mode="EDIT")


bpy.ops.mesh.select_all(action="SELECT")


bpy.ops.mesh.remove_doubles(
    threshold=1e-7
)


bpy.ops.mesh.normals_make_consistent(
    inside=False
)


bpy.ops.object.mode_set(mode="OBJECT")

# =====================================================
# EXPORT
# =====================================================

bpy.ops.object.select_all(action="DESELECT")

obj.select_set(True)

bpy.context.view_layer.objects.active=obj


print("DONE")
