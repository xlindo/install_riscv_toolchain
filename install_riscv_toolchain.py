#!/usr/bin/python3
'''
Author: hi@xlindo.com
Date: 2022-05-24 14:44:06
LastEditTime: 2022-05-24 19:20:29
LastEditors: hi@xlindo.com
Description: Automatically install
    * riscv-gnu-toolchain
    * riscv-isa-sim (spike)
    * riscv-pk
Prerequisites:
    * (Debian-like, Ubuntu) apt install autoconf automake autotools-dev curl python3 libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev libisl-dev gdb -y
    * (CentOS-like) yum -y install autoconf automake python3 libmpc-devel mpfr-devel gmp-devel gawk  bison flex texinfo patchutils gcc gcc-c++ zlib-devel expat-devel
Usage:
    0. By default, the installation path is `./riscv_install` (`RISCV_INSTALL`)
    1. [New install] `python3 install_riscv_toolchain.py {linux | elf | elf-rvv}`
        1.1 `linux` for `riscv64-linux-unknown-gnu`
        1.2 `elf` for `riscv64-unknown-elf`
        1.3 `elf-rvv` for `riscv64-unknown-elf` with `rvv`
    2. [Manually]`python3 install_riscv_toolchain.py` and **follow the prompts**:
        2.1. Clone riscv-gnu-toolchain, riscv-isa-sim (spike), riscv-pk or not
        2.2. Update submodules in `riscv-gnu-toolchain` or not (qemu will be removed)
        2.3. Choose build target from `riscv64-linux-unknown-gnu`, `riscv64-unknown-elf`, `riscv64-unknown-elf` with `rvv`
        2.4. Waiting, and the compiling result will be in `RISCV_INSTALL`
License: GPLv3
Copyright (c) 2022 by https://xlindo.com, All Rights Reserved.
'''
from multiprocessing import Pool
import os
import sys

RISCV_INSTALL = os.getcwd() + "/riscv_install"

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


def clone_repo(repo):
    print(repo + " cloning")
    os.system("git clone " + repo)


def clone_repos():
    with Pool(len(RISCV_REPOS)) as pl:
        pl.map(clone_repo, RISCV_REPOS)


def update_gitmodules():
    os.chdir("riscv-gnu-toolchain")
    os.system("git rm qemu")
    os.system("rm -rf .gitmodules")
    with open(".gitmodules", "w") as f:
        f.write(DOT_GITMODULES)
    os.system("git submodule update --init --recursive")
    os.chdir("..")


def riscv64_linux_unknown_gnu_12():
    RISCV_INSTALL_LINUX_12 = RISCV_INSTALL + "/linux_12"
    if os.path.exists(RISCV_INSTALL_LINUX_12):
        os.system("rm -rf " + RISCV_INSTALL_LINUX_12)
    # install riscv-gnu-toolchain
    os.chdir("riscv-gnu-toolchain")
    os.system("cd riscv-gcc && git reset --hard origin/riscv-gcc-12.1.0")
    os.system("./configure --prefix=" + RISCV_INSTALL_LINUX_12)
    os.system("make linux -j48")
    os.chdir("..")

    # install riscv-pk
    os.chdir("riscv-pk")
    if os.path.exists("build"):
        os.system("rm -rf build")
    os.mkdir("build")
    os.chdir("build")
    os.environ["PATH"] = RISCV_INSTALL_LINUX_12 + "/bin:" + os.getenv("PATH")
    os.system("../configure --host=riscv64-unknown-linux-gnu --prefix=" +
              RISCV_INSTALL_LINUX_12)
    os.system("echo $PATH")
    os.system("make -j48 && make install")
    os.chdir("../..")

    # install riscv-isa-sim (spike)
    os.chdir("riscv-isa-sim")
    if os.path.exists("build"):
        os.system("rm -rf build")
    os.mkdir("build")
    os.chdir("build")
    os.system("../configure --prefix=" + RISCV_INSTALL_LINUX_12)
    os.system("make -j48 && make install")
    os.chdir("../..")

    return RISCV_INSTALL_LINUX_12


def riscv64_unknown_elf_12():
    RISCV_INSTALL_12 = RISCV_INSTALL + "/unknown_elf_12"
    if os.path.exists(RISCV_INSTALL_12):
        os.system("rm -rf " + RISCV_INSTALL_12)
    # install riscv-gnu-toolchain
    os.chdir("riscv-gnu-toolchain")
    os.system("cd riscv-gcc && git reset --hard origin/riscv-gcc-12.1.0")
    os.system("./configure --prefix=" + RISCV_INSTALL_12)
    os.system("make -j48")
    os.chdir("..")

    # install riscv-pk
    os.chdir("riscv-pk")
    if os.path.exists("build"):
        os.system("rm -rf build")
    os.mkdir("build")
    os.chdir("build")
    os.environ["PATH"] = RISCV_INSTALL_12 + "/bin:" + os.getenv("PATH")
    os.system("../configure --host=riscv64-unknown-elf --prefix=" +
              RISCV_INSTALL_12)
    os.system("make -j48 && make install")
    os.chdir("../..")

    # install riscv-isa-sim (spike)
    os.chdir("riscv-isa-sim")
    if os.path.exists("build"):
        os.system("rm -rf build")
    os.mkdir("build")
    os.chdir("build")
    os.system("../configure --prefix=" + RISCV_INSTALL_12)
    os.system("make -j48 && make install")
    os.chdir("../..")

    return RISCV_INSTALL_12


def riscv64_unknown_elf_rvv_12():
    RISCV_INSTALL_LINUX_RVV_12 = RISCV_INSTALL + "/linux_rvv_12"
    if os.path.exists(RISCV_INSTALL_LINUX_RVV_12):
        os.system("rm -rf " + RISCV_INSTALL_LINUX_RVV_12)
    # install riscv-gnu-toolchain
    os.chdir("riscv-gnu-toolchain")
    os.system("cd riscv-gcc && git reset --hard origin/riscv-gcc-rvv-next")
    os.system("./configure --with-arch=rv64gcv --with-abi=lp64d --prefix=" + RISCV_INSTALL_LINUX_RVV_12)
    os.system("make -j48")
    os.chdir("..")

    # install riscv-pk
    os.chdir("riscv-pk")
    if os.path.exists("build"):
        os.system("rm -rf build")
    os.mkdir("build")
    os.chdir("build")
    os.environ["PATH"] = RISCV_INSTALL_LINUX_RVV_12 + \
        "/bin:" + os.getenv("PATH")
    os.system("../configure --host=riscv64-unknown-elf --prefix=" +
              RISCV_INSTALL_LINUX_RVV_12)
    os.system("make -j48 && make install")
    os.chdir("../..")

    # install riscv-isa-sim (spike)
    os.chdir("riscv-isa-sim")
    if os.path.exists("build"):
        os.system("rm -rf build")
    os.mkdir("build")
    os.chdir("build")
    os.system("../configure --prefix=" + RISCV_INSTALL_LINUX_RVV_12)
    os.system("make -j48 && make install")
    os.chdir("../..")

    return RISCV_INSTALL_LINUX_RVV_12


if __name__ == "__main__":
    print("RISC-V toolchain will be installed into " + RISCV_INSTALL)
    install_path = ""
    if sys.argv[1] == "linux":
        # Automatically install riscv-gnu-toolchain, riscv-isa-sim (spike), riscv-pk without interruption, BUT all things will be reconstructed.
        clone_repos()
        update_gitmodules()
        install_path = riscv64_linux_unknown_gnu_12()
        sys.exit(0)
    elif sys.argv[1] == "elf":
        # Automatically install riscv-gnu-toolchain, riscv-isa-sim (spike), riscv-pk without interruption.
        clone_repos()
        update_gitmodules()
        install_path = riscv64_unknown_elf_12()
        sys.exit(0)
    elif sys.argv[1] == "elf-rvv":
        # Automatically install riscv-gnu-toolchain, riscv-isa-sim (spike), riscv-pk without interruption.
        clone_repos()
        update_gitmodules()
        install_path = riscv64_unknown_elf_rvv_12()
        sys.exit(0)
    else:
        # Clone repos
        opt_clone_repos = input(
            "Clone riscv-gnu-toolchain, riscv-isa-sim (spike), riscv-pk? (y/[N]) "
        )
        if opt_clone_repos in ['y', 'Y']:
            clone_repos()
        else:
            print("Skip cloning repos...")

        # modify riscv-gnu-toolchain to local source
        # time consuming
        opt_update_gitmodules = input(
            "Update the Modules for riscv-gnu-toolchain? (y/[N]) ")
        if opt_update_gitmodules in ['y', 'Y']:
            update_gitmodules()
        else:
            print("Skip updating gitmodules...")

        opt_build_targets = input("""Choose the building targets: (1/2/3)
1. riscv64-linux-unknown-gnu, spike and pk
2. riscv64-unknown-elf, spike and pk
3. riscv64-unknown-elf with rvv, spike and pk

>>> """)
        if "1" == opt_build_targets:
            install_path = riscv64_linux_unknown_gnu_12()
        elif "2" == opt_build_targets:
            install_path = riscv64_unknown_elf_12()
        elif "3" == opt_build_targets:
            install_path = riscv64_unknown_elf_rvv_12()
        else:
            print("Invalid input...quit...")

    print("Script finished! You can set the install path " + install_path +
          " in environment.")
