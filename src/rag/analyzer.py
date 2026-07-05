"""
LLM-based analysis engine using RAG - FREE LOCAL VERSION
Uses local LLMs (Ollama) - no API costs!
"""

from typing import Dict, List, Optional, Any
import json
import re
import requests
from src.rag.retriever import DocumentRetriever
from src.utils.logger import get_logger
from src.utils.models import BrandPositioning, PerceptionScore
from config.settings import LOCAL_LLM_MODEL, LOCAL_LLM_HOST, LOCAL_LLM_TEMPERATURE

logger = get_logger("rag.analyzer")


class RAGAnalyzer:
    """RAG-based analyzer using FREE local LLM (Ollama)"""
    
    def __init__(self, retriever: DocumentRetriever, model_name: str = LOCAL_LLM_MODEL):
        self.retriever = retriever
        self.model_name = model_name
        self.llm_host = LOCAL_LLM_HOST
        self.temperature = LOCAL_LLM_TEMPERATURE
        
        logger.info(f"Initialized RAGAnalyzer with local model: {model_name}")
        logger.info(f"LLM Host: {self.llm_host}")
        logger.info("✓ FREE - No API costs! Running locally.")
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test connection to local LLM"""
        try:
            response = requests.get(f"{self.llm_host}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✓ Connected to local LLM server")
                return True
        except Exception as e:
            logger.warning(f"Could not connect to LLM at {self.llm_host}: {str(e)}")
            logger.warning("Make sure Ollama is running: ollama serve")
            return False
    
    def _call_local_llm(self, prompt: str) -> str:
        """Call local LLM via Ollama API"""
        try:
            response = requests.post(
                f"{self.llm_host}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": self.temperature,
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"LLM API error: {response.status_code}")
                return ""
        
        except requests.exceptions.Timeout:
            logger.error("LLM request timeout - model may be slow or unavailable")
            return ""
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            return ""
    
    def analyze_brand_positioning(self, company: str) -> BrandPositioning:
        """Analyze brand positioning using RAG"""
        logger.info(f"Analyzing brand positioning for {company}")
        
        # Retrieve relevant documents
        positioning_queries = [
            f"What is {company}'s brand positioning and key messaging?",
            f"How does {company} differentiate itself from competitors?",
            f"What are {company}'s main value propositions?",
            f"What trust signals does {company} use in its messaging?"
        ]
        
        all_context = ""
        for query in positioning_queries:
            context = self.retriever.retrieve_for_analysis(query, company, top_k=3)
            all_context += context + "\n\n"
        
        # Create analysis prompt
        analysis_prompt = f"""You are a brand intelligence analyst. Based on the provided documents about {company}, 
analyze and extract the following information about their brand positioning:

1. Positioning Statement (1-2 sentences)
2. Main Claims (list of 3-5 key claims made about the product/service)
3. Trust Signals (evidence of credibility, security, reliability)
4. Emotional Themes (emotional appeals used in messaging)
5. Target Segments (customer segments being targeted)
6. Product Focus (main product categories emphasized)
7. Key Differentiators (what makes them unique)

DOCUMENTS:
{all_context}

Respond ONLY with JSON (no other text):
{{
    "positioning_statement": "...",
    "main_claims": ["...", "...", "..."],
    "trust_signals": ["...", "...", "..."],
    "emotional_themes": ["...", "...", "..."],
    "target_segments": ["...", "...", "..."],
    "product_focus": ["...", "...", "..."],
    "key_differentiators": ["...", "...", "..."],
    "market_position": "..."
}}"""
        
        # Get LLM response
        try:
            response_text = self._call_local_llm(analysis_prompt)
            
            if not response_text:
                logger.warning(f"Empty response from LLM for {company}")
                return BrandPositioning(brand=company, positioning_statement="Unable to analyze", confidence=0.0)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                return BrandPositioning(
                    brand=company,
                    positioning_statement=data.get('positioning_statement', ''),
                    main_claims=data.get('main_claims', []),
                    trust_signals=data.get('trust_signals', []),
                    emotional_themes=data.get('emotional_themes', []),
                    target_segments=data.get('target_segments', []),
                    product_focus=data.get('product_focus', []),
                    key_differentiators=data.get('key_differentiators', []),
                    market_position=data.get('market_position', ''),
                    confidence=0.75,  # Lower confidence for local model
                    supporting_evidence=self._extract_evidence(all_context)
                )
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
        except Exception as e:
            logger.error(f"Error analyzing brand positioning: {str(e)}")
        
        # Return default if analysis fails
        return BrandPositioning(
            brand=company,
            positioning_statement="Unable to determine",
            confidence=0.0
        )
    
    def score_perception_dimension(
        self,
        company: str,
        dimension: str,
        dimension_description: str
    ) -> PerceptionScore:
        """Score a company on a specific perception dimension"""
        logger.debug(f"Scoring {company} on dimension: {dimension}")
        
        query = f"Evidence of {dimension} in {company}'s brand and messaging"
        context = self.retriever.retrieve_for_analysis(query, company, top_k=5)
        
        scoring_prompt = f"""You are a brand perception analyst. Score {company} on the dimension of "{dimension}".

Dimension Definition: {dimension_description}

Based on the following documents:
{context}

Provide:
1. A score from 0-10 (where 10 is strongest on this dimension)
2. A brief rationale for the score
3. Key evidence points (2-3 specific pieces of evidence)

Respond ONLY with JSON (no other text):
{{
    "score": <number 0-10>,
    "rationale": "...",
    "evidence": ["...", "...", "..."],
    "confidence": <number 0-1>
}}"""
        
        try:
            response_text = self._call_local_llm(scoring_prompt)
            
            if not response_text:
                logger.warning(f"Empty response from LLM for {company} on {dimension}")
                return PerceptionScore(
                    company=company,
                    dimension=dimension,
                    score=5.0,
                    rationale="Unable to score because the local LLM returned an empty response.",
                    confidence=0.0,
                )
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                return PerceptionScore(
                    company=company,
                    dimension=dimension,
                    score=float(data.get('score', 5)),
                    rationale=data.get('rationale', ''),
                    evidence=data.get('evidence', []),
                    supporting_snippets=self._extract_snippets(context, data.get('evidence', [])),
                    confidence=float(data.get('confidence', 0.6)) * 0.85  # Adjust for local model
                )
        
        except Exception as e:
            logger.error(f"Error scoring dimension: {str(e)}")
        
        return PerceptionScore(
            company=company,
            dimension=dimension,
            score=5.0,
            rationale="Unable to score with available local LLM response.",
            confidence=0.0
        )
    
    def generate_comparison_insights(
        self,
        dimension: str,
        companies: List[str],
        scores: Dict[str, float]
    ) -> List[str]:
        """Generate insights comparing companies on a dimension"""
        logger.debug(f"Generating comparison insights for {dimension}")
        
        # Get contexts for all companies
        contexts = {}
        for company in companies:
            query = f"Evidence of {dimension} in {company}'s brand"
            contexts[company] = self.retriever.retrieve_for_analysis(query, company, top_k=3)
        
        comparison_prompt = f"""You are a competitive intelligence analyst. Based on how these companies position themselves
on the dimension of "{dimension}", provide 3-4 key competitive insights.

{chr(10).join([f"## {company}: Score {scores[company]}/10" for company in companies])}

CONTEXTS:
{chr(10).join([f"### {company}:" + chr(10) + contexts[company] for company in companies])}

Provide insights that highlight:
- Competitive advantages
- Gaps and weaknesses
- Strategic positioning differences
- Opportunity for differentiation

Format as a numbered list.
"""
        
        try:
            response_text = self._call_local_llm(comparison_prompt)

            # Parse insights
            insights = [
                line.strip()
                for line in response_text.split('\n')
                if line.strip() and line.strip()[0].isdigit()
            ]

            return insights
        
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    def _extract_evidence(self, context: str) -> List[str]:
        """Extract evidence snippets from context"""
        lines = context.split('\n')
        snippets = []
        for line in lines:
            if len(line.strip()) > 20 and '[Document' not in line:
                snippets.append(line.strip()[:100])
        return snippets[:5]
    
    def _extract_snippets(self, context: str, evidence_items: List[str]) -> List[str]:
        """Extract supporting text snippets"""
        snippets = []
        lines = context.split('\n')
        
        for item in evidence_items:
            for line in lines:
                if item.lower() in line.lower() and len(line) > 20:
                    snippets.append(line.strip()[:150])
                    break
        
        return snippets


__all__ = ["RAGAnalyzer"]
