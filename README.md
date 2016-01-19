# TPM 2.0 Simulator Extraction Script

The purpose of this script is to extract the source code from the publicly available PDF version 01.16 of the *Trusted Platform Module Library Specification* published by the Trusted Computing Group (TCG).

The result of the extraction scripts is a complete set of the source files for a __Trusted Platform Module (TPM) 2.0 Simulator__, which runs under Windows, Linux, as well as Genode (by applying the appropriate patches).

*Note:* The extraction script also works with a Microsoft Word-based FODT-version of the more recent specifications (e.g., version 01.19), which are however only available to TCG members.

*License:* The files of this project are licensed under **BSD 2-Clause License** (except where indicated otherwise).

---

## User Instructions


### Extraction

#### Requirements
Make sure the following packages are installed on your system:
```
cmake
build-essential
python-bs4
python-pip
python-dev
```

Also install the python module "pyastyle" for formatted output:
```
pip install pyastyle
```

#### Extracting the source code
1. Open a Terminal and navigate to the project folder `tpm2simulator`
2. Edit configuration settings in the file `tpm2simulator/scripts/settings.py`
   and change `SET = False` to `SET = True` when finished
3. Create a folder named `build` and run the following command inside:
```
cmake -G "Unix Makefiles" ../cmake -DCMAKE_BUILD_TYPE=Debug -DSPEC_VERSION=116
```
This command
  * runs the Python script to extract the simulator source code
  * patches files containing the source code
  * generates a Makefile used for building the simulator

#### Building and running the simulator
1. Build the simulator
```
make
```

2. Run the simulator:
```
./Simulator
```
(If there are any error messages at startup, restart simulator)


### Testing
In order to test if the simulator is working correctly, we use [IBM's TPM 2.0 TSS](https://github.com/stwagnr/ibmtpm20tss)

1. Open a Terminal and start the TPM simulator

2. Open another Terminal and navigate to the project folder `ibmtpm20tss/utils`

3. Build the TSS:
```
make
```
4. Run the tests:
```
./reg.sh -a
```

---

### Credits

This project was created by **[Steffen Wagner](https://github.com/stwagnr)** ([Fraunhofer AISEC](https://www.aisec.fraunhofer.de)).

Special thanks to **[Sergej Proskurin](https://github.com/prosig)** and **[Tamás Bakos](https://github.com/tamasbakos)** for their support in implementing the script.

**IBM's TPM 2.0 TSS** was created by [Ken Goldman](http://sourceforge.net/u/kagoldman) and is licensed under the Berkeley Software Distribution (BSD) License. We'd like to thank Ken for implementing and providing a TSS that also includes test cases, which we could use to verify the extracted source code of the TPM 2.0 simulator.

**pyastyle** (created by [Timon Wong](https://github.com/timonwong), NHNCN) and **Artistic Style** (licensed under [GNU Lesser General Public License version 3.0](http://astyle.sourceforge.net/license.html))
