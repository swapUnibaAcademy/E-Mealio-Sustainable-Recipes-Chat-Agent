# 🌱E-Mealio: A Chat Agent for Sustainable and Healthy Recipes Suggestions

A project originally developed by **Antonio Raffaele Iacovazzi** as part of his *Master’s Thesis in Computer Science*, with the goal of developing a chat-based agent that helps users adopt sustainable food habits.

Subsequently, **Lorenzo Blanco**, as part of his *Bachelor's Thesis in Computer Science*, further developed the chat-based agent by enhancing its functionalities, improving usability and overall user experience, and expanding its domain beyond sustainability to also address the promotion of healthy food habits.

---

## 🔌 Current Status

**❌ Bot Status: OFFLINE**  
The Telegram bot is currently **active and operational**. You can interact with it searching **@emealio_bot** on Telegam and typing the `/start` command.

---

## How to Install

> Instructions below are intended for running the project locally.  
> **Python 3** is required.

### 1. Clone the Repository

Download or clone this repository into a local folder.

---

### 2. Install the Dataset

#### a. Install MongoDB

- **MongoDB Community Edition**  
  [Installation Guide](https://www.mongodb.com/docs/manual/installation/)

- **MongoDB Compass** (a handy frontend GUI)  
  [Compass Download](https://www.mongodb.com/it-it/products/tools/compass)

#### b. Import the Dataset

1. Extract `emealio_food_db.zip` to a location of your choice.
2. Open **MongoDB Compass**.
3. Create a new database and name it:  
   ➤ `emealio_food_db`
4. Create a collection inside it called:  
   ➤ `ingredients`
5. Import data:
   - Click on the collection, then use the **"Add Data"** > **"Import JSON"** function to import `emealio_food_db.ingredients.json`.
6. Repeat the process for the remaining `.json` files:
   - For example, `emealio_food_db.recipes.json` should be imported into a collection named `recipes`.
   - **Make sure each collection is named exactly like the corresponding file (without the `.json` extension).**

---

### 3. Compute Embeddings

> The dataset does not include embeddings due to their size (~3GB).  
> Follow these steps to generate them locally.

#### a. Required Libraries

Make sure the following Python libraries are installed:

```bash
pip install pandas numpy pymongo sentence_transformers
```

#### b. Generate Embeddings

Run the script:

```bash
python datasetUtilities/compute_embeddings.py
```

- This process takes around **1.5 hours**.
- Progress is shown every 100 items with a message like:  
  `Done N`

---

### 4. Install and Run the Agent

The core agent code is located in the `projectRoot` folder.

#### a. Install Dependencies

Use `pip` to install required libraries:

```bash
pip install -r requirements.txt
```

#### b. Set Up the Telegram Bot

1. Create a new bot using **[BotFather](https://core.telegram.org/bots/features#creating-a-new-bot)** on Telegram.  
   (Or contact me at **ar.iacovazzi@gmail.com** to gain access to the existing bot.)

2. Create a `.env` file in the `projectRoot` folder with the following contents:

```env
OPENAI_API_KEY=
TELEGRAM_BOT_TOKEN=
ANTHROPIC_API_KEY=
```

- Add your corresponding API keys.  
- You can provide just one (OpenAI or Anthropic), or none if you plan to configure a different LLM via LangChain.

#### c. Run the Bot

Launch the agent:

```bash
python TelegramBot.py
```

- Send `/start` to the bot on Telegram.
- If it replies, everything is working! 🎉

---

### 5. Run Unit Tests

You can verify everything is set up correctly by running:

```bash
python test.py
```

- Tests are validated with:
  - **OpenAI GPT-4o**
  - **Anthropic Claude Sonnet 3.5**
- If all tests pass, the bot is ready to go.
- If you use a different LLM, ensure it passes all tests—otherwise, the agent may not work properly.

---

## 🐳 Run with Docker (Recommended)

Alternatively, you can run E-Mealio fully containerized with Docker and Docker Compose — no manual setup required.

### ✅ Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/)

### 📁 Project Structure (Relevant Files)

```
E-Mealio/
├── docker-compose.yml
├── Dockerfile
├── mongo_dump/                  # Precomputed MongoDB dump (BSON format), WARNING: the actual files are not in the folder, check the readme inside to understand how to download them. 
├── .env                         # Contains API keys
└── projectRoot/                 # Main bot code
```

---

### 🔑 1. Set Environment Variables

Create a `.env` file in the root (same directory as `docker-compose.yml`) with:

```env
OPENAI_API_KEY=your_openai_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ANTHROPIC_API_KEY=your_anthropic_key
```

> You can leave some variables blank if you're not using a specific provider.

---

### 📥 2. Download the MongoDB Dump

Download the precomputed MongoDB dump from the following link:

**🔗 [Download emealio_food_db.zip](https://www.dropbox.com/scl/fi/lvygo3co749v278adexvf/emealio_food_db.zip?rlkey=96ciy1dirffwah8n3i1sw1wxf&dl=0)**

Then:

1. Unzip the file.
2. Place the contents inside the `/mongo_dump` directory.

---

### 🚀 3. Build and Launch the Containers

From the root of the project, run:

```bash
docker-compose up --build
```

This will:

- Start a MongoDB container
- Automatically restore the precomputed database from `/mongo_dump`
- Launch the Telegram bot

---

### 🧪 4. Verify It’s Working

- Open your Telegram bot and send `/start`
- You should receive a response from the bot within a few seconds 🎉

---

### 💾 MongoDB Persistence

MongoDB data is stored in a Docker-managed volume named `mongo_data`.

To **completely reset** the environment (including clearing the database), run:

```bash
docker-compose down -v
```
