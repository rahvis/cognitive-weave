# cognitive_weave_poc/conversational_agent.py

import re
from typing import List, Optional, Dict, Set

from openai import AzureOpenAI

from cognitive_weave.semantic_oracle import SemanticOracleInterface
from cognitive_weave.data_structures import InsightParticle, InsightAggregateAttributes
from cognitive_weave.utils import get_azure_openai_client, AZURE_OAI_DEPLOYMENT_GPT4, log_info, log_error

# A simple list of common stopwords for basic relevance checking
STOPWORDS = set([
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "should",
    "can", "could", "may", "might", "must", "i", "you", "he", "she", "it",
    "we", "they", "me", "him", "her", "us", "them", "my", "your", "his",
    "its", "our", "their", "mine", "yours", "hers", "ours", "theirs",
    "to", "of", "in", "on", "at", "for", "with", "about", "against",
    "between", "into", "through", "during", "before", "after", "above",
    "below", "from", "up", "down", "out", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why",
    "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "just", "don", "shouldve", "now",
    "what", "tell", "me", "give", "explain", "about", "whats", "who", "whom"
])


class ConversationalAgent:
    """
    A conversational agent that uses the Cognitive Weave memory system.
    """
    def __init__(self):
        self.soi = SemanticOracleInterface()
        self.conversational_llm_client: AzureOpenAI = get_azure_openai_client()
        self.conversational_llm_deployment: str = AZURE_OAI_DEPLOYMENT_GPT4
        
        self.memory_store: List[InsightParticle] = []
        self.turn_count = 0
        self.ia_synthesis_interval = 3 # Synthesize IA every N turns

        log_info("ConversationalAgent initialized.")
        log_info(f"  SOI ready: {'Yes' if self.soi else 'No'}")
        log_info(f"  Conversational LLM client ready: {'Yes' if self.conversational_llm_client else 'No'}")
        log_info(f"  Using LLM deployment for conversation: {self.conversational_llm_deployment}")

    def _preprocess_query_for_keywords(self, text: str) -> Set[str]:
        """Simple preprocessing to extract potential keywords from text."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text) # Remove punctuation
        words = text.split()
        return {word for word in words if word not in STOPWORDS and len(word) > 2}

    def add_to_memory(self, text_input: str, source: str = "user_input"):
        """
        Processes text input, creates an InsightParticle, and adds it to memory.
        """
        log_info(f"\n--- Adding to Memory (Source: {source}) ---")
        log_info(f"Raw text: \"{text_input}\"")
        
        ip_attributes = self.soi.enrich_text_to_ip_attributes(text_input)
        if ip_attributes:
            new_ip = InsightParticle(
                core_data=text_input, # Store original text as core_data for this PoC
                resonance_keys=ip_attributes.get("resonance_keys", []),
                signifiers=ip_attributes.get("signifiers", []),
                situational_imprint=ip_attributes.get("situational_imprint"),
                extracted_entities=ip_attributes.get("extracted_entities", [])
            )
            self.memory_store.append(new_ip)
            log_info(f"Successfully created and stored IP: {new_ip.particle_id}")
            log_info(f"  Situational Imprint: \"{new_ip.situational_imprint}\"")
            log_info(f"  Resonance Keys: {new_ip.resonance_keys}")
            log_info(f"  Total IPs in memory: {len(self.memory_store)}")
        else:
            log_error("Failed to enrich text for IP creation. Not added to memory.")

    def retrieve_relevant_insights(self, query_text: str, top_k: int = 2) -> List[InsightParticle]:
        """
        Retrieves relevant InsightParticles from memory based on the query.
        This is a simplified keyword-based retrieval for PoC.
        """
        log_info(f"\n--- Retrieving Relevant Insights from Memory ---")
        log_info(f"Query for retrieval: \"{query_text}\"")

        if not self.memory_store:
            log_info("Memory is empty. No insights to retrieve.")
            return []

        query_keywords = self._preprocess_query_for_keywords(query_text)
        log_info(f"Processed query keywords: {query_keywords}")

        scored_ips = []
        for ip in self.memory_store:
            score = 0
            # Score based on resonance key overlap
            for r_key_phrase in ip.resonance_keys:
                r_key_words = self._preprocess_query_for_keywords(r_key_phrase)
                score += len(query_keywords.intersection(r_key_words)) * 2 # Higher weight for resonance keys
            
            # Score based on situational imprint overlap
            if ip.situational_imprint:
                imprint_words = self._preprocess_query_for_keywords(ip.situational_imprint)
                score += len(query_keywords.intersection(imprint_words))
            
            if score > 0:
                scored_ips.append({"ip": ip, "score": score})
        
        # Sort by score descending
        sorted_ips = sorted(scored_ips, key=lambda x: x["score"], reverse=True)
        
        relevant_ips = [item["ip"] for item in sorted_ips[:top_k]]
        
        if relevant_ips:
            log_info(f"Retrieved {len(relevant_ips)} relevant IP(s):")
            for i, ip in enumerate(relevant_ips):
                log_info(f"  {i+1}. IP ID: {ip.particle_id}, Imprint: \"{ip.situational_imprint}\" (Score: {next(item['score'] for item in sorted_ips if item['ip'].particle_id == ip.particle_id)})")
        else:
            log_info("No sufficiently relevant IPs found in memory for this query.")
            # Fallback: retrieve the most recent IP if no keyword match
            if self.memory_store and top_k > 0:
                log_info(f"Falling back to retrieving the most recent IP.")
                most_recent_ip = [self.memory_store[-1]]
                log_info(f"  1. IP ID: {most_recent_ip[0].particle_id}, Imprint: \"{most_recent_ip[0].situational_imprint}\" (Recent)")
                return most_recent_ip


        return relevant_ips

    def _attempt_ia_synthesis(self):
        """
        Attempts to synthesize an InsightAggregate if enough IPs are present.
        """
        log_info(f"\n--- Attempting Insight Aggregate (IA) Synthesis ---")
        if len(self.memory_store) < 2: # Need at least 2 IPs to synthesize something meaningful
            log_info("Not enough IPs in memory to attempt IA synthesis.")
            return

        # For this PoC, we'll use situational imprints of ALL current IPs
        # In a real system, you'd select related IPs based on clustering or other metrics
        imprints_for_synthesis = [ip.situational_imprint for ip in self.memory_store if ip.situational_imprint]
        
        if not imprints_for_synthesis or len(imprints_for_synthesis) < 2:
            log_info("Not enough valid imprints available for IA synthesis.")
            return

        log_info(f"Using {len(imprints_for_synthesis)} IP imprints for IA synthesis:")
        for i, imprint in enumerate(imprints_for_synthesis):
            log_info(f"  Imprint {i+1}: \"{imprint}\"")

        ia_attributes: Optional[InsightAggregateAttributes] = self.soi.synthesize_ia_from_imprints(imprints_for_synthesis)

        if ia_attributes:
            log_info("Successfully synthesized Insight Aggregate attributes.")
            # Create a new IP for this IA and add it to memory
            new_ia_particle = InsightParticle(
                core_data=ia_attributes.ia_core_data,
                resonance_keys=ia_attributes.ia_resonance_keys,
                signifiers=ia_attributes.ia_signifiers,
                situational_imprint=ia_attributes.ia_situational_imprint,
                is_aggregate=True,
                # For PoC, assume it's derived from all IPs used for synthesis
                derived_from_ids=[ip.particle_id for ip in self.memory_store if ip.situational_imprint in imprints_for_synthesis] 
            )
            self.memory_store.append(new_ia_particle) # Add the new IA to memory
            log_info(f"New IA (ID: {new_ia_particle.particle_id}) added to memory.")
            log_info(f"  IA Core Data: \"{new_ia_particle.core_data}\"")
            log_info(f"  Total IPs in memory (including IA): {len(self.memory_store)}")
        else:
            log_error("IA synthesis failed or produced no attributes.")


    def generate_response(self, user_query: str) -> str:
        """
        Generates a response to the user's query, using retrieved memory.
        """
        log_info(f"\n--- Generating Response for Query ---")
        log_info(f"User query: \"{user_query}\"")

        relevant_insights = self.retrieve_relevant_insights(user_query)
        
        memory_context_str = "No specific memories retrieved for this query."
        if relevant_insights:
            memory_context_parts = []
            for i, insight in enumerate(relevant_insights):
                context = f"Memory {i+1} (Type: {'Aggregate' if insight.is_aggregate else 'Particle'}): "
                if insight.is_aggregate:
                    context += f"Synthesized Insight: \"{insight.core_data}\" (Summary: \"{insight.situational_imprint}\")"
                else:
                    context += f"\"{insight.situational_imprint}\" (Keywords: {insight.resonance_keys})"
                memory_context_parts.append(context)
            memory_context_str = "\n".join(memory_context_parts)
        
        system_prompt = f"""You are a helpful AI assistant.
You have access to some memories from previous interactions or synthesized insights.
Use these memories to provide a comprehensive and contextually relevant answer to the user's query.
If the memories are not directly relevant, answer the query based on your general knowledge but acknowledge if you are not using specific memories.

Available Memories:
---
{memory_context_str}
---
"""
        
        log_info(f"\n--- Prompt for Conversational LLM ---")
        log_info(f"System Prompt Snippet:\n{system_prompt[:300]}...") # Log a snippet
        log_info(f"User Query to LLM: \"{user_query}\"")
        
        try:
            response = self.conversational_llm_client.chat.completions.create(
                model=self.conversational_llm_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            assistant_response = response.choices[0].message.content
            log_info("Successfully received response from conversational LLM.")
            return assistant_response.strip()
        except Exception as e:
            log_error(f"Error during conversational LLM call: {e}")
            return "I encountered an error trying to process your request. Please try again."

    def start_chat(self):
        """
        Starts the interactive chat loop with the user.
        """
        print("\nWelcome to the Cognitive Weave Conversational Agent!")
        print("Type 'quit' to exit.")
        print("I will try to remember our conversation and synthesize insights.")

        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'quit':
                print("Agent: Goodbye!")
                break

            # Add user input to memory
            self.add_to_memory(user_input, source="user_input")
            
            # Generate and print agent's response
            agent_response = self.generate_response(user_input)
            print(f"Agent: {agent_response}")

            # Add agent's response to memory as well (optional, but can be useful)
            # self.add_to_memory(agent_response, source="agent_response")

            self.turn_count += 1
            if self.turn_count % self.ia_synthesis_interval == 0:
                self._attempt_ia_synthesis()
        
        log_info("\nChat session ended.")
        log_info(f"Final memory store contains {len(self.memory_store)} IPs:")
        for i, ip in enumerate(self.memory_store):
            type_info = "Aggregate" if ip.is_aggregate else "Particle"
            core_info = ip.core_data if ip.is_aggregate else ip.situational_imprint
            log_info(f"  {i+1}. ID: {ip.particle_id} (Type: {type_info}), Content: \"{str(core_info)[:100]}...\"")


if __name__ == "__main__":
    # Ensure Azure credentials are set up (as per utils.py logic)
    from cognitive_weave.utils import AZURE_OAI_ENDPOINT, AZURE_OAI_KEY, _PLACEHOLDER_ENDPOINT, _PLACEHOLDER_KEY
    if AZURE_OAI_ENDPOINT == _PLACEHOLDER_ENDPOINT or AZURE_OAI_KEY == _PLACEHOLDER_KEY:
        print("="*80)
        print("ERROR: Azure OpenAI credentials in cognitive_weave/utils.py appear to be the original placeholders.")
        print("Please open cognitive_weave/utils.py and replace them with your actual Azure credentials before running the agent.")
        print("="*80)
    else:
        agent = ConversationalAgent()
        agent.start_chat()
