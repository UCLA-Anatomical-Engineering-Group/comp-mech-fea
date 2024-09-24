from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

import time
import math

# timing
start_time_cpu = time.clock()
start_time_wall = time.time()

NUM_CPUS = 4
TOTAL_RAM = 64 # [GBs]

MODULUS_TI64 = 104800.31 # [MPa]
POISSON_TI64 = 0.31

SINGLE_STEP = False
INCLUDE_ROTATION = True # Ry
INCLUDE_INPLANE_VERT_FORCE = False # Fz
INCLUDE_INPLANE_HORIZ_FORCE = False # Fx
INCLUDE_INPLANE_TORQUE = False # Tz
INCLUDE_OUTPLANE_FORCE = False # Fy
INCLUDE_OUTPLANE_TORQUE = False # Tx

FULL_TAPER = False
MESH_FACTOR = 3

######################
## helper functions ##
######################
def pprint(str):
	print >> sys.__stdout__, str

def change_extension_to_lowercase(file_path_without_extension):
	# Find the file in the directory with any extension
	directory, file_name = os.path.split(file_path_without_extension)
	for item in os.listdir(directory):
		if item.startswith(file_name):
			base, ext = os.path.splitext(item)
			if base == file_name:
				full_file_path = os.path.join(directory, item)
				# Check if the extension is not lowercase
				if ext and not ext.islower():
					new_file_path = os.path.join(directory, base + ext.lower())
					os.rename(full_file_path, new_file_path)
					return new_file_path
				else:
					return full_file_path
################
## file paths ##
################
file_name = 'xpivot_$$$'
project_dir = '$$$'

step_file_path_noext = project_dir + 'steps/' + file_name
step_file_path = change_extension_to_lowercase(step_file_path_noext)

param_file_path = project_dir + 'params/' + file_name + '.txt'
with open(param_file_path, 'r') as file:
	for line in file:
		if line.strip().startswith('#') or '=' not in line:
			continue
		param_name, param_value = [x.strip() for x in line.split('=')]
		exec(param_name + ' = ' + param_value)
################

# define loads
if SINGLE_STEP:
	rotation_deg = $$$ # Ry
	inplane_vert_force_N = $$$ # Fz
	inplane_horiz_force_N = $$$ # Fx
	inplane_torque_Nm = $$$ # Tz
	inplane_torque_Nmm = inplane_torque_Nm*1000.0 # convert units
	outplane_force_N = $$$ # Fy
	outplane_torque_Nm = $$$ # Tx
	outplane_torque_Nmm = outplane_torque_Nm*1000.0 # convert units

else: # trajectory
	num_steps_rot = 0
	if INCLUDE_ROTATION:
		rotation_degs = [$$$] # Ry
		num_steps_rot = len(rotation_degs)

		# use velo for simulating trajectory
		velocity_dps = [rotation_degs[0]]
		for i in range(len(rotation_degs)-1):
			velocity_dps.append(rotation_degs[i+1] - rotation_degs[i])

	num_steps_inplane_vert_force = 0
	if INCLUDE_INPLANE_VERT_FORCE:
		inplane_vert_force_Ns = [$$$] # Fz
		num_steps_inplane_vert_force = len(inplane_vert_force_Ns)

	num_steps_inplane_horiz_force = 0
	if INCLUDE_INPLANE_HORIZ_FORCE:
		inplane_horiz_force_Ns = [$$$] # Fx
		num_steps_inplane_horiz_force = len(inplane_horiz_force_Ns)

	num_steps_inplane_torque = 0
	if INCLUDE_INPLANE_TORQUE:
		inplane_torque_Nms = [$$$] # Tz
		inplane_torque_Nmms = [i*1000.0 for i in inplane_torque_Nms] # convert units
		num_steps_inplane_torque = len(inplane_torque_Nms)

	num_steps_outplane_force = 0
	if INCLUDE_OUTPLANE_FORCE:
		outplane_force_Ns = [$$$] # Fy
		num_steps_outplane_force = len(outplane_force_Ns)

	num_steps_outplane_torque = 0
	if INCLUDE_OUTPLANE_TORQUE:
		outplane_torque_Nms = [$$$] # Tz
		outplane_torque_Nmms = [i*1000.0 for i in outplane_torque_Nms] # convert units
		num_steps_outplane_torque = len(outplane_torque_Nms)

	# check num_step equality when > 1 type of load
	step_cnts = [num_steps_rot, num_steps_inplane_vert_force, num_steps_inplane_horiz_force, num_steps_inplane_torque, num_steps_outplane_force, num_steps_outplane_torque]
	# ignore loads not included
	non_zero_step_cnts = [val for val in step_cnts if val != 0]
	if len(non_zero_step_cnts) > 1:
	    assert all(val == non_zero_step_cnts[0] for val in non_zero_step_cnts), "Load vector lengths must be equal."
	num_steps = non_zero_step_cnts[0]

# import step file
mdb.openStep(step_file_path, scaleFromFile=OFF)
part_name = 'xpivot'
model_name = 'Model-1'
xpivot_model = mdb.models[model_name]
xpivot_model.PartFromGeometryFile(combine=True, dimensionality=THREE_D, geometryFile=mdb.acis, mergeSolidRegions=True, name='xpivot', retainBoundary=True, type=DEFORMABLE_BODY)
xpivot_part = xpivot_model.parts[part_name]

# create and apply Ti64 material
material_name = 'Ti64'
xpivot_model.Material(name=material_name)
xpivot_model.materials[material_name].Elastic(table=((MODULUS_TI64, POISSON_TI64), ))
section_name = 'Section-1'
xpivot_model.HomogeneousSolidSection(material=material_name, name=section_name, thickness=None)
xpivot_part.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=Region(cells=xpivot_part.cells.getSequenceFromMask(('[#1]', ), )), sectionName=section_name, thicknessAssignment=FROM_SECTION)

# create assembly
mdb.models[model_name].rootAssembly.DatumCsysByDefault(CARTESIAN)
mdb.models[model_name].rootAssembly.Instance(dependent=OFF, name=part_name + '-1', part=xpivot_part)
xpivot_assy = mdb.models[model_name].rootAssembly
xpivot_assy_inst = xpivot_assy.instances[part_name + '-1']

# create steps
mdb.models[model_name].StaticStep(name='Step-1', nlgeom=ON, previous='Initial')
if not SINGLE_STEP:
	for i in range(num_steps-1):
		xpivot_model.StaticStep(name='Step-' + str(i+2), nlgeom=ON, previous='Step-' + str(i+1), maxNumInc=100)

# create reference points
rp_offset_z = BLADE_LENGTH + 5.0 # params.txt [mm]
rp = xpivot_assy.ReferencePoint(point=(0.0, 0.0, rp_offset_z))
xpivot_assy.Set(name='RP', referencePoints=(xpivot_assy.referencePoints[rp.id], ))

# create kinematic coupling
face_load = xpivot_assy_inst.faces.findAt(((FACE_LOAD_X, FACE_LOAD_Y, FACE_LOAD_Z),))
xpivot_assy.Surface(name='Surface-Load', side1Faces=face_load)
xpivot_model.Coupling(controlPoint=xpivot_assy.sets['RP'], couplingType=KINEMATIC, influenceRadius=WHOLE_SURFACE, localCsys=None, name='Coupling-SurfaceLoad', surface=xpivot_assy.surfaces['Surface-Load'], u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

# create distal ground
face_gnd = xpivot_assy_inst.faces.findAt(((FACE_GND_X, FACE_GND_Y, FACE_GND_Z),))
xpivot_assy.Set(faces=face_gnd, name='Face-GND')
xpivot_model.EncastreBC(createStepName='Step-1', localCsys=None, name='BC_GND', region=xpivot_assy.sets['Face-GND'])

# define loads
if SINGLE_STEP:
	if INCLUDE_ROTATION:
		xpivot_model.DisplacementBC(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='BC-Rotation', region=xpivot_assy.sets['RP'], u1=UNSET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=rotation_deg*math.pi/180, ur3=UNSET)
	if INCLUDE_INPLANE_VERT_FORCE:
		xpivot_model.ConcentratedForce(cf3=inplane_vert_force_N, createStepName='Step-1', distributionType=UNIFORM, field='', follower=ON, localCsys=None, name='Load-InPlaneVertForce', region=xpivot_assy.sets['RP'])
	if INCLUDE_INPLANE_HORIZ_FORCE:
		xpivot_model.ConcentratedForce(cf1=inplane_horiz_force_N, createStepName='Step-1', distributionType=UNIFORM, field='', follower=ON, localCsys=None, name='Load-InPlaneHorizForce', region=xpivot_assy.sets['RP'])
	if INCLUDE_INPLANE_TORQUE:
		xpivot_model.Moment(cm3=inplane_torque_Nmm, createStepName='Step-1', distributionType=UNIFORM, field='', localCsys=None, name='Load-InPlaneTorque', region=xpivot_assy.sets['RP'])
	if INCLUDE_OUTPLANE_FORCE:
		xpivot_model.ConcentratedForce(cf2=outplane_force_N, createStepName='Step-1', distributionType=UNIFORM, field='', follower=ON, localCsys=None, name='Load-OutPlaneForce', region=xpivot_assy.sets['RP'])
	if INCLUDE_OUTPLANE_TORQUE:
		xpivot_model.Moment(cm1=outplane_torque_Nmm, createStepName='Step-1', distributionType=UNIFORM, field='', localCsys=None, name='Load-OutPlaneTorque', region=xpivot_assy.sets['RP'])

else: # trajectory
	# set up step 1
	if INCLUDE_ROTATION:
		xpivot_model.VelocityBC(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, fieldName='', localCsys=None, name='BC-Velo', region=xpivot_assy.sets['RP'], v1=UNSET, v2=UNSET, v3=UNSET, vr1=UNSET, vr2=velocity_dps[0]*math.pi/180, vr3=UNSET)
	if INCLUDE_INPLANE_VERT_FORCE:
		xpivot_model.ConcentratedForce(cf3=inplane_vert_force_Ns[0], createStepName='Step-1', distributionType=UNIFORM, field='', follower=ON, localCsys=None, name='Load-InPlaneVertForce', region=xpivot_assy.sets['RP'])
	if INCLUDE_INPLANE_HORIZ_FORCE:
		xpivot_model.ConcentratedForce(cf1=inplane_horiz_force_Ns[0], createStepName='Step-1', distributionType=UNIFORM, field='', follower=ON, localCsys=None, name='Load-InPlaneHorizForce', region=xpivot_assy.sets['RP'])
	if INCLUDE_INPLANE_TORQUE:
		xpivot_model.Moment(cm3=inplane_torque_Nmms[0], createStepName='Step-1', distributionType=UNIFORM, field='', localCsys=None, name='Load-InPlaneTorque', region=xpivot_assy.sets['RP'])
	if INCLUDE_OUTPLANE_FORCE:
		xpivot_model.ConcentratedForce(cf2=outplane_force_Ns[0], createStepName='Step-1', distributionType=UNIFORM, field='', follower=ON, localCsys=None, name='Load-OutPlaneForce', region=xpivot_assy.sets['RP'])
	if INCLUDE_OUTPLANE_TORQUE:
		xpivot_model.Moment(cm1=outplane_torque_Nmms[0], createStepName='Step-1', distributionType=UNIFORM, field='', localCsys=None, name='Load-OutPlaneTorque', region=xpivot_assy.sets['RP'])

	# set up remaining steps
	for i in range(num_steps-1):
		if INCLUDE_ROTATION:
			xpivot_model.boundaryConditions['BC-Velo'].setValuesInStep(stepName='Step-' + str(i+2), vr2=velocity_dps[i+1]*math.pi/180)
		if INCLUDE_INPLANE_VERT_FORCE:
			xpivot_model.loads['Load-InPlaneVertForce'].setValuesInStep(stepName='Step-' + str(i+2), cf3=inplane_vert_force_Ns[i+1])
		if INCLUDE_INPLANE_HORIZ_FORCE:
			xpivot_model.loads['Load-InPlaneHorizForce'].setValuesInStep(stepName='Step-' + str(i+2), cf1=inplane_horiz_force_Ns[i+1])
		if INCLUDE_INPLANE_TORQUE:
			xpivot_model.loads['Load-InPlaneTorque'].setValuesInStep(stepName='Step-' + str(i+2), cm3=inplane_torque_Nmms[i+1])
		if INCLUDE_OUTPLANE_FORCE:
			xpivot_model.loads['Load-OutPlaneForce'].setValuesInStep(stepName='Step-' + str(i+2), cf3=outplane_force_Ns[i+1])
		if INCLUDE_OUTPLANE_TORQUE:
			xpivot_model.loads['Load-OutPlaneTorque'].setValuesInStep(stepName='Step-' + str(i+2), cm3=outplane_torque_Nmms[i+1])			


# prep for meshing
face_inner_cylinder = xpivot_assy_inst.faces.findAt(((FACE_INNER_CYLINDER_X, FACE_INNER_CYLINDER_Y, FACE_INNER_CYLINDER_Z),))
xpivot_assy.PartitionCellByExtendFace(cells=xpivot_assy_inst.cells, extendFace=face_inner_cylinder[0])

xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER1_FILLET1_X, IGNORE_OUTER1_FILLET1_Y, IGNORE_OUTER1_FILLET1_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER1_FILLET2_X, IGNORE_OUTER1_FILLET2_Y, IGNORE_OUTER1_FILLET2_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER1_FILLET3_X, IGNORE_OUTER1_FILLET3_Y, IGNORE_OUTER1_FILLET3_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER1_FILLET4_X, IGNORE_OUTER1_FILLET4_Y, IGNORE_OUTER1_FILLET4_Z),),))

xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER1_TAPER1_X, IGNORE_OUTER1_TAPER1_Y, IGNORE_OUTER1_TAPER1_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER1_TAPER2_X, IGNORE_OUTER1_TAPER2_Y, IGNORE_OUTER1_TAPER2_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER1_TAPER3_X, IGNORE_OUTER1_TAPER3_Y, IGNORE_OUTER1_TAPER3_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER1_TAPER4_X, IGNORE_OUTER1_TAPER4_Y, IGNORE_OUTER1_TAPER4_Z),),))

xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER2_FILLET1_X, IGNORE_OUTER2_FILLET1_Y, IGNORE_OUTER2_FILLET1_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER2_FILLET2_X, IGNORE_OUTER2_FILLET2_Y, IGNORE_OUTER2_FILLET2_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER2_FILLET3_X, IGNORE_OUTER2_FILLET3_Y, IGNORE_OUTER2_FILLET3_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER2_FILLET4_X, IGNORE_OUTER2_FILLET4_Y, IGNORE_OUTER2_FILLET4_Z),),))

xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER2_TAPER1_X, IGNORE_OUTER2_TAPER1_Y, IGNORE_OUTER2_TAPER1_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER2_TAPER2_X, IGNORE_OUTER2_TAPER2_Y, IGNORE_OUTER2_TAPER2_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER2_TAPER3_X, IGNORE_OUTER2_TAPER3_Y, IGNORE_OUTER2_TAPER3_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_OUTER2_TAPER4_X, IGNORE_OUTER2_TAPER4_Y, IGNORE_OUTER2_TAPER4_Z),),))

xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_INNER_FILLET1_X, IGNORE_INNER_FILLET1_Y, IGNORE_INNER_FILLET1_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_INNER_FILLET2_X, IGNORE_INNER_FILLET2_Y, IGNORE_INNER_FILLET2_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_INNER_FILLET3_X, IGNORE_INNER_FILLET3_Y, IGNORE_INNER_FILLET3_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_INNER_FILLET4_X, IGNORE_INNER_FILLET4_Y, IGNORE_INNER_FILLET4_Z),),))

xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_INNER_TAPER1_X, IGNORE_INNER_TAPER1_Y, IGNORE_INNER_TAPER1_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_INNER_TAPER2_X, IGNORE_INNER_TAPER2_Y, IGNORE_INNER_TAPER2_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_INNER_TAPER3_X, IGNORE_INNER_TAPER3_Y, IGNORE_INNER_TAPER3_Z),),))
xpivot_assy.ignoreEntity((xpivot_assy_inst.edges.findAt((IGNORE_INNER_TAPER4_X, IGNORE_INNER_TAPER4_Y, IGNORE_INNER_TAPER4_Z),),))

# seed blade length edges
length_edges = []
if FULL_TAPER:
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_OUTER11_X, LENGTH_FULL_OUTER11_Y, LENGTH_FULL_OUTER11_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_OUTER12_X, LENGTH_FULL_OUTER12_Y, LENGTH_FULL_OUTER12_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_OUTER13_X, LENGTH_FULL_OUTER13_Y, LENGTH_FULL_OUTER13_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_OUTER14_X, LENGTH_FULL_OUTER14_Y, LENGTH_FULL_OUTER14_Z),))

	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_OUTER21_X, LENGTH_FULL_OUTER21_Y, LENGTH_FULL_OUTER21_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_OUTER22_X, LENGTH_FULL_OUTER22_Y, LENGTH_FULL_OUTER22_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_OUTER23_X, LENGTH_FULL_OUTER23_Y, LENGTH_FULL_OUTER23_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_OUTER24_X, LENGTH_FULL_OUTER24_Y, LENGTH_FULL_OUTER24_Z),))

	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_INNER1_X, LENGTH_FULL_INNER1_Y, LENGTH_FULL_INNER1_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_INNER2_X, LENGTH_FULL_INNER2_Y, LENGTH_FULL_INNER2_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_INNER3_X, LENGTH_FULL_INNER3_Y, LENGTH_FULL_INNER3_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_FULL_INNER4_X, LENGTH_FULL_INNER4_Y, LENGTH_FULL_INNER4_Z),))

else: # partial taper
	# ignore taper vertices before seeding
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_OUTER11_X, LENGTH_UPPER_PARTIAL_OUTER11_Y, LENGTH_UPPER_PARTIAL_OUTER11_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_OUTER12_X, LENGTH_UPPER_PARTIAL_OUTER12_Y, LENGTH_UPPER_PARTIAL_OUTER12_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_OUTER13_X, LENGTH_UPPER_PARTIAL_OUTER13_Y, LENGTH_UPPER_PARTIAL_OUTER13_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_OUTER14_X, LENGTH_UPPER_PARTIAL_OUTER14_Y, LENGTH_UPPER_PARTIAL_OUTER14_Z),),))

	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_OUTER11_X, LENGTH_LOWER_PARTIAL_OUTER11_Y, LENGTH_LOWER_PARTIAL_OUTER11_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_OUTER12_X, LENGTH_LOWER_PARTIAL_OUTER12_Y, LENGTH_LOWER_PARTIAL_OUTER12_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_OUTER13_X, LENGTH_LOWER_PARTIAL_OUTER13_Y, LENGTH_LOWER_PARTIAL_OUTER13_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_OUTER14_X, LENGTH_LOWER_PARTIAL_OUTER14_Y, LENGTH_LOWER_PARTIAL_OUTER14_Z),),))

	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_OUTER21_X, LENGTH_UPPER_PARTIAL_OUTER21_Y, LENGTH_UPPER_PARTIAL_OUTER21_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_OUTER22_X, LENGTH_UPPER_PARTIAL_OUTER22_Y, LENGTH_UPPER_PARTIAL_OUTER22_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_OUTER23_X, LENGTH_UPPER_PARTIAL_OUTER23_Y, LENGTH_UPPER_PARTIAL_OUTER23_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_OUTER24_X, LENGTH_UPPER_PARTIAL_OUTER24_Y, LENGTH_UPPER_PARTIAL_OUTER24_Z),),))

	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_OUTER21_X, LENGTH_LOWER_PARTIAL_OUTER21_Y, LENGTH_LOWER_PARTIAL_OUTER21_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_OUTER22_X, LENGTH_LOWER_PARTIAL_OUTER22_Y, LENGTH_LOWER_PARTIAL_OUTER22_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_OUTER23_X, LENGTH_LOWER_PARTIAL_OUTER23_Y, LENGTH_LOWER_PARTIAL_OUTER23_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_OUTER24_X, LENGTH_LOWER_PARTIAL_OUTER24_Y, LENGTH_LOWER_PARTIAL_OUTER24_Z),),))

	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_INNER1_X, LENGTH_UPPER_PARTIAL_INNER1_Y, LENGTH_UPPER_PARTIAL_INNER1_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_INNER2_X, LENGTH_UPPER_PARTIAL_INNER2_Y, LENGTH_UPPER_PARTIAL_INNER2_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_INNER3_X, LENGTH_UPPER_PARTIAL_INNER3_Y, LENGTH_UPPER_PARTIAL_INNER3_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_UPPER_PARTIAL_INNER4_X, LENGTH_UPPER_PARTIAL_INNER4_Y, LENGTH_UPPER_PARTIAL_INNER4_Z),),))

	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_INNER1_X, LENGTH_LOWER_PARTIAL_INNER1_Y, LENGTH_LOWER_PARTIAL_INNER1_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_INNER2_X, LENGTH_LOWER_PARTIAL_INNER2_Y, LENGTH_LOWER_PARTIAL_INNER2_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_INNER3_X, LENGTH_LOWER_PARTIAL_INNER3_Y, LENGTH_LOWER_PARTIAL_INNER3_Z),),))
	xpivot_assy.ignoreEntity((xpivot_assy_inst.vertices.findAt((LENGTH_LOWER_PARTIAL_INNER4_X, LENGTH_LOWER_PARTIAL_INNER4_Y, LENGTH_LOWER_PARTIAL_INNER4_Z),),))

	# seed length edges
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_OUTER11_X, LENGTH_CENTER_PARTIAL_OUTER11_Y, LENGTH_CENTER_PARTIAL_OUTER11_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_OUTER12_X, LENGTH_CENTER_PARTIAL_OUTER12_Y, LENGTH_CENTER_PARTIAL_OUTER12_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_OUTER13_X, LENGTH_CENTER_PARTIAL_OUTER13_Y, LENGTH_CENTER_PARTIAL_OUTER13_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_OUTER14_X, LENGTH_CENTER_PARTIAL_OUTER14_Y, LENGTH_CENTER_PARTIAL_OUTER14_Z),))

	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_OUTER21_X, LENGTH_CENTER_PARTIAL_OUTER21_Y, LENGTH_CENTER_PARTIAL_OUTER21_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_OUTER22_X, LENGTH_CENTER_PARTIAL_OUTER22_Y, LENGTH_CENTER_PARTIAL_OUTER22_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_OUTER23_X, LENGTH_CENTER_PARTIAL_OUTER23_Y, LENGTH_CENTER_PARTIAL_OUTER23_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_OUTER24_X, LENGTH_CENTER_PARTIAL_OUTER24_Y, LENGTH_CENTER_PARTIAL_OUTER24_Z),))

	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_INNER1_X, LENGTH_CENTER_PARTIAL_INNER1_Y, LENGTH_CENTER_PARTIAL_INNER1_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_INNER2_X, LENGTH_CENTER_PARTIAL_INNER2_Y, LENGTH_CENTER_PARTIAL_INNER2_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_INNER3_X, LENGTH_CENTER_PARTIAL_INNER3_Y, LENGTH_CENTER_PARTIAL_INNER3_Z),))
	length_edges.append(xpivot_assy_inst.edges.findAt((LENGTH_CENTER_PARTIAL_INNER4_X, LENGTH_CENTER_PARTIAL_INNER4_Y, LENGTH_CENTER_PARTIAL_INNER4_Z),))

xpivot_assy.seedEdgeByNumber(constraint=FINER, edges=xpivot_assy_inst.edges.findAt(*[(edge.pointOn[0],) for edge in length_edges]), number=BLADE_LENGTH*MESH_FACTOR) # params.txt

# see outer blade width edges
outer_width_edges = []
outer_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_OUTER11_X, WIDTH_OUTER11_Y, WIDTH_OUTER11_Z),))
outer_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_OUTER12_X, WIDTH_OUTER12_Y, WIDTH_OUTER12_Z),))
outer_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_OUTER13_X, WIDTH_OUTER13_Y, WIDTH_OUTER13_Z),))
outer_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_OUTER14_X, WIDTH_OUTER14_Y, WIDTH_OUTER14_Z),))

outer_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_OUTER21_X, WIDTH_OUTER21_Y, WIDTH_OUTER21_Z),))
outer_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_OUTER22_X, WIDTH_OUTER22_Y, WIDTH_OUTER22_Z),))
outer_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_OUTER23_X, WIDTH_OUTER23_Y, WIDTH_OUTER23_Z),))
outer_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_OUTER24_X, WIDTH_OUTER24_Y, WIDTH_OUTER24_Z),))

xpivot_assy.seedEdgeByNumber(constraint=FINER, edges=xpivot_assy_inst.edges.findAt(*[(edge.pointOn[0],) for edge in outer_width_edges]), number=round(OUTER_BLADE_WIDTH)*MESH_FACTOR) # params.txt

# seed inner blade width edges
inner_width_edges = []
inner_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_INNER1_X, WIDTH_INNER1_Y, WIDTH_INNER1_Z),))
inner_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_INNER2_X, WIDTH_INNER2_Y, WIDTH_INNER2_Z),))
inner_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_INNER3_X, WIDTH_INNER3_Y, WIDTH_INNER3_Z),))
inner_width_edges.append(xpivot_assy_inst.edges.findAt((WIDTH_INNER4_X, WIDTH_INNER4_Y, WIDTH_INNER4_Z),))

xpivot_assy.seedEdgeByNumber(constraint=FINER, edges=xpivot_assy_inst.edges.findAt(*[(edge.pointOn[0],) for edge in inner_width_edges]), number=round(INNER_BLADE_WIDTH)*MESH_FACTOR)

# seed blade thickness edges
thickness_edges = []
thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_OUTER11_X, THICKNESS_OUTER11_Y, THICKNESS_OUTER11_Z),))
thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_OUTER12_X, THICKNESS_OUTER12_Y, THICKNESS_OUTER12_Z),))
thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_OUTER11_X, THICKNESS_OUTER11_Y - OUTER_BLADE_WIDTH, THICKNESS_OUTER11_Z),))
thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_OUTER12_X, THICKNESS_OUTER12_Y - OUTER_BLADE_WIDTH, THICKNESS_OUTER12_Z),))

thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_OUTER21_X, THICKNESS_OUTER21_Y, THICKNESS_OUTER21_Z),))
thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_OUTER22_X, THICKNESS_OUTER22_Y, THICKNESS_OUTER22_Z),))
thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_OUTER21_X, THICKNESS_OUTER21_Y + OUTER_BLADE_WIDTH, THICKNESS_OUTER21_Z),))
thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_OUTER22_X, THICKNESS_OUTER22_Y + OUTER_BLADE_WIDTH, THICKNESS_OUTER22_Z),))

thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_INNER1_X, THICKNESS_INNER1_Y, THICKNESS_INNER1_Z),))
thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_INNER2_X, THICKNESS_INNER2_Y, THICKNESS_INNER2_Z),))
thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_INNER3_X, THICKNESS_INNER3_Y, THICKNESS_INNER3_Z),))
thickness_edges.append(xpivot_assy_inst.edges.findAt((THICKNESS_INNER4_X, THICKNESS_INNER4_Y, THICKNESS_INNER4_Z),))

xpivot_assy.seedEdgeByNumber(constraint=FINER, edges=xpivot_assy_inst.edges.findAt(*[(edge.pointOn[0],) for edge in thickness_edges]), number=6)

# apply global seed
xpivot_assy.seedPartInstance(deviationFactor=0.1, minSizeFactor=0.1, regions=(xpivot_assy_inst, ), size=1.0)

xpivot_assy.generateMesh(regions=(xpivot_assy_inst, ))

job_name = 'Job-$$$'
job = mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=TOTAL_RAM, memoryUnits=GIGA_BYTES, model='Model-1', modelPrint=OFF, multiprocessingMode=DEFAULT, name=job_name, nodalOutputPrecision=SINGLE, numCpus=NUM_CPUS, numDomains=NUM_CPUS, numGPUs=0, numThreadsPerMpiProcess=1, queue=None, resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)

job.submit()
job.waitForCompletion()

mdb.saveAs('$$$')
mdb.close()

# timing
end_time_cpu = time.clock()
end_time_wall = time.time()
elapsed_time_cpu = end_time_cpu - start_time_cpu
elapsed_time_wall = end_time_wall - start_time_wall
