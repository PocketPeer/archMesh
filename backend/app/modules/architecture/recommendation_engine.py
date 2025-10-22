"""
Recommendation Engine - Simple component for generating recommendations
"""

from typing import List
from .models import Architecture, Recommendation, Priority


class RecommendationEngine:
    """
    Simple recommendation engine that generates recommendations from architecture.
    
    Single responsibility: Generate recommendations from architecture
    """
    
    def __init__(self):
        # Simple recommendation templates
        self.recommendation_templates = [
            {
                "title": "Implement API Gateway",
                "description": "Add an API gateway for centralized request handling, authentication, and rate limiting",
                "priority": Priority.HIGH,
                "impact": "Improved security and scalability",
                "effort": "2-3 weeks",
                "cost": "Medium",
                "rationale": "Centralized API management improves security and makes the system more maintainable"
            },
            {
                "title": "Add Monitoring and Logging",
                "description": "Implement comprehensive monitoring and logging for system observability",
                "priority": Priority.HIGH,
                "impact": "Better system reliability and debugging",
                "effort": "1-2 weeks",
                "cost": "Low",
                "rationale": "Monitoring is essential for production systems to ensure reliability"
            },
            {
                "title": "Implement Caching Strategy",
                "description": "Add caching layer to improve performance and reduce database load",
                "priority": Priority.MEDIUM,
                "impact": "Improved performance and reduced costs",
                "effort": "1-2 weeks",
                "cost": "Low",
                "rationale": "Caching can significantly improve system performance"
            },
            {
                "title": "Add Load Balancing",
                "description": "Implement load balancing for high availability and scalability",
                "priority": Priority.MEDIUM,
                "impact": "Improved scalability and availability",
                "effort": "1 week",
                "cost": "Medium",
                "rationale": "Load balancing is essential for scalable systems"
            },
            {
                "title": "Implement Security Measures",
                "description": "Add comprehensive security measures including authentication, authorization, and data encryption",
                "priority": Priority.HIGH,
                "impact": "Enhanced security and compliance",
                "effort": "2-4 weeks",
                "cost": "Medium",
                "rationale": "Security is critical for any production system"
            }
        ]
    
    def generate(self, architecture: Architecture) -> List[Recommendation]:
        """
        Generate recommendations from architecture.
        
        Args:
            architecture: Architecture to analyze
            
        Returns:
            List[Recommendation]: Generated recommendations
        """
        recommendations = []
        
        # Analyze architecture and generate relevant recommendations
        for template in self.recommendation_templates:
            if self._should_recommend(template, architecture):
                recommendation = Recommendation(
                    id=f"rec_{len(recommendations) + 1}",
                    title=template["title"],
                    description=template["description"],
                    priority=template["priority"],
                    impact=template["impact"],
                    effort=template["effort"],
                    cost=template["cost"],
                    rationale=template["rationale"]
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _should_recommend(self, template: dict, architecture: Architecture) -> bool:
        """Simple logic to determine if a recommendation should be included"""
        title = template["title"].lower()
        
        # API Gateway recommendation
        if "api gateway" in title:
            # Recommend if no API gateway exists and we have multiple services
            has_gateway = any(comp.type.value == "api_gateway" for comp in architecture.components)
            has_multiple_services = len([comp for comp in architecture.components if comp.type.value == "service"]) > 1
            return not has_gateway and has_multiple_services
        
        # Monitoring recommendation
        elif "monitoring" in title:
            # Always recommend monitoring
            return True
        
        # Caching recommendation
        elif "caching" in title:
            # Recommend if no cache exists and we have database
            has_cache = any(comp.type.value == "cache" for comp in architecture.components)
            has_database = any(comp.type.value == "database" for comp in architecture.components)
            return not has_cache and has_database
        
        # Load balancing recommendation
        elif "load balancing" in title:
            # Recommend if no load balancer exists and we have multiple components
            has_load_balancer = any(comp.type.value == "load_balancer" for comp in architecture.components)
            has_multiple_components = len(architecture.components) > 3
            return not has_load_balancer and has_multiple_components
        
        # Security recommendation
        elif "security" in title:
            # Always recommend security
            return True
        
        # Default: recommend if architecture quality is low
        return architecture.quality_score < 0.7
