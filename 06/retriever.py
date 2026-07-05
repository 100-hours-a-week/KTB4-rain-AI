"""
retriever.py - RAG 검색기 (Retriever)

KorQuAD 데이터로 구축한 FAISS 벡터 저장소에서, 질문과 관련된 문서를
검색해오는 역할을 한다.

- 임베딩 모델: BAAI/bge-m3 (로컬, Colab A100 GPU에서 임베딩 생성)
- 벡터 저장소: FAISS
- Gemini API 무료 임베딩 사용 시 일일 요청 한도(1,000건)에 걸려
  로컬 임베딩 모델로 전환했다 (자세한 내용은 06/README.md 트러블슈팅 참고)
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def load_retriever(faiss_path, embedding_model="BAAI/bge-m3", k=3, device="cpu"):
    """
    저장된 FAISS 벡터 저장소를 불러와서 retriever 객체를 생성하는 함수

    Args:
        faiss_path: FAISS 인덱스가 저장된 경로
        embedding_model: 임베딩에 사용할 모델 이름
        k: 검색 시 반환할 문서 개수
        device: 'cuda' 또는 'cpu'

    Returns:
        retriever: 질문을 넣으면 관련 문서를 반환하는 객체
    """
    print("임베딩 모델 로드 중...")
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={'device': device},
        encode_kwargs={'normalize_embeddings': True}
    )

    print("FAISS 벡터 저장소 로드 중...")
    vectorstore = FAISS.load_local(
        faiss_path,
        embeddings,
        allow_dangerous_deserialization=True
    )
    print("로드 완료!")

    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever


def search(retriever, question):
    """
    질문을 받아서 관련 문서를 검색하는 함수

    Args:
        retriever: load_retriever()로 만든 retriever 객체
        question: 검색할 질문

    Returns:
        문서 리스트 (각 문서는 page_content 속성으로 텍스트 접근 가능)
    """
    return retriever.invoke(question)


if __name__ == "__main__":
    # 테스트용 실행 (FAISS 인덱스는 별도로 구축되어 있어야 함)
    FAISS_PATH = "faiss_index_local"

    retriever = load_retriever(FAISS_PATH)

    test_question = "이순신은 누구인가?"
    results = search(retriever, test_question)

    print(f"\n질문: {test_question}")
    print(f"검색된 문서 수: {len(results)}개\n")
    for i, doc in enumerate(results, 1):
        print(f"--- 검색 결과 {i} ---")
        print(doc.page_content[:200])
        print()