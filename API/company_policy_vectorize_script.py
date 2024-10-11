# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings.openai import OpenAIEmbeddings
# import os

# os.environ['OPENAI_API_KEY'] = ''

# loader = PyPDFLoader("/home/khudi/Desktop/Farm_Ecommernce_Agent/API/Farm Rio Company Policy.pdf")
# pages = loader.load_and_split()



# faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings())
# faiss_index.save_local('./faiss_index')
# docs = faiss_index.similarity_search("what is the reutrn policy?", k=2)
# print(docs)
# # for doc in docs:
# #     print(str(doc.metadata["page"]) + ":", doc.page_content[:300])