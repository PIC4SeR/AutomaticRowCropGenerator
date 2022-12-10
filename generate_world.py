# MIT License

# Copyright (c) 2022 Marco Ambrosio

#     Permission is hereby granted, free of charge, to any person obtaining a copy
#     of this software and associated documentation files (the "Software"), to deal
#     in the Software without restriction, including without limitation the rights
#     to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#     copies of the Software, and to permit persons to whom the Software is
#     furnished to do so, subject to the following conditions:

#     The above copyright notice and this permission notice shall be included in all
#     copies or substantial portions of the Software.

#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#     IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#     AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#     OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#     SOFTWARE.


import bpy
import os, sys, glob
import random, math
import yaml
from shutil import copy2
from string import Template
import numpy as np
from scipy.interpolate import griddata


def load_models(source_file, dest_file, location):
    global COUNTER_MODELS
    
    print("Loading model from {}".format(source_file))
    with bpy.data.libraries.load(source_file) as (data_from, data_to):
        objects = []
        for obj in data_from.objects:
            # print(obj)
            objects.append({'name' : obj})

    bpy.ops.wm.append(filepath=dest_file, directory=source_file+'/Object/', files=objects)
    
    plant = bpy.data.objects['plant']
    plant.name = "plant"+str(COUNTER_MODELS)
    if len(plant.children) != 0:
        plant.children[0].name = "leaves"+str(COUNTER_MODELS)
        
    plant.location = location
    COUNTER_MODELS += 1


    
def duplicate_models(plant_list, location, yaw):
    global COUNTER_MODELS
    plant_name = "plant"+str(random.choice(plant_list))
    bpy.context.view_layer.objects.active = bpy.data.objects[plant_name]
    bpy.data.objects[plant_name].select_set(True)
    bpy.ops.object.select_grouped(extend = True, type='CHILDREN_RECURSIVE')
    
    # Linked True prevents from having a simulation world, which dimension increase
    # exponentially due to models duplication
    bpy.ops.object.duplicate(linked = True)    
    plant = bpy.context.view_layer.objects.active
    plant.name = "plant"+str(COUNTER_MODELS)
    if len(plant.children) != 0:
        plant.children[0].name = "leaves"+str(COUNTER_MODELS)
    COUNTER_MODELS += 1
    
    plant.location = location
    # plant.rotation_euler = (0.0, 0.0, yaw)
        
        
class TerrainHeightMap:
        
        def __init__(self, object):
            
            vertices = object.data.vertices
            matrix = object.matrix_world
            scale = matrix.to_scale()
            
            x = []
            y = []
            z = []
            for v in vertices:
                v_scaled = scale * v.co
                x.append(v_scaled[0])
                y.append(v_scaled[1])
                z.append(v_scaled[2])
            
            self.x = np.array(x)
            self.y = np.array(y)
            self.z = np.array(z)
    
        def get_height(self, x_pos, y_pos):
            z = float(griddata((self.x,self.y), self.z, (x_pos, y_pos), method='cubic'))
            
            if np.isnan(z):
                z = float(griddata((self.x,self.y), self.z, (x_pos, y_pos), method='nearest'))
            
            return z

def load_terrain(terrain_name, dest_file):
    """
    Load terrain file and return height map callable function
    """

    # Generate gazebo model for terrain
    base_gazebo_path = os.path.join(workdir, 'gazebo', 'models')
    if os.path.exists(os.path.join(base_gazebo_path, terrain_name)):
        print("Skipping gazebo model terrain generation, model already exists")
    else:
        templates = load_templates(workdir)
        terrains_folder_path = os.path.join(workdir, 'terrains')
        obj = terrain_name+'.obj'
        mtl = terrain_name+'.mtl'
        meshes_path = os.path.join(base_gazebo_path, terrain_name, 'meshes')

        os.makedirs(meshes_path, exist_ok=True)
        copy2(os.path.join(terrains_folder_path, obj), os.path.join(meshes_path, obj))
        copy2(os.path.join(terrains_folder_path, mtl), os.path.join(meshes_path, mtl))

        gazebo_model_folder_path = os.path.join(base_gazebo_path, terrain_name)
        with open(os.path.join(gazebo_model_folder_path, 'model.config'), 'w') as file:
            template = templates['model_config_template']
            file.write(template.substitute({
                'model_name': terrain_name,
                'author_name': 'Marco Ambrosio',
                'author_email': 'marco.ambrosio@polito.it'
            }))
        
        with open(os.path.join(gazebo_model_folder_path, 'model.sdf'), 'w') as file:
            template = templates['model_sdf_template']
            file.write(template.substitute({
                'model_name': terrain_name,
                'mesh_path': f'model://{terrain_name}/meshes/{obj}'
            }))

    # Load terrain in blender and return height map
    source_file = os.path.join(workdir, "terrains", terrain_name+".blend")
    print("Loading terrain from {}".format(source_file))
    with bpy.data.libraries.load(source_file) as (data_from, data_to):
        objects = []
        for obj in data_from.objects:
            objects.append({'name' : obj})    
    bpy.ops.wm.append(filepath=dest_file, directory=source_file+'/Object/', files=objects)
    
    object = bpy.data.objects[0]

    return TerrainHeightMap(object)


def get_plant_positions(number_of_rows, rows_in_group, magic_number, height_map, avg_plant_footprint, models_per_row, min_yaw, max_yaw):
    """
    Get the positions of the plants in the world
    """
    tmp = 0.0
    x_gird = []
    for i in range(number_of_rows):
        if i%rows_in_group==0 and i!=0:
            tmp += magic_number
        x_gird.append(tmp)
        tmp += magic_number
    x_gird = [x - max(x_gird)/2 for x in x_gird]
    y_grid = [0.0 + i*(avg_plant_footprint+magic_number/3) for i in range(models_per_row)]
    y_grid = [y - max(y_grid)/2 for y in y_grid]

    plant_positions = []
    for x in x_gird:
        for y in y_grid:
            x_pos = x + random.triangular(-1,1,0)*magic_number/10
            y_pos = y + random.triangular(-1,1,0)*magic_number/10
            plant_positions.append((
                x_pos,
                y_pos,
                height_map.get_height(x_pos, y_pos),
                random.uniform(min_yaw, max_yaw)))
    
    print("Number of plants: {}".format(len(plant_positions)))
    return plant_positions

                    

def load_templates(workdir):
    templates = dict()
    template_names = glob.glob('*_template', root_dir=os.path.join(workdir, 'templates'))
    for name in template_names:
        with open(os.path.join(workdir, 'templates', name), 'r') as file:
            templates[name] = Template(
                str.join('', file.readlines())
            )
    return templates


def generate_gazebo_models(workdir, plant_name):
    """
    Generate a standard Gazebo model (*.sdf) for each mesh file (*.obj) present in the folder.
    Returns a list of the names of the generated models.
    """

    #  Load Templates
    templates = load_templates(workdir)
    base_models_path = os.path.join(workdir, 'plants', plant_name)
    base_gazebo_path = os.path.join(workdir, 'gazebo', 'models')

    # Get list of obj and mtl files
    obj_list = glob.glob('*.obj', root_dir=base_models_path)
    obj_list.sort()
    mtl_list = glob.glob('*.mtl', root_dir=base_models_path)
    mtl_list.sort()
    textures_list = [
        *glob.glob('*.png', root_dir=base_models_path),
        *glob.glob('*.jpg', root_dir=base_models_path),
        *glob.glob('*.jpeg', root_dir=base_models_path),]

    # Check if models already exist
    if glob.glob(f'*{plant_name}*', root_dir=base_gazebo_path):
        raise Exception(f"Models of {plant_name} already exist")

    print(f"Found {len(obj_list)} obj files and {len(mtl_list)} mtl files")
    models = []
    for obj, mtl, i in zip(obj_list, mtl_list, range(1,len(obj_list)+1)):
        model_name = plant_name+f'{i}'
        gazebo_model_folder_path = os.path.join(base_gazebo_path, model_name)
        meshes_path = os.path.join(base_gazebo_path, model_name, 'meshes')

        # Create model folder and copy obj and mtl files, as well as textures
        os.makedirs(meshes_path, exist_ok=True)
        copy2(os.path.join(base_models_path, obj), os.path.join(meshes_path, obj))
        copy2(os.path.join(base_models_path, mtl), os.path.join(meshes_path, mtl))
        for file in textures_list:
            copy2(os.path.join(base_models_path, file), os.path.join(meshes_path, file))

        with open(os.path.join(gazebo_model_folder_path, 'model.config'), 'w') as file:
            template = templates['model_config_template']
            file.write(template.substitute({
                'model_name': model_name,
                'author_name': 'Marco Ambrosio',
                'author_email': 'marco.ambrosio@polito.it'
            }))
        
        with open(os.path.join(gazebo_model_folder_path, 'model.sdf'), 'w') as file:
            template = templates['model_sdf_template']
            file.write(template.substitute({
                'model_name': model_name,
                'mesh_path': f'model://{model_name}/meshes/{obj}'
            }))
        
        models.append(model_name)
    
    return tuple(models)


def generate_gazebo_world(workdir, plant_name, plant_positions, terrain_name):
    templates = load_templates(workdir)
    gazebo_models_path = os.path.join(workdir, 'gazebo', 'models')
    gazebo_world_path = os.path.join(workdir, 'gazebo', 'worlds', plant_name+'.world')

    models = glob.glob(f'*{plant_name}*', root_dir=gazebo_models_path)
    if len(models) == 0:
        raise Exception(f"Models of {plant_name} not found")
    else:
        print(f"Found {len(models)} models")
        print(f"Models: {models}")

    world = templates['world_template']
    include = templates['include_template']

    # Add terrain
    world = Template(world.substitute({
                'include': include.safe_substitute({
                    'pose': f'0 0 0 0 0 0',
                    'uri': f'model://{terrain_name}',
                    'name': terrain_name,
                })
            }))
        
    # Add plants
    for i, (x, y, z, yaw) in enumerate(plant_positions):
        model = random.choice(models)
        if i+1 == len(plant_positions):
            world = world.substitute({
                'include': include.safe_substitute({
                    'pose': f'{x} {y} {z} 0 0 {yaw}',
                    'uri': f'model://{model}',
                    'name': f'{plant_name}{i+1}',
                    'include': '',
                })
            })
        else:
            world = Template(world.substitute({
                'include': include.safe_substitute({
                    'pose': f'{x} {y} {z} 0 0 {yaw}',
                    'uri': f'model://{model}',
                    'name': f'{plant_name}{i+1}',
                })
            }))
    
    with open(gazebo_world_path, 'w') as file:
        file.write(world)



def generate_blender_model(plant_positions, workdir):
    global WORLD_FILE_PATH

    print("Generating Blender world...")
    plant_file_paths = glob.glob(os.path.join(workdir, 'plants', plant_name, "*.blend"))
    plant_list_range = list(range(len(plant_file_paths)))
    print("Found {} plants".format(len(plant_file_paths)))

    for i, (x, y, z, yaw) in enumerate(plant_positions):
        print("Placing plant {} of {}".format(i+1, len(plant_positions)))

        if i < len(plant_list_range):
            load_models(plant_file_paths[i], WORLD_FILE_PATH, (x,y,z))
        else:
            duplicate_models(plant_list_range, (x,y,z), yaw)

    bpy.ops.wm.save_as_mainfile(filepath=WORLD_FILE_PATH)

    
    
if __name__=="__main__":
    
    try:
        global COUNTER_MODELS
        COUNTER_MODELS = 0

        global WORLD_FILE_PATH

        # PARAMETERS
        with open("configuration.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        number_of_rows = config["number_of_rows"]
        rows_in_group = config["rows_in_group"]
        row_length = config["row_length"]
        magic_number = config["magic_number"]
        avg_plant_footprint = config["avg_plant_footprint"]
        plant_name = config["plant_name"]
        terrain_name = config["terrain_name"]
        generate_blender_models_flag = config["generate_blender_model"]
        generate_gazebo_models_flag = config["generate_gazebo_models"]
        generate_gazebo_world_flag = config["generate_gazebo_world"]

        models_per_row = int(round(row_length/(avg_plant_footprint+magic_number/3), 0))
        min_yaw = -math.pi
        max_yaw = math.pi

        
        # PATHS
        workdir = os.getcwd()
        WORLD_FILE_PATH = os.path.join(workdir, "world.blend") # where to save the world

        # select all objects and delete
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        height_map = load_terrain(terrain_name, WORLD_FILE_PATH)
        plant_positions = get_plant_positions(
            number_of_rows, rows_in_group, magic_number, height_map,
            avg_plant_footprint, models_per_row, min_yaw, max_yaw)

        
        if generate_blender_models_flag:
            generate_blender_model(plant_positions, workdir)

        if generate_gazebo_models_flag:
            generate_gazebo_models(workdir, plant_name)
        
        if generate_gazebo_world_flag:
            generate_gazebo_world(workdir, plant_name, plant_positions, terrain_name)

    except Exception as e:
        bpy.ops.wm.quit_blender()
        raise e
    finally:
        bpy.ops.wm.quit_blender()