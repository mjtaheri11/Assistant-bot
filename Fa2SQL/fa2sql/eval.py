import utils
import pandas as pd
from tqdm import tqdm
from prompts import SQL_GENERATOR_PROMPT_EVAL, SCHEMA_GL, SCHEMA_INV
from langchain_community.chat_models import ChatOllama

config = utils.get_config()

schemas = {'GL': SCHEMA_GL, 'INV': SCHEMA_INV}

llm_model = config['evaluation']['model_name']
llm = ChatOllama(model= llm_model, temperature=config['ollama']['temperature'], keep_alive=config['ollama']['keep_alive'], timeout=300)


# Read from a CSV file
df = pd.read_csv(config['evaluation']['dataset'], header=0)

results = []
for item in tqdm(df.iterrows()):
    prompt = SQL_GENERATOR_PROMPT_EVAL.format(schema=schemas[item[1].schema],history='', question=item[1].query)
    response = llm.invoke(prompt)
    print(response.content)
    res = [item[1].query, item[1].schema, item[1].sql, response.content]
    results.append(res)

# Write results to a CSV file
result_df = pd.DataFrame(results, columns=['query', 'schema', 'sql', 'model_response'])
result_df.to_csv(config['evaluation']['output_path'] + llm_model + '.csv', index=False)
