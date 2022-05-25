# Install RISC-V toolchain

This project helps automatically install

* `riscv-gnu-toolchain`
* `riscv-isa-sim (spike)`
* `riscv-pk`
   
## Prerequisites

* (Debian-like, Ubuntu) `apt install autoconf automake autotools-dev curl python3 libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev libisl-dev gdb -y`
* (CentOS-like) `yum install autoconf automake python3 libmpc-devel mpfr-devel gmp-devel gawk  bison flex texinfo patchutils gcc gcc-c++ zlib-devel expat-devel -y`

## Getting Started

By default, the installation path is `./riscv_install` (`RISCV_INSTALL`)

This script could be executed with or without an option.

* [Auto install] `python3 install_riscv_toolchain.py {linux} {elf} {elf-rvv}`
    1. `linux` for `riscv64-linux-unknown-gnu`
    2. `elf` for `riscv64-unknown-elf`
    3. `elf-rvv` for `riscv64-unknown-elf` with `rvv`
* [Manually]`python3 install_riscv_toolchain.py` and follow the prompts:
    1. Clone riscv-gnu-toolchain, riscv-isa-sim (spike), riscv-pk or not
    2. Update submodules in `riscv-gnu-toolchain` or not (qemu will be removed)
    3. Choose build target from `riscv64-linux-unknown-gnu`, `riscv64-unknown-elf`, `riscv64-unknown-elf` with `rvv`
    4. Waiting, and the compiling result will be in `RISCV_INSTALL`

### Example:
    
`python3 install_riscv_toolchain.py elf elf-rvv`

This will automatically install `spike`, `pk`, `riscv64-unknown-elf`-toolchain and `riscv64-unknown-elf`-toolchain(with rvv) in `./riscv_install/{elf, elf-rvv}`.

### Options in the script:

 * RISCV_INSTALL, the installation path
 * NUM_CORES, the number of cores for your CPU
 * *_REPO urls, in case you have unlimited github access

## Authors

* **hi@xlindo.com** from 2022.5

## License

This project is licensed under GPLv3.
