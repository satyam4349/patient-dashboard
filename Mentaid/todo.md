# TODO: Dependency files and consolidation plan

## Created files (paths)
- Backend/Prototype/optimized_way/optimized_requie.txt
- Backend/Prototype/optimized_way/description.txt
- Backend/Prototype/optimized_requie.txt
- Backend/Prototype/description.txt
- Backend/optimized_requie.txt
- Backend/description.txt
- Frontend/optimized_requie.txt
- Frontend/description.txt

## Action: Create single consolidated requirements.txt (global)
- Analyze all the above folder-wise pins and produce one pinned, conflict-free global requirements.txt for the whole project.
- Target location: Backend/requirements.txt (single source for installs), per preference to use one file.
- After creating it, delete existing per-folder venvs and create one global venv using this file only.

## Notes and risk management
- Potential conflicts to handle explicitly:
  - numpy ABI/version pinning to avoid numpy.core issues
  - websockets versions (Gradio/Starlette/Uvicorn compatibility)
  - shap and lime heavy deps and their transitive constraints
  - scikit-learn + joblib compatibility with saved SVM pickle
  - torch/transformers/sentence-transformers CPU-only pinning
  - spaCy model data (optional) must match spaCy minor version
- Multiple Python versions exist locally → enforce a dedicated venv pinned to one Python version (global is 3.11 and more i have 3.10 and 3.13 too) to avoid cross-version conflicts.
- Ensure compatibility with artifacts created on Google Colab (SVM pickle, MentalBERT). Pin sklearn/numpy to compatible ranges or re-export if needed.

## Implementation steps
1) Aggregate imports and current pins from all created optimized_requie.txt files.
2) Select Python appropriate version to make the venv in gloabbly in this project directory and pin critical stacks:
   - FastAPI/Pydantic v2
   - Transformers/Torch CPU
   - Sentence-Transformers
   - Gradio
   - sklearn/joblib/numpy/scipy compatible trio
3) Test install in a fresh venv; run Backend and Frontend; validate model loading and main flows.
4) Document any special install steps (spaCy model downloads, NLTK data) in README.
5)also make sure to read the prd.md to include any more varibales in thinking if there might be any issues 
6)also after going through all of the things above make sure to make a section below of best practices,caution while buidling while i wanna build and exact detailed feature by feature efficient roadmap to get to the mvp and even the future versions...i ma thinking i am gonna use google adk for companion agent and assistent agent system.so include the documentations necessary for eevrything too in prd.md or here whichever will be more efficient.
7)make a new planner.md file to include everything roadmap feature by feature efficient to be implemented and also update the prd.md file to include to setup the agent assistent and the companion to properly talk with the patient and the clinicians and all and instruction son how i will do it .
8)or tell me if the hf capstnone project structure would be more accurate for the agents i need where i need them to automously ask the patient and also automnously properly work with the clinician and the patient as well so that they can communicate with each other without any human intervention at all .
