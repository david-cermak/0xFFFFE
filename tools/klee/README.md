# KLEE Symbolic Execution Engine

KLEE is a symbolic execution engine built on top of the LLVM compiler infrastructure. It can automatically generate test cases that achieve high coverage on a diverse set of complex and environmentally-intensive programs. KLEE works by running a program symbolically, and using a constraint solver to check the feasibility of paths in the program.

## Setup and Usage

```bash
$ git clone https://github.com/klee/klee.git
$ cd klee
$ podman build -t klee/klee .
$ podman run --rm -ti --ulimit='stack=-1:-1' klee/klee
```

## Simple Example: Multi-Language Hello World

Let's start with a simple example that demonstrates KLEE's symbolic execution capabilities.

1- Use the provided example program (`hello_multilang.c` in this folder) and copy it into the KLEE container and compile:

```bash
# First, copy the file into the running container
$ podman cp hello_multilang.c <container_id>:/tmp/
$ podman exec -it <container_id> bash

# Inside the container:
$ cd /tmp
$ clang -emit-llvm -O0 -c -g -I/usr/include/klee hello_multilang.c
$ klee hello_multilang.bc
```

3- KLEE will explore all possible paths and generate test cases:

```bash
$ ls klee-out-0/
# You'll see generated test cases for each branch
$ klee-stats klee-out-0/
# Shows coverage statistics
```
