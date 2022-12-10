> Project: "Automatic Row Crop Generator"

> Owner: "Marco Ambrosio, Brenno Tuberga" 

> Date: "2022:12" 

---

# Automatic Row Crop Generator User Guide

## Licence 

All the code and models inside this repository are released under the MIT Licence.

> MIT License\
> \
> Copyright (c) 2022 Marco Ambrosio, Brenno Tuberga\
> \
> Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:\
> \
> The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software. \
> \
>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Description of the project

The code in this repository provides useful tools to automatically generate models of row-based crops for Blender and Gazebo.

## Installation procedure

Open a terminal inside this folder and run the following command:

``` blender --python install_requirements.py ```

## User Guide

Write something useful for the user


Row lenght is disposed along Y axis, while field width is disposed along X axis.

Blender models of the plants must have the origin of the object at the bottom of the plant. See the provided models for reference.

Meshes for Gazebo must be in OBJ format. All the texture images must stay in the same folder as the model. Here is a list of suggested parameters for the OBJ export:
- Forward: +Y
- Up: +Z
- Scale: 1
- Path Mode: Strip

Folder structure for plants and terrains:

```
plants
├── artichoke
│   ├── artichoke1
│   │   ├── artichoke1.blend
│   │   ├── artichoke1.mtl
│   │   ├── artichoke1.obj
│   │   └── textures
│   │       ├── petalo1.jpg
│   │       └── texture foglia.jpg
│   └── artichokeN
│       ├── artichokeN.blend
│       ├── artichokeN.mtl
│       ├── artichokeN.obj
│       └── textures
│           ├── petalo1.jpg
│           └── texture foglia.jpg
│
├── another_plant
│   ├── another_plant1

```


## Authors

Marco Ambrosio, Brenno Tuberga

## Acknowledgments

This project has been developed thank to PIC4SeR Center.