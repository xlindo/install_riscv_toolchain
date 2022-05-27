# Install RISC-V toolchain

This project helps automatically install

* `riscv-gnu-toolchain`
* `riscv-isa-sim (spike)`
* `riscv-pk`
   
## Prerequisites

### Debian-like, Ubuntu

* RISC-V utils
    * `apt update`
    * `apt install -y autoconf automake autotools-dev curl python3 libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev libisl-dev gdb git device-tree-compiler wget`
* LLVM
    * `apt install libssl-dev ninja-build -y`

### CentOS-like, CentOS 7

* RISC-V utils
    * `yum -y install autoconf automake python3 python3-devel libmpc-devel mpfr-devel gmp-devel gawk  bison flex texinfo patchutils gcc gcc-c++ zlib-devel expat-devel git make dtc`
* LLVM
    * isl **IMPORTANT!!!**
        * `wget ftp://gcc.gnu.org/pub/gcc/infrastructure/isl-0.18.tar.bz2`
        * `tar -jxvf isl-0.18.tar.bz2 && cd isl-0.18 `
        * `./configure && make -j48 && make install`
        * `echo "export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH" >> ~/.bashrc`
    * GCC 7 (use scl)
        * `yum install centos-release-scl -y`
        * `yum install devtoolset-7 -y`
        * `scl enable devtoolset-7 bash`
        * `source /opt/rh/devtoolset-7/enable`
        * `echo "source /opt/rh/devtoolset-7/enable" >> ~/.bashrc` 
    * CMake 3.13.4+ (required by LLVM)
        * `yum install openssl openssl-devel -y`
        * `git clone https://github.91chi.fun/https://github.com/Kitware/CMake && cd CMake`
        * `./bootstrap && make`
        * `make install`
    * Ninja 
        * re2c
            * `git clone https://github.91chi.fun/https://github.com/skvadrik/re2c && cd re2c`
            * `autoreconf -i -W all`
            * `mkdir .build && cd .build && ../configure && make -j48 && make install`
        * ninja
            * `git clone https://github.91chi.fun/https://github.com/ninja-build/ninja && cd ninja`
            * `python3 configure.py --bootstrap`
            * [`cp ninja /usr/bin`] (or other path)

## Getting Started

By default, the installation path is `./riscv_install` (`RISCV_INSTALL`)

This script could be executed with or without an option.

* [Auto install] `python3 install_riscv_toolchain.py {linux} {elf} {elf-rvv}`
    1. `linux` for `riscv64-linux-unknown-gnu`
    2. `elf` for `riscv64-unknown-elf`
    3. `elf-rvv` for `riscv64-unknown-elf` with `rvv`
    4. `llvm` for LLVM clang
* [Manually]`python3 install_riscv_toolchain.py` and follow the prompts:
    1. Clone riscv-gnu-toolchain, riscv-isa-sim (spike), riscv-pk or not
    2. Update submodules in `riscv-gnu-toolchain` or not (qemu will be removed)
    3. Choose build target from `riscv64-linux-unknown-gnu`, `riscv64-unknown-elf`, `riscv64-unknown-elf` with `rvv`
    4. Waiting, and the compiling result will be in `RISCV_INSTALL`

### Example
    
`python3 install_riscv_toolchain.py elf elf-rvv`

This will automatically install `spike`, `pk`, `riscv64-unknown-elf`-toolchain and `riscv64-unknown-elf`-toolchain(with rvv) in `./riscv_install/{elf, elf-rvv}`.

### Options in the script

* RISCV_INSTALL, the installation path
* NUM_CORES, the number of cores for your CPU
* *_REPO urls, in case you have unlimited github access

## ISSUES

* The modules failed to update in riscv-gnu-toolchain
    * Remove the whole repo and re-clone may be a fast way

## Authors

* **hi@xlindo.com** from 2022.5

## License

This project is licensed under GPLv3.
