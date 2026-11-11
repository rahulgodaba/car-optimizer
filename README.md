# Car-Optimizer: 
Imagine a driver waking up on a freezing winter morning, walking out to their car, and turning the key only to hear a clicking sound because their battery died overnight. According to AAA, this frustrating experience is one that impacts 7 million drivers on a yearly basis. This tool is built to solve that exact problem before it happens.

Instead of waiting for a car to break down, our tool acts like an early warning system on the driver's phone. On a morning where temperatures drop by 15 degrees, the tool immediately flags that the driver's car is at risk. 

By looking at their gas consumption data and realizing they have a low MPG pattern, the tool realizes that the driver is often on brief 10 minute drives which never allow the engine to fully warm up. Because these quick drives constantly starve the vehicle's alternator of the runtime it needs to recharge, the battery is left dangerously depleted. The application flags this, explains the exact risk to the driver in plain English, and delivers the beginning stages of an automated workflow, by reserving a replacement battery nearby or mapping out a 'conditioning' drive to resolve the issue seamlessly before their battery ever dies.

## 1. Why car-optimizer?
This project draws direct inspiration from Arun Rajagopalan's article, "[Motorq's Next Era: From Dashboards to Decisions](https://www.motorq.com/blog/motorqs-next-era)". and Vivek Malipatil's 5 year vision of the product he shared in [this video](https://www.youtube.com/watch?v=OBy2yVySeU4). 

Arun emphasized the need to "act on data immediately". His anecdotes from customer feedback made it clear that Motorq will now be focused on "turning vehicle data into clear recommendations" and automating workflows. Vivek's vision, "for any business, or even any individual person in the world, to be able to seamlessly request and receive automated insights from their connected vehicle", got me thinking about several interesting use cases which could solve problems at scales for vehicle drivers all over the world. The prototype I've built here serves as an initial attempt to prove how a highly accessible, simplified use case can fulfill Arun & Vivek's vision. 

Coincidentally, I had 4 years of manual data I logged back in high school when I was learning the ropes of data analysis! I had collected data every time we filled up our 2009 Toyota Corolla and attempted to build a personal analytics & receipt reader app. I used that data set to help with this project!

## 2. System Architecture and scaling in Production
This prototype has three independent tiers:
1. Deterministic pipeline: A Pandas worker processes the continuous CSV data rows to compute exact MPG averages and trip milestones. This isolates all calculations away from the LLM, eliminating statistical hallucinations.
2. Vector store document index (RAG): Manufacturer data guides from official documentation are stored with metadata filters. The agent uses the metadata filters tonarrow down the text the model has to digest.
3. Orchestrator: The Anthropic SDK converts calculated data and retrieved text files into a JSON object.

While this prototype uses static files to prove the business logic, an agent like this, in production, running across thousands of cars requires a regular data feed to streaming and the use of cloud-based databases.

Here is how this local prototype would scale:
1. The Telemetry stream: Instead of a static `fuelData.csv` file, the application will rely on APIs connected OEMs. This data could be housed in a cloud platform like Snowflake.
2. The Cloud database: The `vectorDb.json` text file moves into an enterprise database that's best suited for unstructured data.
3. Existing OEM API integrations: Instead of a script like `demo.py`, the application is set to monitor the incoming OEM API data. The moment a car’s efficiency drops below a set threshold, the application instantly triggers a metadata search to pull the right manufacturer warning steps.

## 3. User Experience mockup

<img width="2880" height="2480" alt="winter-freeze-alert" src="https://github.com/user-attachments/assets/b837b462-d73e-4d21-af70-97d5fcd4fec1" />

## 4. Evals
I added 2 evals which test:
1. The schema output to ensure that the tool always outputs the exact keys the frontend interface will expect 
2. The trigger of the automated workflows

If this tool were to be shipped to production, additional evaluations would be needed to:
1. Ensure the metadata was successfully retrieving the expected text blocks for the appropriate vehicle
2. Validate the LLM did not hallucinate when providing specific repair partnames
3. A regression gate with 1000s of historical logs which are run to keep the alerting logic bug-free.
4. 
## 5. Setup
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
