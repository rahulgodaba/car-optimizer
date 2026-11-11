# Car-Optimizer: 
A simple tool that takes vehicle gas logs, cross references them with text from Toyota manuals, and returns a JSON array which can be used to automate maintenance alerts. 

When a driver of a high mileage Corolla starts their car after an overnight 15 degrees F temperature drop, the tool flags the vehicle's vulnerability based on historical data. By analyzing low MPG logs, the engine identifies a commute pattern where the engine never fully warms up and the alternator is starved of charging runtime. It instantly alerts the driver that the battery faces terminal failure, providing automated action steps to protect the car before it breaks down.

## 1. Executive Vision and Connected Vehicle Intelligence

This project draws direct inspiration from Motorq CEO Arun Rajagopalan's article, "Motorq's Next Era: From Dashboards to Decisions". When I read that Motorq was trying to move past raw data dashboards to deliver actionable recommendations and workflow automation, it reminded me of how I first learned data analysis by tracking fuel consumption and experimenting with OCR apps for our family's Toyota Corolla back in high school. 
I was also inspired by Motorq Co-founder and CPO Vivek Malipatil's vision. He noted that his vision for the company in 5 years is "for any business, or even any individual person in the world, to be able to seamlessly request and receive automated insights from their connected vehicle". This tool serves as an initial attempt to prove how a highly accessible, simplified use case can fulfill that vision. 

## 3. System Architecture and scaling in Production

This prototype has three independent tiers:
1. Deterministic pipeline: A Pandas worker processes the continuous CSV data rows to compute exact MPG averages and trip milestones. This isolates all calculations away from the LLM, eliminating statistical hallucinations.
2. Vector store document index (RAG): Manufacturer data guides from official documentation are stored with metadata filters. The agent uses the metadata filters tonarrow down the text the model has to digest.
3. Orchestrator: The Anthropic SDK converts calculated data and retrieved text files into a JSON object.

While this prototype uses static files to prove the business logic, an agent like this, in Production, running across thousands of cars requires a regular data feed to streaming and the use of cloud-based databases.

Here is how this local prototype would scale:
1. The Telemetry Stream: Instead of a static `fuelData.csv` file, the application will rely on APIs connected OEMs. This data could be housed in a cloud platform like Snowflake.
2. The Cloud Database: The `vectorDb.json` text file moves into an enterprise database that's best suited for unstrucutred data.
3. The Live Retrieval Pipeline: Instead of a script like `demo.py`, the application is set to monitor the incoming OEM API data. The moment a car’s efficiency drops below a set threshold, the application instantly triggers a metadata search to pull the right manufacturer warning steps.

## 4. User Experience mockup

The final notification to the user consists of the following data:

+-------------------------------------------------------------------+
| WINTER FREEZE: RISK DETECTED                                      |
+-------------------------------------------------------------------+

| TITLE:                                                            |
| Your daily commute puts you at risk of a dead                     |
| battery on Monday morning. Act before the temps drop tonight!     |
|                                                                   |
| FINANCIAL EXPOSURE:                                               |
| $150.00 - $300.00 (Emergency towing fee + replacement battery)    |
|                                                                   |
| OPERATIONAL IMPACT:                                               |
| lost peace of mind and unexpected out-of-pocket expenses.         |

+-------------------------------------------------------------------+

| [] SELECT TO APPROVE: IN-VEHICLE BATTERY CONDITIONING             |
|     Flips on your car's  navigation system to route               |
|     a pre-configured 20 minute highway section on your drive      |
|     home today, allowing the alternator to fully top off your     |
|     charge.                                                       |
|                                                                   |
| [✓] SCHEDULED: AUTOMATED PARTS STORE PICKUP                       |
|     Because your battery is  past its 3 year                      |
|     lifespan, a replacement battery has been reserved at the      |
|     local Costco hub on your commute path.                        |
+-------------------------------------------------------------------+

## 5. Evals
I added 2 eval which test:
    1. The schema output to ensure that the tool always outputs the exact keys the frontend interface will expect 
    2. The trigger of the automated workflows

## 6. Setup
Execute these terminal commands from your root directory to install the necessary components, run the orchestration core, and execute the eval suite:

```bash
# 1
git clone https://github.com/rahulgodaba/car-optimizer/
cd car-optimizer

# 2
pip install pandas anthropic

# 3
export ANTHROPIC_API_KEY="your_api_key_here"

# 4
python src/demo.py

# 5
python tests/evals.py
```
