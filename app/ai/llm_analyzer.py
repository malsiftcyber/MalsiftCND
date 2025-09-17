"""
LLM-powered analysis for device identification and OS detection
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

from app.core.config import settings


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"


@dataclass
class DeviceAnalysis:
    """Device analysis result"""
    device_type: str
    operating_system: str
    confidence: float
    reasoning: str
    additional_info: Dict[str, Any]


class LLMAnalyzer:
    """LLM-powered device and OS analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger("ai.llm_analyzer")
        self.providers = self._initialize_providers()
    
    def _initialize_providers(self) -> Dict[LLMProvider, Any]:
        """Initialize LLM providers"""
        providers = {}
        
        if settings.OPENAI_API_KEY:
            try:
                import openai
                providers[LLMProvider.OPENAI] = openai.AsyncOpenAI(
                    api_key=settings.OPENAI_API_KEY
                )
            except ImportError:
                self.logger.warning("OpenAI library not available")
        
        if settings.ANTHROPIC_API_KEY:
            try:
                import anthropic
                providers[LLMProvider.ANTHROPIC] = anthropic.AsyncAnthropic(
                    api_key=settings.ANTHROPIC_API_KEY
                )
            except ImportError:
                self.logger.warning("Anthropic library not available")
        
        if settings.GROQ_API_KEY:
            try:
                import groq
                providers[LLMProvider.GROQ] = groq.AsyncGroq(
                    api_key=settings.GROQ_API_KEY
                )
            except ImportError:
                self.logger.warning("Groq library not available")
        
        return providers
    
    async def analyze_device(self, scan_data: Dict[str, Any]) -> DeviceAnalysis:
        """Analyze device based on scan data"""
        if not self.providers:
            return self._fallback_analysis(scan_data)
        
        # Prepare analysis prompt
        prompt = self._build_analysis_prompt(scan_data)
        
        # Try providers in order of preference
        for provider_type, provider in self.providers.items():
            try:
                result = await self._query_provider(provider_type, provider, prompt)
                if result:
                    return self._parse_analysis_result(result)
            except Exception as e:
                self.logger.error(f"Provider {provider_type.value} failed: {e}")
                continue
        
        # Fallback if all providers fail
        return self._fallback_analysis(scan_data)
    
    def _build_analysis_prompt(self, scan_data: Dict[str, Any]) -> str:
        """Build analysis prompt from scan data"""
        prompt = """
You are a cybersecurity expert analyzing network scan data to identify device types and operating systems.

Scan Data:
"""
        
        # Extract relevant information
        hosts = scan_data.get("hosts", {})
        for host_ip, host_info in hosts.items():
            prompt += f"\nHost: {host_ip}\n"
            
            # Add hostname if available
            if host_info.get("hostname"):
                prompt += f"Hostname: {host_info['hostname']}\n"
            
            # Add OS information
            os_info = host_info.get("os", {})
            if os_info:
                prompt += f"OS Detection: {os_info.get('name', 'Unknown')} "
                prompt += f"(Accuracy: {os_info.get('accuracy', 0)}%)\n"
            
            # Add services
            services = host_info.get("services", [])
            if services:
                prompt += "Open Services:\n"
                for service in services:
                    prompt += f"  - Port {service.get('port', '?')}: "
                    prompt += f"{service.get('service', 'unknown')} "
                    if service.get('version'):
                        prompt += f"({service.get('version')})"
                    prompt += "\n"
            
            # Add port information
            ports = host_info.get("ports", {})
            if ports:
                open_ports = [p for p in ports.values() if p.get('state') == 'open']
                if open_ports:
                    prompt += f"Open Ports: {len(open_ports)} total\n"
        
        prompt += """
Please analyze this data and provide:
1. Most likely device type (e.g., Windows Server, Linux Router, IoT Device, etc.)
2. Operating system (be specific if possible)
3. Confidence level (0-100%)
4. Reasoning for your analysis
5. Any additional security-relevant information

Respond in JSON format:
{
    "device_type": "string",
    "operating_system": "string", 
    "confidence": number,
    "reasoning": "string",
    "additional_info": {
        "key": "value"
    }
}
"""
        
        return prompt
    
    async def _query_provider(self, provider_type: LLMProvider, provider: Any, prompt: str) -> Optional[str]:
        """Query specific LLM provider"""
        if provider_type == LLMProvider.OPENAI:
            response = await provider.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            return response.choices[0].message.content
        
        elif provider_type == LLMProvider.ANTHROPIC:
            response = await provider.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        elif provider_type == LLMProvider.GROQ:
            response = await provider.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            return response.choices[0].message.content
        
        return None
    
    def _parse_analysis_result(self, result: str) -> DeviceAnalysis:
        """Parse LLM analysis result"""
        try:
            # Try to extract JSON from the response
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx]
                data = json.loads(json_str)
                
                return DeviceAnalysis(
                    device_type=data.get("device_type", "Unknown"),
                    operating_system=data.get("operating_system", "Unknown"),
                    confidence=data.get("confidence", 0.0),
                    reasoning=data.get("reasoning", ""),
                    additional_info=data.get("additional_info", {})
                )
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Failed to parse LLM result: {e}")
        
        # Fallback parsing
        return DeviceAnalysis(
            device_type="Unknown",
            operating_system="Unknown",
            confidence=0.0,
            reasoning="Failed to parse LLM response",
            additional_info={"raw_response": result}
        )
    
    def _fallback_analysis(self, scan_data: Dict[str, Any]) -> DeviceAnalysis:
        """Fallback analysis when LLM is not available"""
        hosts = scan_data.get("hosts", {})
        
        # Simple heuristic-based analysis
        device_type = "Unknown"
        os_info = "Unknown"
        confidence = 0.0
        reasoning = "Basic heuristic analysis"
        
        for host_ip, host_info in hosts.items():
            # Check OS detection results
            os_data = host_info.get("os", {})
            if os_data.get("name"):
                os_info = os_data["name"]
                confidence = os_data.get("accuracy", 0) / 100.0
            
            # Check services for device type hints
            services = host_info.get("services", [])
            service_names = [s.get("service", "").lower() for s in services]
            
            if "ssh" in service_names:
                device_type = "Linux Server"
                confidence = max(confidence, 0.7)
            elif "rdp" in service_names or "smb" in service_names:
                device_type = "Windows Server"
                confidence = max(confidence, 0.8)
            elif "http" in service_names or "https" in service_names:
                device_type = "Web Server"
                confidence = max(confidence, 0.6)
        
        return DeviceAnalysis(
            device_type=device_type,
            operating_system=os_info,
            confidence=confidence,
            reasoning=reasoning,
            additional_info={}
        )
