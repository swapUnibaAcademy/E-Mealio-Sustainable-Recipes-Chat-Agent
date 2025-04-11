# 🌱E-Mealio: A Chat Agent for Sustainable Recipes Suggestions

A project by **Antonio Raffaele Iacovazzi** for the *Master’s Thesis in Computer Science*  
**Goal**: Develop a chat-based agent that helps users adopt sustainable food habits.

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
