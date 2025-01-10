# Comprehensive Diabetes Model

This microsimulation project aims to study the effects of various interventions on diabetes prevalence.

**PI:** Tom Hoerger, RTI
**Code:** Rainer Hilscher, RTI

## Requirements
- Python 3.9+ (3.9 - 3.12 have been successfully tested)
- See requirements.txt for Python packages that need to be installed
- The analysis script in particular makes use of Pandas

## Usage
- Use `python run-model.py [scenario name]` to execute the model
- Scenario files need to be placed in the ./scenarios folder
- Custom built scenario files need to contain the exact same variables as the ones listed in the same scenario files

### to run the 't1d-final-glyco_basic.json' scenario
- Example: python run-model.py t1d-final-glyco_basic

### to only run a specific stage
- Example: python run-model.py t1d-final-glyco_basic --stages=analysis
- Possible stages: {population, simulation, analysis}

