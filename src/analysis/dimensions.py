"""
Perception dimension discovery and analysis using local LLMs.
"""

from typing import Dict, List, Optional
import json
import re
import requests

from config.settings import (
    LOCAL_LLM_HOST,
    LOCAL_LLM_MODEL,
    LOCAL_LLM_TEMPERATURE,
    PERCEPTION_DIMENSIONS_COUNT,
)
from src.embeddings.vector_db import VectorDatabase
from src.rag.retriever import DocumentRetriever
from src.utils.logger import get_logger
from src.utils.models import PerceptionDimension, PerceptionScore

logger = get_logger("analysis.dimensions")


class LocalLLMClient:
    """Small Ollama client for analysis modules."""

    def __init__(
        self,
        model_name: str = LOCAL_LLM_MODEL,
        host: str = LOCAL_LLM_HOST,
        temperature: float = LOCAL_LLM_TEMPERATURE,
    ):
        self.model_name = model_name
        self.host = host.rstrip("/")
        self.temperature = temperature

    def generate(self, prompt: str, timeout: int = 120) -> str:
        """Generate text with the configured local LLM."""
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": self.temperature,
                    "stream": False,
                },
                timeout=timeout,
            )
            if response.status_code == 200:
                return response.json().get("response", "")

            logger.error(f"Local LLM API error: {response.status_code} - {response.text}")
            return ""
        except requests.exceptions.Timeout:
            logger.error("Local LLM request timed out")
            return ""
        except Exception as exc:
            logger.error(f"Error calling local LLM: {exc}")
            return ""


def _extract_json_array(text: str) -> Optional[List]:
    """Extract the first JSON array from an LLM response."""
    json_match = re.search(r"\[.*\]", text, re.DOTALL)
    if not json_match:
        return None

    try:
        parsed = json.loads(json_match.group())
        return parsed if isinstance(parsed, list) else None
    except json.JSONDecodeError as exc:
        logger.error(f"Error parsing JSON array from local LLM response: {exc}")
        return None


def _extract_json_object(text: str) -> Optional[Dict]:
    """Extract the first JSON object from an LLM response."""
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if not json_match:
        return None

    try:
        parsed = json.loads(json_match.group())
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError as exc:
        logger.error(f"Error parsing JSON object from local LLM response: {exc}")
        return None


class DimensionDiscovery:
    """Discover perception dimensions from documents."""

    def __init__(self, vector_db: VectorDatabase, model_name: str = LOCAL_LLM_MODEL):
        self.vector_db = vector_db
        self.llm = LocalLLMClient(model_name=model_name)

    def discover_dimensions(self, companies: List[str]) -> List[PerceptionDimension]:
        """Automatically discover perception dimensions from all companies' documents."""
        logger.info(f"Discovering perception dimensions for {len(companies)} companies")

        company_samples = {}
        for company in companies:
            company_samples[company] = self._get_company_sample(company)

        themes = self._extract_themes(company_samples)
        dimensions = self._identify_dimensions_from_themes(themes)

        logger.info(f"Discovered {len(dimensions)} perception dimensions")
        return dimensions

    def _get_company_sample(self, company: str, sample_size: int = 10) -> str:
        """Get sample documents from a company."""
        try:
            collection = self.vector_db.get_collection("brand_documents")
            if not collection:
                return ""

            results = collection.get(where={"company": company}, limit=sample_size)

            if results and results["documents"]:
                return "\n".join(results["documents"][:sample_size])

        except Exception as exc:
            logger.warning(f"Error getting sample for {company}: {exc}")

        return ""

    def _extract_themes(self, company_samples: Dict[str, str]) -> str:
        """Extract recurring themes from samples."""
        theme_extraction_prompt = """
You are a brand analyst. Analyze these company brand documents and identify the
top recurring themes, dimensions, and positioning factors that appear across
the companies.

"""

        for company, sample in company_samples.items():
            theme_extraction_prompt += f"\n## {company}:\n{sample[:500]}\n"

        theme_extraction_prompt += """

Identify 10-15 key dimensions or themes that companies use to differentiate
themselves.

Respond ONLY with a JSON array:
["dimension1", "dimension2", "..."]
"""

        try:
            response_text = self.llm.generate(theme_extraction_prompt)
            themes = _extract_json_array(response_text)
            if themes:
                return ", ".join(str(theme) for theme in themes)

        except Exception as exc:
            logger.error(f"Error extracting themes: {exc}")

        return ""

    def _identify_dimensions_from_themes(self, themes: str) -> List[PerceptionDimension]:
        """Convert themes to structured dimensions."""
        if not themes:
            return self._get_default_dimensions()

        dimension_prompt = f"""
You are a brand analyst.

Based on these brand positioning themes: {themes}

Create {PERCEPTION_DIMENSIONS_COUNT} key perception dimensions that can be used
to compare insurance companies. For each dimension:

1. Give it a clear, concise name
2. Provide a definition
3. List 3-5 evidence keywords that indicate high performance on this dimension

Respond ONLY with a JSON array:
[
    {{
        "name": "dimension_name",
        "description": "...",
        "keywords": ["keyword1", "keyword2"]
    }}
]
"""

        try:
            response_text = self.llm.generate(dimension_prompt)
            data = _extract_json_array(response_text)

            if data:
                dimensions = []
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    dimensions.append(
                        PerceptionDimension(
                            dimension_name=item.get("name", "unknown"),
                            description=item.get("description", ""),
                            evidence_keywords=item.get("keywords", []),
                            scoring_method="evidence_based_local_llm_scoring",
                        )
                    )

                if dimensions:
                    return dimensions

        except Exception as exc:
            logger.error(f"Error identifying dimensions: {exc}")

        return self._get_default_dimensions()

    def _get_default_dimensions(self) -> List[PerceptionDimension]:
        """Get default perception dimensions."""
        defaults = [
            {
                "name": "Trust & Reliability",
                "description": "Perceived trustworthiness, credibility, and reliability of the brand",
            },
            {
                "name": "Innovation",
                "description": "Perceived innovation and modernization of products and services",
            },
            {
                "name": "Customer Service",
                "description": "Quality of customer support and service orientation",
            },
            {
                "name": "Digital Experience",
                "description": "Digital capabilities, online presence, and tech-forward positioning",
            },
            {
                "name": "Transparency",
                "description": "Clarity in communication, openness about products and policies",
            },
            {
                "name": "Affordability",
                "description": "Cost-effectiveness and value for money proposition",
            },
            {
                "name": "Security & Protection",
                "description": "Financial security, data protection, and policyholder safety emphasis",
            },
            {
                "name": "Brand Legacy",
                "description": "Historical presence, market longevity, and established market position",
            },
        ]

        return [
            PerceptionDimension(
                dimension_name=dimension["name"],
                description=dimension["description"],
                evidence_keywords=[],
                scoring_method="default_dimension",
            )
            for dimension in defaults
        ]


class PerceptionScorer:
    """Score companies on perception dimensions."""

    def __init__(self, retriever: DocumentRetriever, model_name: str = LOCAL_LLM_MODEL):
        self.retriever = retriever
        self.llm = LocalLLMClient(model_name=model_name, temperature=0.5)

    def score_all_companies(
        self,
        companies: List[str],
        dimensions: List[PerceptionDimension],
    ) -> Dict[str, Dict[str, PerceptionScore]]:
        """Score all companies on all dimensions."""
        logger.info(f"Scoring {len(companies)} companies on {len(dimensions)} dimensions")

        results = {}
        for company in companies:
            results[company] = {}
            for dimension in dimensions:
                score = self._score_company_dimension(company, dimension)
                results[company][dimension.dimension_name] = score

        logger.info("Scoring complete")
        return results

    def _score_company_dimension(
        self,
        company: str,
        dimension: PerceptionDimension,
    ) -> PerceptionScore:
        """Score a company on a specific dimension."""
        logger.debug(f"Scoring {company} on {dimension.dimension_name}")

        query = f"{dimension.dimension_name}: {dimension.description}"
        context = self.retriever.retrieve_for_analysis(query, company, top_k=5)

        scoring_prompt = f"""
You are a brand perception analyst. Score "{company}" on the dimension:

DIMENSION: {dimension.dimension_name}
DEFINITION: {dimension.description}

Based on the following documents about the company:
{context}

Provide a score from 0-10 where:
- 0-2: No evidence or negative signals
- 3-4: Weak or minimal emphasis
- 5-6: Moderate emphasis
- 7-8: Strong emphasis
- 9-10: Very strong emphasis and differentiation

Respond ONLY with JSON:
{{
    "score": <number 0-10>,
    "rationale": "Explain the score in 2-3 sentences",
    "evidence_points": ["key point 1", "key point 2", "key point 3"],
    "confidence": <number 0-1>
}}
"""

        try:
            response_text = self.llm.generate(scoring_prompt)
            data = _extract_json_object(response_text)

            if data:
                return PerceptionScore(
                    company=company,
                    dimension=dimension.dimension_name,
                    score=float(data.get("score", 5)),
                    rationale=data.get("rationale", ""),
                    evidence=data.get("evidence_points", data.get("evidence", [])),
                    confidence=float(data.get("confidence", 0.7)) * 0.85,
                )

        except Exception as exc:
            logger.error(f"Error scoring {company} on {dimension.dimension_name}: {exc}")

        return PerceptionScore(
            company=company,
            dimension=dimension.dimension_name,
            score=5.0,
            rationale="Unable to score with available local LLM response.",
            evidence=[],
            confidence=0.0,
        )


__all__ = ["DimensionDiscovery", "PerceptionScorer"]
