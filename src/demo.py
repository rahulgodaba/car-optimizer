import os
import json
import pandas as pd
import anthropic

#Step 1: Deterministic Processing Layer which processes the continuous, multi year telemetry data rows using pandas
#Isolates the trailing rows to identify 'high-wear' commuter signals
def analyzeTelemetry():
    df = pd.read_csv("data/fuelData.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Calculate the rolling mileage changes over consecutive trips to gas station
    df['mileageDelta'] = df['odometerReading'].diff()
    
    latestOdo = int(df['odometerReading'].max())
    
    # Isolate trailing rows to capture the current commute 
    trailingRecords = df.tail(3)
    avgMpg = trailingRecords['mileage'].mean()
    avgDeltaDays = trailingRecords['deltaDays'].mean()
    avgBlockMiles = trailingRecords['mileageDelta'].dropna().mean()
    
    # Trigger condition for a short 3.5-mile commute
    isCommuter = True if (avgMpg < 18) else False
    
    return {
        "targetOem": "Toyota",
        "latestOdometer": latestOdo,
        "calculatedAvgBlockMiles": round(avgBlockMiles, 1) if not pd.isna(avgBlockMiles) else 148.0,
        "runningEfficiencyMpg": round(avgMpg, 1),
        "commuterProfileDetected": isCommuter
    }

#Step 2: Pre-filtering the metadata which simulates a hybrid vector database lookup
def queryKnowledgeStore(oemFilter, componentFilter):
    with open("data/knowledgeStore.json", "r") as f:
        database = json.load(f)
        
    matchedChunks = []
    for chunk in database:
        meta = chunk["metadata"]
        if meta["oem"] == oemFilter and meta["component"] == componentFilter:
            matchedChunks.append(chunk["content"])
            
    return " ".join(matchedChunks)

#Step 3: Orchestration via Anthropic SDK, takes telemetry data, retrieved RAG text chunks, and weather data
def generateOptimizationRecommendation():
    stats = analyzeTelemetry()
    
    if stats["commuterProfileDetected"]:
        oilRules = queryKnowledgeStore(stats["targetOem"], "oilMonitor")
        retrievedContext = f"{oilRules}"
    else:
        retrievedContext = "Metrics indicate standard baseline operation."

    liveWeatherFeed = "Alert: Extended freeze settling overnight in Philadelphia. Lows dropping to 15°F."

    apiKeyToken = os.environ.get("ANTHROPIC_API_KEY")

    if not apiKeyToken:
        raise ValueError("Missing ANTHROPIC_API_KEY environment variable. Run 'export ANTHROPIC_API_KEY=...' first.")

    client = anthropic.Anthropic(api_key=apiKeyToken)

    systemPrompt = """
    You are the automated orchestration core of the Car Optimizer Platform. You translate the raw  telemetry data and unstructured manufacturer rules into machine readable, event-driven automation payloads.
    
    OUTPUT FORMAT REQUIREMENTS:
    - Return a raw, valid JSON object using camelCase keys. Do not wrap the response in markdown code blocks (no ```json).
    - Ensure all string text fields use clean, universal ASCII characters. Instead of unicode symbols like degrees symbols, write out 'degrees F' or 'Fahrenheit' explicitly to prevent string rendering bugs.
    
    REQUIRED JSON STRUCTURAL SCHEMA:
    Output exactly these keys at the root level using camelCase:
    - "alertPriority": (String: HIGH, MEDIUM, LOW)
    - "title": (Consequence driven risk summary specifying the immediate downside if ignored)
    - "financialExposure": (Quantified loss in dollars if ignored)
    - "operationalImpact": (Text outlining the immediate consequence to the driver's daily routine)
    - "context": (Text detailing how short cold cycles cause moisture pooling and limit alternator recovery in a way that is understandable to a layman)
    - "automatedWorkflow": (A list of dictionaries. Each dictionary must contain exactly:
        "step": (Integer),
        "serviceTrigger": (String: ex., IN_VEHICLE_NAV, MOBILE_PUSH, CALENDAR_API, SERVICE_SCHEDULER),
        "payloadAction": (String detailing the programmatic trigger command),
        "userValue": (Text explaining the value add to the driver and how this reduces friction)
      )
    """

    userInput = f"""
    Process current profile metrics to output a prioritized 'Action' Card:
    - Telemetry Profile: {json.dumps(stats)}
    - Unstructured Factory Context Chunks: {retrievedContext}
    - Live Weather Stream: {liveWeatherFeed}
    """

    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=4000,
        system=systemPrompt,
        messages=[{"role": "user", "content": userInput}]
    )
    
    #added this to account for parsing the final text output and separate from thinking block
    for block in response.content:
        # Check standard string property mappings
        if hasattr(block, 'text') and block.text:
            return block.text
            
        try:
            blockData = block.model_dump() if hasattr(block, 'model_dump') else dict(block)
            if blockData.get('type') == 'text':
                return blockData.get('text')
        except Exception:
            pass
            
    raise ValueError(f"Could not extract raw text string payload. Found blocks: {str(response.content)}")

if __name__ == "__main__":
    print(json.dumps(json.loads(generateOptimizationRecommendation()), indent=4))