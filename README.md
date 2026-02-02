# Dual-Agent Knowledge Graph Reasoning

## Overview
This project implements a **Dual-Agent Architecture** designed to solve the problem of **Incomplete Knowledge Graph Question Answering (IKGOA)**. While standard LLMs often struggle with pathfinding in incomplete graphs, this system uses a specialized **Planner** and **Executor** to navigate data and dynamically fill knowledge gaps.



## Key Features
* **Dual-Agent System**: Separates high-level reasoning (Planner) from low-level database interaction (Executor).
* **Dynamic Knowledge Integration (DKI)**: The system can "hypothesize" missing triples when a search path is blocked, allowing the reasoning process to continue even when the KG is incomplete.
* **Neo4j & Gemini Integration**: Built using **Gemini 2.5 Flash** for reasoning and **Neo4j AuraDB** for structured data storage.
* **Robust Multi-hop Search**: Capable of traversing complex paths to answer questions that require connecting multiple disparate facts.

## Technology Stack
* **Core LLM**: Gemini 2.5 Flash.
* **Database**: Neo4j AuraDB.
* **Framework**: LangChain for tool-binding and agent management.
* **Navigation**: Custom Cypher queries for one-hop traversal.

## Project Structure
* \`agent_core.py\`: Contains the main manual loop for the Dual-Agent system and tool-calling logic.
* \`search_tool.py\`: The interface for Neo4j, handling connection pooling and graph queries.
* \`.env\`: Configuration file for API keys and database credentials.

## Setup and Installation

### 1. Prerequisites
* Python 3.9+
* A Neo4j AuraDB instance (with the Movie Graph dataset loaded).
* Google Gemini API Key.

### 2. Loading the Dataset (Neo4j AuraDB)
The project is designed to run on the standard "Movie Graph" dataset. To load it into your AuraDB instance:
1. Log in to your **Neo4j Browser**.
2. In the command line at the top, type `:play movie-graph` and press Enter.
3. Follow the instructions in the guide that appears: click the "Create" code block to run the Cypher script that populates the database with actors, movies, and relationships.

### 3. Install Dependencies
```bash
pip install langchain-google-genai neo4j python-dotenv
```

### 4. Environment Configuration
Ensure your `.env` file is set up with the following:
```env
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
GEMINI_API_KEY=your_gemini_api_key
```

## How to Run
Once the database is loaded and your environment is configured, you can run the agent as follows:

1. **Verify Connection**: (Optional) Run the search tool standalone to ensure your credentials are correct and the database is reachable:
   ```bash
   python search_tool.py
   ```
2. **Execute Reasoning Agent**: Run the main agent loop to process the multi-hop query:
   ```bash
   python agent_core.py
   ```

## Experimental Performance
Our experiments on **Complex WebQuestions (CWQ)** and **WebQuestionsSP (WebQSP)** show that this Dual-Agent approach maintains high accuracy (Hits@1) even when the graph is 30% incomplete.

| Method | 0% Missing | 10% Missing | 20% Missing | 30% Missing |
| :--- | :--- | :--- | :--- | :--- |
| RAG | 64.9 | 57.7 | 50.5 | 44.3 |
| **Ours** | **69.2** | **64.7** | **60.3** | **56.1** |
*(Results for WebQSP benchmark)*

---
**Contact**:

Arsen Boyajyan | [arsen_04@sjtu.edu.cn](mailto:arsen_04@sjtu.edu.cn)  
Gu Jingyu | [gujyu123@sjtu.edu.cn](mailto:gujyu123@sjtu.edu.cn)