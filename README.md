# TPM 2.0 Simulator Extraction Script

The purpose of this script is to extract the source code from the publicly available PDF versions 01.16 and 01.38 of the *Trusted Platform Module Library Specification* published by the Trusted Computing Group (TCG).

The result of the extraction scripts is a complete set of the source files for a __Trusted Platform Module (TPM) 2.0 Simulator__, which runs under Windows, Linux, as well as Genode (by applying the appropriate patches).

*Note:* The extraction script also works with a Microsoft Word-based FODT-version of the more recent specifications (e.g., version 01.19), which are however only available to TCG members.

*License:* The files of this project are licensed under **BSD 2-Clause License** (except where indicated otherwise).

---

## User Instructions


### Extraction

#### Requirements
Make sure the following packages are installed on your system:
```
patch
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
1. Open a terminal and navigate to the project folder `tpm2simulator`
2. Edit configuration settings in the file `tpm2simulator/scripts/settings.py` (e.g., `MANUFACTURER`, `VENDOR_STRING_1`, and `FIRMWARE_V1`) and change `SET = False` to `SET = True` when finished
3. Create a folder named `build` and run the following command inside:
    ```
    cmake -G "Unix Makefiles" ../cmake -DCMAKE_BUILD_TYPE=Debug -DSPEC_VERSION=116
    ```
    or
    ```
    cmake -G "Unix Makefiles" ../cmake -DCMAKE_BUILD_TYPE=Debug -DSPEC_VERSION=138
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
(If there are any error messages at startup, restart the simulator)


### Testing
In order to test if the simulator is working correctly, we use [IBM's TPM 2.0 TSS](https://sourceforge.net/projects/ibmtpm20tss)

1. Open a terminal and start the TPM simulator

2. Open another terminal and navigate to the project folder `ibmtpm20tss/utils`

3. Build the TSS:
```
make
```
4. Run the tests:
```
./reg.sh -a
```

### Compatibility
The following table shows which version of the TPM Simulator works with which version of the IBM's TPM 2.0 TSS.

| Specification version | Used document type | TSS version | Results                                                                                                           |
| --------------------- | ------------------ | ----------- | ----------------------------------------------------------------------------------------------------------------- |
| 116                   | PDF                | 755         | Working <sup id="a1">[1](#f1)</sup><sup>,</sup><sup id="a2">[2](#f2)</sup>                                        |  
| 116                   | PDF                | 996         | Working <sup id="a1">[1](#f1)</sup><sup>,</sup><sup id="a2">[2](#f2)</sup><sup>,</sup><sup id="a3">[3](#f3)</sup> |
| 116                   | FODT               | 755         | Working <sup id="a1">[1](#f1)</sup><sup>,</sup><sup id="a2">[2](#f2)</sup>                                        |
| 116                   | FODT               | 996         | Working <sup id="a1">[1](#f1)</sup><sup>,</sup><sup id="a2">[2](#f2)</sup><sup>,</sup><sup id="a3">[3](#f3)</sup> |
| 119                   | FODT               | 755         | Working <sup id="a1">[1](#f1)</sup>                                                                               |
| 119                   | FODT               | 996         | Working <sup id="a1">[1](#f1)</sup><sup>,</sup><sup id="a3">[3](#f3)</sup>                                        |
| 124                   | FODT               | 755         | Working                                                                                                           |
| 124                   | FODT               | 996         | Working <sup id="a1">[1](#f1)</sup><sup>,</sup><sup id="a3">[3](#f3)</sup>                                        |
| 138                   | PDF                | 755         | Working <sup id="a4">[4](#f4)</sup>                                                                               |
| 138                   | PDF                | 996         | Working <sup id="a4">[4](#f4)</sup>                                                                               |
| 138                   | FODT               | 755         | Working <sup id="a4">[4](#f4)</sup>                                                                               |
| 138                   | FODT               | 996         | Working <sup id="a4">[4](#f4)</sup>                                                                               |

<b id="f1">1</b>: The option `-116` has to be added to line 88 in /utils/regtests/testaes.sh.

<b id="f2">2</b>: The policy tests (`-18` for version 755 of the TSS, `-21` for version 996 of the TSS) cannot be executed separately. They only work if they are executed with the other tests using the option `-a` (all) in the TSS.

<b id="f3">3</b>: The lines 66-68 in /utils/regtests/initkeys.sh have to be removed. Only the tests which are not for version 138 of the TPM specification can be executed (which tests are affected can be retrieved by calling the TSS with the help argument `-h`). The tests have to be executed separately by using the option `-n$TESTNUMBER` with the TSS.

<b id="f4">4</b>: The TSS fails when running it the first time, but not in any subsequent run. The clock test fails.

---

### Credits

This project was created by **[Steffen Wagner](https://github.com/stwagnr)** ([Fraunhofer AISEC](https://www.aisec.fraunhofer.de)).

Special thanks to **[Sergej Proskurin](https://github.com/prosig)**, **[Tamás Bakos](https://github.com/tamasbakos)**, and Christoph Kowatsch for their support in implementing the script.

**IBM's TPM 2.0 TSS** was created by [Ken Goldman](http://sourceforge.net/u/kagoldman) and is licensed under the Berkeley Software Distribution (BSD) License. We'd like to thank Ken for implementing and providing a TSS that also includes test cases, which we could use to verify the extracted source code of the TPM 2.0 simulator.

**pyastyle** (created by [Timon Wong](https://github.com/timonwong), NHNCN) and **Artistic Style** (licensed under [GNU Lesser General Public License version 3.0](http://astyle.sourceforge.net/license.html))

