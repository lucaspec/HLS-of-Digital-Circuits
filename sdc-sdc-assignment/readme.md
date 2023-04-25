# Course Project: Implement Your Modulo Scheduler (SDC-SDC)

## Introduction

This is the repository for the first student project in the course **Synthesis of Digital Circuits**.
The goal of this project is to practice the theory of modulo scheduling we have covered in this lecture.

## Package Dependencies

### Graphviz (A Graph Visualization Engine)

On Ubuntu machines, you can get the required dependencies via package manager:

```sh
sudo apt-get install graphviz graphviz-dev
``` 

### Python
```
python 3.7
pygraphviz 1.9
llvmlite 0.39.1
PuLP 2.7.0
networkx 2.8
``` 
### LLVM (Compiler Frontend, Optional)

As in many HLS compilers, we use LLVM as the frontend to generate intermediate representation (IR) from C code.
For the purpose of this project, we provide the IR code of the HLS kernels of the assignments.
