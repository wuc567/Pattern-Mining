# OPST_MS

This project implements **Order-Preserving Suffix Trees (OPST)** and their applications in **pattern mining** and **matching statistics**.  
It provides algorithms for constructing OPST, mining maximal and closed patterns, and OPMS with and without suffix links.

---

## Directory Structure

.  
├── OPST_construction.cpp         # OPST construction  
├── OPST_MP.cpp                   # OPST + maximal pattern mining  
├── OPST_CP.cpp                   # OPST + closed pattern mining  
├── OPST_MS_SuffixLink.cpp        # OPST + matching statistics (with suffix links)  
├── OPST_MS_Root.cpp              # OPST + matching statistics (without suffix links)  
├── BA_MP.cpp                     # Baseline for maximal pattern mining  
├── BA_CP.cpp                     # Baseline for closed pattern mining  
├── node.cpp / node.h             # Node structure  
├── OPST.cpp / OPST.h             # Core OPST implementation  
├── OPST_MS.cpp / OPST_MS.h       # OPST + matching statistics  
├── baseline.cpp / baseline.h     # Baseline implementations  
├── oracle.cpp / oracle.h         # Oracle data structure  
├── DerivedWTInt.cpp / .h         # Wavelet tree based integer support  
├── utils.cpp / utils.hpp         # Utility functions  
├── malloc.h                      # Memory statistics (uses mallinfo/mallinfo2)  
├── inputW.txt                    # Example input text W  
├── inputP.txt                    # Example input text P  
├── Makefile                      # Build configuration  
├── pre-install.sh                # Installation script for dependencies  
├── sdslite.zip                   # SDSL library (compressed)  
├── README.md                     # (this file) 

## Dependencies

- **C++17** or later  
- [**SDSL-lite**](https://github.com/simongog/sdsl-lite) (Succinct Data Structure Library)  
- **divsufsort / divsufsort64** (suffix array construction libraries)  

Install dependencies with:

```bash
./pre-install.sh
```

## Build

Build all executables:
```bash
make all
```
This produces the following binaries:

- OPSTConstruction     # build OPST
- OPSTMaximal          # OPST with maximal pattern mining
- OPSTClosed           # OPST with closed pattern mining
- BAMP                 # baseline for maximal pattern mining
- BACP                 # baseline for closed pattern mining
- OPST_MS_SuffixLink   # OPST with matching statistics (suffix links)
- OPST_MS_Root         # OPST with matching statistics (no suffix links)

## Clean build files:
```bash
make clean
```
## Usage

###  Index Construction
```bash
./OPSTConstruction -f inputW.txt
```
###  Mining Maximal OP Patterns
```bash
./OPSTMaximal -f inputW.txt -t 2
./BAMP -f inputW.txt -t 2
```

###  Mining Closed OP Patterns

```bash
./OPSTClosed -f inputW.txt -t 2
./BACP -f inputW.txt -t 2
```
### OPMS
```bash
./OPST_MS_SuffixLink -w inputW.txt -p inputP.txt
./OPST_MS_Root -w inputW.txt -p inputP.txt
```

### Options
```text
-f    path to the input file
-t    minimal support (tau > 1)
-w    input text W for matching statistics
-p    input text P for matching statistics
```



## Datasets
The preprocessed and clustering datasets are available at [Google Drive](https://drive.google.com/file/d/1LFMfavFYjdF_qamQTp5ONKPfirUpMH5P/view?usp=sharing).


This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
