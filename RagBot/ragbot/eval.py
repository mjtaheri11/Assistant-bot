import json
import random
import re
import os 
from statistics import mean

import torch
import numpy as np 
import pandas as pd
from tqdm import tqdm
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from FlagEmbedding import FlagReranker

from prompts import RAG_EVAL_PROMPT
from config import config
from make_sentence_chunks import chunk_document

# "میخوام طبقه حساب تعریف کنم چه مرحله هایی داره؟", "response"

torch.manual_seed(0)
np.random.seed(0)
torch.cuda.manual_seed_all(0)
random.seed(0)

embedding_model_ = HuggingFaceEmbeddings(
                model_name=config["embedding_model"]["model_name"],
                model_kwargs={"device": config["embedding_model"]["device"]})

reranker_model_ = FlagReranker(
                config["reranker"]["model_name"],
                device=config["reranker"]["device"])

# OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://dockerize_assistant-ollama-1:11434')
llm = ChatOllama(
        model=config["ollama"]["model_name"],
        temperature=config["ollama"]["temperature"],
        keep_alive=config["ollama"]["keep_alive"],
        seed=0
        # base_url=OLLAMA_HOST,
    )

def create_retriever():
    collection_path = config["evaluation"]["persist_directory"]
    
    print(f'Creating an evaluation vector DB in {collection_path} ...')
    # document_loader = DirectoryLoader(path=config["evaluation"]['documents_addr'], glob="**/*.txt", loader_cls=TextLoader)
    # documents = document_loader.load()
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=config["retriever"]["chunk_size"],
    #                                                chunk_overlap=config["evaluation"]["chunk_overlap"])
    # chunks = text_splitter.split_documents(documents)
    chunks = chunk_document(config["evaluation"]["documents_addr"], target_chunk_size=config["retriever"]["chunk_size"], max_chunk_size=config["retriever"]["max_chunk_size"])
    print(f'Generated {len(chunks)} chunks')

    vdb = Chroma(persist_directory=collection_path, embedding_function=embedding_model_)
    if len(vdb.get()["ids"]) > 0:
        print(f'VectorDB has {len(vdb.get()["ids"])} documents already, deleting them ...')
        vdb._collection.delete(vdb.get()["ids"])
        
    vdb.add_documents(chunks)
    print(f'{len(chunks)} documents have been added to the vector DB')
    retriever = vdb.as_retriever(search_kwargs={"k": config['evaluation']['retrieved_documents']})
    
    return retriever

retriever = create_retriever()

def retrieve_context(prompt, k=config['evaluation']['retrieved_rank2_documents']):
    docs = retriever.invoke(prompt)
    docs = [doc.page_content for doc in docs]
    scores = reranker_model_.compute_score([[prompt, doc] for doc in docs], normalize=True)
    docs_scores = [(docs[i], scores[i]) for i in range(len(docs))]
    docs_scores_sorted = sorted(docs_scores, key=lambda x: x[1], reverse=True)[:k]

    conf = mean([d[1] for d in docs_scores])

    return '\n\n'.join([d[0] for d in reversed(docs_scores_sorted) ]), conf

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class TwitterUser(BaseModel):
    answer: str = Field(description="Your answer, accompanied by a brief explanation.")
    reasoning: str = Field(description="Explanation for your choice.")

parser = PydanticOutputParser(pydantic_object=TwitterUser)

def output_parser(output):
    output = output.split('reasoning')
    answer = output[0].split(':')[1].strip()
    reason = output[1].split(':')[1].strip()
    return (answer, reason)


def write_to_file(results, accuracy, num_hits, num_processed_data):
    print(f'WRTIE {len(results)} RESULTS TO A CSV FILE')
    headers = ['question', 'A', 'B', 'C','D', 'Answer', 'Model_Answer','Correct?', 'Model_Reason', 'Model_Context', 'Confidence']
    clean_results = []
    for result in results:
        row = [result['question'], result['choices'][0], result['choices'][1], result['choices'][2], result['choices'][3], result['correct_answer'] ]
        try: 
            answer, reason = result['predicted_answer']['answer'], result['predicted_answer']['reasoning']
            # obj = parser.parse(result['predicted_answer'])
            # answer = obj.answer
            # reason = obj.reasoning
        except:
            answer, reason = output_parser(result['predicted_answer'])

        row.append(answer)
        if result['correct_answer'] in answer:
            row.append('1')
        else:
            row.append('0')
        row.append(reason)
        row.append(result['context'])
        row.append(result['context_confidence'])
        clean_results.append(row)

    addr = config['evaluation']['output_path'] + str(accuracy) + "_" + str(num_hits) + "_" + str(num_processed_data) + "_" +  config['evaluation']['dataset'].split('/')[-1].replace(".csv", "") + '_results_' + config['evaluation']['model_name'].replace(":", "-") + "_" + str(config["retriever"]["chunk_size"]) + "_" + str(config["retriever"]["max_chunk_size"]) + "_" + str(config["evaluation"]["retrieved_documents"]) + "_" + str(config["evaluation"]["retrieved_rank2_documents"]) + "_" + str(config["retriever"]["sentence_overlap"]) + ".csv"
    
    pd.DataFrame(clean_results, columns=headers).to_csv(addr, index=False)
    
    print(f'RESULTS WRITTEN TO {addr}')


def main(config=config):
    processed_results = []
    num_hits = 0
    test_dataset = pd.read_csv(config['evaluation']['dataset'], header=None)
    test_dataset.columns = ['source','question', 'a','b','c','d','answer']
    print(f"RUN THE EVALUATION ON {len(test_dataset)} SAMPLES" )
    total_test_data = len(test_dataset)

    for question in tqdm(test_dataset.iterrows(), total=len(test_dataset)):
        query = question[1].question
        prompt_lst = [query]
        result = {
            'question': question[1].question,
            'choices': [question[1].a, question[1].b, question[1].c, question[1].d], 
            'correct_answer': question[1].answer
        }
        
        # prompt_lst.extend(result["choices"])
        # prompt = "\n".join(prompt_lst)
        context, confidence = retrieve_context(prompt=query)
        result['context'] = context
        result['context_confidence'] = confidence
        # import pdb
        # pdb.set_trace()

        prompt = RAG_EVAL_PROMPT.format(context=context, question=query, a=question[1].a, b=question[1].b, c=question[1].c, d=question[1].d)
        # import pdb 
        # pdb.set_trace()
        answer = llm.invoke(prompt)
        try:
            output = answer.content.strip("'").strip()
            output = output.replace("\n", " ").replace("  ", " ")
            output = json.loads(output)
        except:
            total_test_data -= 1
            print('Decoding JSON has failed')
            continue
        
        if question[1].answer == output['answer']:
            num_hits += 1

        result['predicted_answer'] = output
        processed_results.append(result)
        accuracy = num_hits / total_test_data
        print(accuracy)        

    accuracy = num_hits / len(processed_results)
    print(num_hits, accuracy)
    write_to_file(processed_results, accuracy, num_hits, len(processed_results))


def do_eval():
    retrieved_rank2_documents = [5, 10, 15]
    retrieved_documents = [5, 10, 15]
    chunk_sizes = [400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500]
    max_chunk_sizes = [500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600]
    sentence_overlaps = [1, 2, 3, 4]
    
    for t, retrieved_document in enumerate(retrieved_rank2_documents):
        for i, chunk_size in enumerate(chunk_sizes):
            for sentence_overlap in sentence_overlaps:
                for j in range(4):
                    for k in range(3):
                        if k + t < len(retrieved_documents):
                            if i + j < len(chunk_sizes):
                                config["retriever"]["sentence_overlap"] = sentence_overlap
                                config["retriever"]["chunk_size"] = chunk_size
                                config["retriever"]["max_chunk_size"] = max_chunk_sizes[i + j]
                                config["evaluation"]["retrieved_documents"] = retrieved_document
                                config["evaluation"]["retrieved_rank2_documents"] = retrieved_rank2_documents[k + t]
                                main(config)
                
if __name__ == "__main__":
    main()
    # do_eval()    



# def retrieve_context(k=config['evaluation']['retrieved_rank2_documents'], **kwargs):
#     assert "prompt" in kwargs.keys(), "the prompt doesn't involved in the kwargs"
#     queries = [kwargs["prompt"]]
#     # if "choices" in kwargs.keys(): 
#     #     all_queries = queries.extend(kwargs["choices"])
#     queries.extend(kwargs["choices"]) if "choices" in kwargs.keys() else None
#     all_documents = []
#     for prompt in queries: 
#         if re.match(pattern, prompt):
#             continue
#         docs = retriever.invoke(prompt)
#         all_documents.extend([doc.page_content for doc in docs])

#     all_documents = list(set(all_documents))
#     scores = reranker_model_.compute_score([[kwargs["prompt"], doc] for doc in all_documents], normalize=True)
#     docs_scores = [(all_documents[i], scores[i]) for i in range(len(all_documents))]
#     docs_scores_sorted = sorted(docs_scores, key=lambda x: x[1], reverse=False)[:k]

#     conf = mean([d[1] for d in docs_scores])

#     return '\n\n'.join([d[0] for d in docs_scores_sorted ]), conf
