# Generalized Reserve Set Covering Problem - with Connectivity and Buffer Constraints
This repository implements the article from Eduardo Álvarez-Miranda, Marcos Goycoolea, Ivana Ljubić, Markus Sinnl: "The Generalized Reserve Set Covering Problem with Connectivity and Buffer Requirements" (European Journal of Operational Research, 2021), available [here](https://www.sciencedirect.com/science/article/abs/pii/S0377221719305818).

Authors: Camilla Bigotto, Anna Guccione

## Abstract 
The design of nature reserves is becoming, more and more, a crucial task for ensuring the conservation of endangered wildlife. In order to guarantee the preservation of species and a general ecological functioning, the designed reserves must typically verify a series of spatial requirements. Among the required characteristics, practitioners and researchers have pointed out two crucial aspects: (i) connectivity, so as to avoid spatial fragmentation, and (ii) the design of buffer zones surrounding (or protecting) so-called core areas. In this paper, we introduce the Generalized Reserve Set Covering Problem with Connectivity and Buffer Requirements. This problem extends the classical Reserve Set Covering Problem and allows to address these two requirements simultaneously. A solution framework based on Integer Linear Programming and branch-and-cut is developed. The framework is enhanced by valid inequalities, a construction and a primal heuristic and local branching. The problem and the framework are presented in a modular way to allow practitioners to select the constraints fitting to their needs and to analyze the effect of e.g., only enforcing connectivity or buffer zones. 

**Topics**: Combinatorial optimization; Maximum weight connected subgraph problem; Wildlife reserve design; Reserve set covering problem; Branch-and-cut
## How to use it
1. Clone the repository:
```bash
git clone https://github.com/panguccio/ReserveDesign.git
cd ReserveDesign
```
2. Create a Python enviroment:
```bash
python3.11 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```
3. Install dependencies:
```bash
python3 -m pip install -r requirements.txt
```
4. Launch python scripts `test.py` and `scalability.py`
