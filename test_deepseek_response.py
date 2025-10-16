import asyncio
from app.core.deepseek_client import ChatDeepSeek
from langchain_core.messages import HumanMessage, SystemMessage

async def test_deepseek_detailed():
    chat = ChatDeepSeek()
    
    # Use the same prompt that the requirements agent uses
    system_prompt = """You are an expert business analyst and requirements engineer with 15+ years of experience in software development and enterprise architecture.

Your responsibilities:
1. Parse business requirements documents thoroughly and systematically
2. Extract and structure requirements into clear, actionable categories:
   - Business goals and objectives
   - Functional requirements (what the system should do)
   - Non-functional requirements (how the system should perform)
   - Constraints (budget, timeline, technology, regulatory)
   - Stakeholders and their specific concerns
3. Identify ambiguities, gaps, and missing information
4. Generate 5-10 clarifying questions, prioritized by importance and impact
5. Provide a confidence score (0.0-1.0) based on document clarity and completeness
6. Output structured JSON following the exact schema provided

Guidelines:
- Be thorough and systematic in your analysis
- Ask insightful, specific questions that will help clarify requirements
- Focus on business value and technical feasibility
- Consider scalability, security, and maintainability
- Identify potential risks and dependencies
- Ensure requirements are testable and measurable

Always output valid JSON wrapped in ```json code blocks. Be precise and comprehensive."""

    user_prompt = """Please analyze the following requirements document and extract structured requirements:

PROJECT: Handmade Crafts Marketplace

BUSINESS OVERVIEW:
We are launching an online marketplace for handmade crafts, connecting artisans with customers who appreciate unique, handcrafted items. The platform should support both individual sellers and small craft businesses.

BUSINESS GOALS:
- Launch a user-friendly marketplace for handmade crafts
- Support 10,000 concurrent users on the platform
- Enable artisans to showcase and sell their products
- Provide customers with a seamless shopping experience
- Generate revenue through commission-based model (5-10% per transaction)

FUNCTIONAL REQUIREMENTS:
- User registration and authentication system
- Product listing and management for sellers
- Shopping cart and checkout functionality
- Payment processing integration
- Order management and tracking
- Review and rating system
- Search and filtering capabilities
- Mobile-responsive design

NON-FUNCTIONAL REQUIREMENTS:
- Platform should handle 10,000 concurrent users
- Page load times under 3 seconds
- 99.9% uptime availability
- Secure payment processing (PCI compliance)
- Mobile-responsive design
- Scalable architecture to support growth

CONSTRAINTS:
- Budget: $50,000 for initial development
- Timeline: 6 months to launch
- Technology: Prefer cloud-native solutions
- Team: 3 developers, 1 designer, 1 product manager

STAKEHOLDERS:
- Artisans (sellers)
- Customers (buyers)
- Platform administrators
- Payment processors

Please provide a structured analysis in JSON format."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    try:
        response = await chat.ainvoke(messages)
        print('=== DEEPSEEK RESPONSE ===')
        print(response.content)
        print('=== END RESPONSE ===')
    except Exception as e:
        print('Error:', e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deepseek_detailed())
