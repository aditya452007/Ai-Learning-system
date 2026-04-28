from app.domain.models.retrieval import RetrievalResult
from app.domain.services.retrieval_fusion import ReciprocalRankFusionService


def test_reciprocal_rank_fusion_rewards_overlap() -> None:
    semantic = [
        RetrievalResult("chunk_a", "source_1", 0.9, 1, "semantic", "A"),
        RetrievalResult("chunk_b", "source_1", 0.8, 2, "semantic", "B"),
    ]
    keyword = [
        RetrievalResult("chunk_b", "source_1", 5.0, 1, "keyword", "B"),
        RetrievalResult("chunk_c", "source_2", 4.0, 2, "keyword", "C"),
    ]

    fused = ReciprocalRankFusionService().fuse([semantic, keyword], top_k=3)

    assert fused[0].chunk_id == "chunk_b"
    assert fused[0].retriever == "hybrid"
    assert fused[0].metadata["contributors"] == ["keyword", "semantic"]

