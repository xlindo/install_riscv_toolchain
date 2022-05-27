#!/usr/bin/python3
#
'''
Author: hi@xlindo.com
Date: 2022-05-24 14:44:06
LastEditTime: 2022-05-27 23:22:42
LastEditors: hi@xlindo.com
Description: This project helps automatically install
    * riscv-gnu-toolchain
    * riscv-isa-sim (spike)
    * riscv-pk
Prerequisites:
    * Debian-like, Ubuntu
        * RISC-V utils
            * apt update
            * apt install -y autoconf automake autotools-dev curl python3 libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev libisl-dev gdb git device-tree-compiler wget
        * LLVM
            * apt install libssl-dev ninja-build -y
    * CentOS-like, CentOS 7
        * RISC-V utils
            * yum -y install autoconf automake python3 python3-devel libmpc-devel mpfr-devel gmp-devel gawk  bison flex texinfo patchutils gcc gcc-c++ zlib-devel expat-devel git make dtc
            * isl **IMPORTANT!!!**
                * wget ftp://gcc.gnu.org/pub/gcc/infrastructure/isl-0.18.tar.bz2
                * tar -jxvf isl-0.18.tar.bz2 && cd isl-0.18 
                * ./configure && make -j48 && make install
                * echo "export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH" >> ~/.bashrc
        * LLVM
            * GCC 7 (use scl)
                * yum install centos-release-scl -y
                * yum install devtoolset-7 -y
                * scl enable devtoolset-7 bash
                * source /opt/rh/devtoolset-7/enable
                * echo "source /opt/rh/devtoolset-7/enable" >> ~/.bashrc
            * CMake 3.13.4+ (required by LLVM)
                * yum install openssl openssl-devel -y
                * git clone https://github.91chi.fun/https://github.com/Kitware/CMake && cd CMake
                * ./bootstrap && make
                * make install
            * Ninja 
                * re2c
                    * git clone https://github.91chi.fun/https://github.com/skvadrik/re2c && cd re2c
                    * autoreconf -i -W all
                    * mkdir .build && cd .build && ../configure && make -j48 && make install
                * ninja
                    * git clone https://github.91chi.fun/https://github.com/ninja-build/ninja && cd ninja
                    * python3 configure.py --bootstrap
                    * [cp ninja /usr/bin] (or other path)
Usage:
    * By default, the installation path is `./riscv_install` (`RISCV_INSTALL`) and `llvm-project/install`
    * [Auto] `python3 install_riscv_toolchain.py auto`
        * All repos ({linux} {elf} {elf-rvv} {llvm}) will be downloaded and built without interruption
    * [Semi-auto] `python3 install_riscv_toolchain.py all`
        * All repos ({linux} {elf} {elf-rvv} {llvm}) will **almost** automatically except some downloading selections.
    * [Partially] `python3 install_riscv_toolchain.py {linux} {elf} {elf-rvv} {llvm}`
        * `linux` for `riscv64-linux-unknown-gnu`
        * `elf` for `riscv64-unknown-elf`
        * `elf-rvv` for `riscv64-unknown-elf` with `rvv`
        * `llvm` for LLVM clang
    * [Manually]`python3 install_riscv_toolchain.py` then **follow the prompts**
        * Clone riscv-gnu-toolchain, riscv-isa-sim (spike), riscv-pk or not
        * Update submodules in `riscv-gnu-toolchain` or not (qemu will be removed)
        * Choose build target from `riscv64-linux-unknown-gnu`, `riscv64-unknown-elf`, `riscv64-unknown-elf` with `rvv`, LLVM
        * Waiting, and the compiling result will be in `RISCV_INSTALL`
Example:
    `python3 install_riscv_toolchain.py elf elf-rvv`

    This will automatically install `spike`, `pk`, `riscv64-unknown-elf`-toolchain and `riscv64-unknown-elf`-toolchain(with rvv) in `./riscv_install/{elf, elf-rvv}`.
Options in the script:
    * RISCV_INSTALL, the installation path
    * NUM_CORES, the number of cores for your CPU
    * *_REPO urls, in case you have unlimited github access
    * LLVM_BUILD_TOOL and LLVM_BUILD_BIN, if no ninja is installed
ISSUES:
    * The modules failed to update in riscv-gnu-toolchain
        * Remove the whole repo and re-clone may be fast
License: GPLv3
Copyright (c) 2022 by https://xlindo.com, All Rights Reserved.
'''
from multiprocessing import Pool
import os
import sys

RISCV_INSTALL = os.getcwd() + "/riscv_install"
NUM_CORES = "48"
LLVM_BUILD_TOOL = "Ninja"
LLVM_BUILD_BIN = "ninja"
#LLVM_BUILD_TOOL = "Unix Makefiles"
#LLVM_BUILD_BIN = "make"

LLVM_REPO = "https://github.91chi.fun/https://github.com/llvm/llvm-project"

RISCV_GNU_TOOLCHAIN_REPO = "https://github.91chi.fun/https://github.com/riscv/riscv-gnu-toolchain"
RISCV_PK_REPO = "https://github.91chi.fun/https://github.com/riscv-software-src/riscv-pk.git"
RISCV_SPIKE_REPO = "https://github.91chi.fun/https://github.com/riscv-software-src/riscv-isa-sim"
RISCV_REPOS = [RISCV_GNU_TOOLCHAIN_REPO, RISCV_PK_REPO, RISCV_SPIKE_REPO]

DOT_GITMODULES = r"""[submodule "riscv-binutils"]
	path = riscv-binutils
	url = https://github.91chi.fun/https://github.com/riscv-collab/riscv-binutils-gdb.git
	branch = riscv-binutils-2.38
[submodule "riscv-gcc"]
	path = riscv-gcc
	url = https://github.91chi.fun/https://github.com/riscv-collab/riscv-gcc.git
	branch = riscv-gcc-12.1.0
[submodule "glibc"]
	path = glibc
	url = https://gitee.com/mirrors_community_sourceware/glibc.git
[submodule "riscv-dejagnu"]
	path = riscv-dejagnu
	url = https://github.91chi.fun/https://github.com/riscv-collab/riscv-dejagnu.git
	branch = riscv-dejagnu-1.6
[submodule "newlib"]
	path = newlib
	url = https://gitee.com/mirrors_community_sourceware/newlib-cygwin_1.git
	branch = master
[submodule "riscv-gdb"]
	path = riscv-gdb
	url = https://github.91chi.fun/https://github.com/riscv-collab/riscv-binutils-gdb.git
	branch = fsf-gdb-10.1-with-sim
[submodule "musl"]
	path = musl
	url = https://gitee.com/mirrors_community_musl-libc/musl.git
	branch = master
"""

ENV_PATH = os.getenv("PATH")


def clone_repo(repo):
    print(repo + " cloning")
    os.system("git clone " + repo)


def clone_riscv_repos(auto=False):
    if not auto:
        opt_clone_repo = input(
            "Re-clone riscv-gnu-toolchain, riscv-isa-sim (spike), riscv-pk? (y/[N]) >>> "
        )
    else:
        opt_clone_repo = 'y'

    if opt_clone_repo in ['y', 'Y']:
        if os.path.exists("riscv-gnu-toolchain"):
            os.system("rm -rf riscv-gnu-toolchain")
        if os.path.exists("riscv-pk"):
            os.system("rm -rf riscv-pk")
        if os.path.exists("riscv-isa-sim"):
            os.system("rm -rf riscv-isa-sim")

        with Pool(len(RISCV_REPOS)) as pl:
            pl.map(clone_repo, RISCV_REPOS)

        update_gitmodules()
    else:
        print("Skip cloning repos...")


def remkdir_cd_build():
    if os.path.exists("build"):
        os.system("rm -rf build")
    os.mkdir("build")
    os.chdir("build")


def update_gitmodules():
    os.chdir("riscv-gnu-toolchain")
    os.system("git rm qemu")
    os.system("rm -rf .gitmodules")
    with open(".gitmodules", "w") as f:
        f.write(DOT_GITMODULES)
    os.system("git submodule update --init --recursive")
    os.chdir("..")


def build_riscv64_tools(targets):
    if not targets:
        return

    for tg in targets:
        INSTALL_PATH = RISCV_INSTALL + '/' + tg
        if "elf" == tg:
            GCC_BRANCH = "cd riscv-gcc && git checkout riscv-gcc-12.1.0 && cd .."
            TOOLCHAIN_CONFIG_CMD = "../configure --prefix=" + INSTALL_PATH
            TOOLCHAIN_MAKE_CMD = "make -j" + NUM_CORES
            PK_CONFIG_CMD = "../configure --host=riscv64-unknown-elf CC=riscv64-unknown-elf-gcc --prefix="+INSTALL_PATH
        elif "elf-rvv" == tg:
            GCC_BRANCH = "cd riscv-gcc && git checkout riscv-gcc-rvv-next && cd .."
            TOOLCHAIN_CONFIG_CMD = "../configure --with-arch=rv64gcv --with-abi=lp64d --prefix=" + INSTALL_PATH
            TOOLCHAIN_MAKE_CMD = "make -j" + NUM_CORES
            PK_CONFIG_CMD = "../configure --host=riscv64-unknown-elf CC=riscv64-unknown-elf-gcc --prefix="+INSTALL_PATH
        elif "linux" == tg:
            GCC_BRANCH = "cd riscv-gcc && git checkout riscv-gcc-12.1.0 && cd .."
            TOOLCHAIN_CONFIG_CMD = "../configure --prefix=" + INSTALL_PATH
            TOOLCHAIN_MAKE_CMD = "make linux -j" + NUM_CORES
            PK_CONFIG_CMD = "../configure --host=riscv64-unknown-linux-gnu CC=riscv64-unknown-linux-gnu-gcc --prefix="+INSTALL_PATH
        else:
            print("Invalid target!")
            continue

        if os.path.exists(INSTALL_PATH):
            os.system("rm -rf " + INSTALL_PATH)
        # install riscv-gnu-toolchain
        os.chdir("riscv-gnu-toolchain")
        os.system(GCC_BRANCH)
        remkdir_cd_build()
        os.system(TOOLCHAIN_CONFIG_CMD)
        os.system(TOOLCHAIN_MAKE_CMD)
        os.chdir("../..")

        # install riscv-pk
        os.chdir("riscv-pk")
        remkdir_cd_build()
        os.environ["PATH"] = INSTALL_PATH + "/bin:" + ENV_PATH
        os.system(PK_CONFIG_CMD)
        os.system("make -j48 && make install")
        os.chdir("../..")

        # install riscv-isa-sim (spike)
        os.chdir("riscv-isa-sim")
        remkdir_cd_build()
        os.system("../configure --prefix=" + INSTALL_PATH)
        os.system("make -j48 && make install")
        os.chdir("../..")


def clone_llvm_repo(auto=False):
    if not auto:
        opt_clone_repo = input("Re-clone llvm-project repo? (y/[N]) >>> ")
    else:
        opt_clone_repo = 'y'

    if opt_clone_repo in ['y', 'Y']:
        if os.path.exists("llvm-project"):
            os.system("rm -rf llvm-project")
        os.system("git clone " + LLVM_REPO)
    else:
        print("Skip cloning llvm-project...")


def build_llvm():
    os.chdir("llvm-project")
    remkdir_cd_build()

    os.system('cmake -G "' + LLVM_BUILD_TOOL + '" -DCMAKE_C_COMPILER=`which gcc` -DCMAKE_CXX_COMPILER=`which g++` -DCMAKE_ASM_COMPILER=`which gcc` -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../install -DLLVM_TARGETS_TO_BUILD="RISCV" -DLLVM_ENABLE_PROJECTS="clang" ../llvm')
    os.system(LLVM_BUILD_BIN + " -j" + NUM_CORES +
              " && " + LLVM_BUILD_BIN + " install")


if __name__ == "__main__":
    targets = sys.argv[1:]

    if 1 == len(targets) and "auto" == targets[0]:
        # Re-clone and install all tools without interruption
        clone_llvm_repo(auto=True)
        build_llvm()
        clone_riscv_repos(auto=True)
        build_riscv64_tools(["elf", "elf-rvv", "linux"])
        print("Finished! You can find the installation for LLVM tools in llvm-project/install and RISC-V utils in riscv_install.")
        sys.exit(0)

    if 1 == len(targets) and "all" == targets[0]:
        # Install all tools bootstrap
        valid_rv_targets = ["elf", "elf-rvv", "linux", "llvm"]
    else:
        # Install specific targets
        valid_rv_targets = [v_t for v_t in targets if v_t in [
            "elf", "elf-rvv", "linux", "llvm"]]

    if valid_rv_targets:
        # Automatically install riscv-gnu-toolchain, riscv-isa-sim (spike), riscv-pk without interruption, BUT all things will be reconstructed.
        if "llvm" in valid_rv_targets:
            # Clone repo
            clone_llvm_repo()
            build_llvm()
            valid_rv_targets.remove("llvm")
        if valid_rv_targets:
            # if targets and targets[0] in ["elf", "elf-rvv", "linux"]:
            # targets only contain riscv utils
            clone_riscv_repos()
            build_riscv64_tools(valid_rv_targets)
    else:
        opt_build_target = input("""Choose the building targets: (1/2/3/4)
1. riscv64-linux-unknown-gnu, spike and pk
2. riscv64-unknown-elf, spike and pk
3. riscv64-unknown-elf with rvv, spike and pk
4. LLVM latest

>>> """)

        if "4" == opt_build_target:
            # Clone repo
            clone_llvm_repo()
            build_llvm()
        elif opt_build_target in ["1", "2", "3"]:
            # Clone repos
            opt_clone_repo = input(
                "Re-clone riscv-gnu-toolchain, riscv-isa-sim (spike), riscv-pk? (y/[N]) >>> "
            )
            if opt_clone_repo in ['y', 'Y']:
                clone_riscv_repos()
            else:
                print("Skip cloning repos...")

            # modify riscv-gnu-toolchain to local source
            # time consuming
            opt_update_gitmodules = input(
                "Update the submodules in riscv-gnu-toolchain? (y/[N]) >>> ")
            if opt_update_gitmodules in ['y', 'Y']:
                update_gitmodules()
            else:
                print("Skip updating gitmodules...")

            if "1" == opt_build_target:
                build_riscv64_tools(["linux"])
            elif "2" == opt_build_target:
                build_riscv64_tools(["elf"])
            elif "3" == opt_build_target:
                build_riscv64_tools(["elf-rvv"])

        else:
            print("Invalid input...quit...")
            sys.exit(1)

    if valid_rv_targets:
        print("Script finished! You can find the installation for RISC-V tools in " + RISCV_INSTALL)
    if "llvm" in targets:
        print("You can find the installation for LLVM tools in llvm-project/install")
