import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.demo import generateOptimizationRecommendation

def runEvals():
    print("[TEST RUN] Running evals on Car-Optimizer...")
    
    try:
        rawOutput = generateOptimizationRecommendation()
        parsedJson = json.loads(rawOutput)
        print("[PASS] API Response successfully deserialized into a valid JSON object")
    except Exception as e:
        print(f"[FAIL] Parsing error: {str(e)}")
        sys.exit(1)
        
    #Enforce strict production contract keys to prevent criteria drift
    expectedKeys = ["alertPriority", "title", "financialExposure", "operationalImpact", "context", "automatedWorkflow"]
    for key in expectedKeys:
        if key in parsedJson:
            print(f"[PASS] Validation successful for key: '{key}'")
        else:
            print(f"[FAIL] Missing required key: '{key}'")
            sys.exit(1)
            
    #Checks structure of automatdWorkflow
    workflow = parsedJson.get("automatedWorkflow", [])
    if isinstance(workflow, list) and len(workflow) > 0:
        print(f"[PASS] Automation list verified. Found {len(workflow)} workflow objects.")
        
        #Check the structure of the first dictionary element in the workflow array
        firstStep = workflow[0]
        stepKeys = ["step", "serviceTrigger", "payloadAction", "userValue"]
        for sKey in stepKeys:
            if sKey in firstStep:
                print(f"  - Verified key: '{sKey}'")
            else:
                print(f"  - [FAIL] Missing key: '{sKey}'")
                sys.exit(1)
    else:
        print("[FAIL] Workflow body is missing or wrong")
        sys.exit(1)

    print("\n[SUCCESS] All is well!")

if __name__ == "__main__":
    runEvals()
