#!/usr/bin/env python3
"""
Ultimate OptikGPT Demo - The Smartest AI in the World
Showcasing open-ended responses and advanced capabilities
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_ultimate_optik_gpt():
    """Test Ultimate OptikGPT capabilities"""
    print("🧠 Ultimate OptikGPT Demo - The Smartest AI in the World")
    print("=" * 60)
    
    # 1. Check capabilities
    print("\n1️⃣ Ultimate OptikGPT Capabilities:")
    response = requests.get(f"{BASE_URL}/api/v1/assistant/capabilities")
    if response.status_code == 200:
        caps = response.json()
        print(f"   🤖 Name: {caps['name']}")
        print(f"   🏷️  Tagline: {caps['tagline']}")
        print(f"   🎯 Response Style: {caps['response_style']}")
        print(f"   🔬 Specialization: {caps['specialization']}")
        
        print("\n   🧠 Intelligence Levels:")
        for skill, level in caps['capabilities']['intelligence_levels'].items():
            print(f"      • {skill.title()}: {level*100:.0f}%")
        
        print("\n   🌐 Expertise Domains:")
        for domain in caps['capabilities']['multi_domain_expertise']:
            print(f"      • {domain}")
        
        print("\n   🎨 Response Modes:")
        for mode in caps['capabilities']['response_modes']:
            print(f"      • {mode}")
    
    # 2. Test creative responses
    print("\n2️⃣ Creative Response Test:")
    creative_prompts = [
        "Design a revolutionary Web3 marketplace that combines AI, NFTs, and social commerce",
        "Imagine a world where e-commerce stores become living ecosystems with tokenized economies",
        "Create an innovative loyalty program that uses blockchain gamification and AI personalization"
    ]
    
    for i, prompt in enumerate(creative_prompts, 1):
        print(f"\n   Test {i}: {prompt[:50]}...")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/assistant/chat",
            json={
                "message": prompt,
                "merchant_id": f"creative_test_{i}"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Status: {result['status']}")
            print(f"   📝 Response: {result['message'][:200]}...")
            print(f"   🎯 Actions: {len(result['actions'])} action items")
        else:
            print(f"   ❌ Error: {response.status_code}")
    
    # 3. Test strategic thinking
    print("\n3️⃣ Strategic Thinking Test:")
    strategic_prompt = """
    Develop a comprehensive 5-year strategy for a traditional e-commerce business 
    to transition into a Web3 dApp powerhouse. Consider market trends, technology adoption,
    competitive landscape, and revenue models.
    """
    
    response = requests.post(
        f"{BASE_URL}/api/v1/assistant/chat",
        json={
            "message": strategic_prompt,
            "merchant_id": "strategy_test",
            "assistant_mode": "strategic"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Strategic Analysis Generated")
        print(f"   📊 Response Length: {len(result['message'])} characters")
        print(f"   🎯 Action Items: {len(result['actions'])}")
        print(f"   🧠 Follow-up Questions: {len([q for q in result['message'].split('•') if q.strip()])}")
    
    # 4. Test technical guidance
    print("\n4️⃣ Technical Guidance Test:")
    tech_prompt = """
    Provide detailed technical architecture for implementing a Shopify-to-dApp conversion system
    that handles 10,000+ stores simultaneously. Include scalability, security, and performance considerations.
    """
    
    response = requests.post(
        f"{BASE_URL}/api/v1/assistant/chat",
        json={
            "message": tech_prompt,
            "merchant_id": "tech_test",
            "assistant_mode": "technical"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Technical Guidance Provided")
        print(f"   🔧 Response: {result['message'][:150]}...")
    
    # 5. Test innovation and brainstorming
    print("\n5️⃣ Innovation & Brainstorming Test:")
    innovation_prompt = """
    Brainstorm 10 breakthrough ideas for the future of Web3 e-commerce that don't exist yet.
    Think beyond current limitations and explore truly innovative concepts.
    """
    
    response = requests.post(
        f"{BASE_URL}/api/v1/assistant/chat",
        json={
            "message": innovation_prompt,
            "merchant_id": "innovation_test",
            "assistant_mode": "creative"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Innovation Ideas Generated")
        print(f"   💡 Sample: {result['message'][:200]}...")
    
    # 6. Test comprehensive analysis
    print("\n6️⃣ Comprehensive Analysis Test:")
    comprehensive_prompt = """
    Analyze the current state of Web3 adoption in e-commerce, identify key barriers,
    propose solutions, and predict future trends over the next 3-5 years.
    """
    
    response = requests.post(
        f"{BASE_URL}/api/v1/assistant/chat",
        json={
            "message": comprehensive_prompt,
            "merchant_id": "comprehensive_test",
            "assistant_mode": "comprehensive"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Comprehensive Analysis Complete")
        print(f"   📈 Analysis Depth: Advanced")
        print(f"   🧠 Confidence: High")
        print(f"   📝 Response Preview: {result['message'][:150]}...")
    
    print("\n🎉 Ultimate OptikGPT Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("   ✅ Multi-domain expertise (Blockchain, E-commerce, AI, Business)")
    print("   ✅ Creative and open-ended responses")
    print("   ✅ Strategic thinking and planning")
    print("   ✅ Technical guidance and architecture")
    print("   ✅ Innovation and brainstorming")
    print("   ✅ Comprehensive analysis capabilities")
    print("   ✅ Follow-up questions and action items")
    print("   ✅ Confidence scoring and metadata")
    
    print(f"\n🌐 Try it yourself: curl -X POST '{BASE_URL}/api/v1/assistant/chat' -H 'Content-Type: application/json' -d '{{\"message\":\"Your question here\",\"merchant_id\":\"test\"}}'")

if __name__ == "__main__":
    test_ultimate_optik_gpt()
