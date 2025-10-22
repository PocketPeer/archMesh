'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  LightbulbIcon, 
  CheckCircleIcon, 
  ArrowRightIcon,
  BuildingIcon,
  ZapIcon,
  ShieldIcon,
  BarChart3Icon
} from 'lucide-react';
import { toast } from 'sonner';

interface Recommendation {
  id: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  impact: string;
  architectureChanges: string[];
  plantUMLCode?: string;
}

interface RecommendationSelectorProps {
  recommendations: Recommendation[];
  onRecommendationsChange: (selectedIds: string[], updatedDiagrams: any[], updatedMetrics: any) => void;
}

export default function RecommendationSelector({ 
  recommendations, 
  onRecommendationsChange 
}: RecommendationSelectorProps) {
  const [selectedRecommendations, setSelectedRecommendations] = useState<string[]>([]);
  const [isApplying, setIsApplying] = useState(false);

  const handleRecommendationToggle = (recommendationId: string) => {
    const newSelected = selectedRecommendations.includes(recommendationId)
      ? selectedRecommendations.filter(id => id !== recommendationId)
      : [...selectedRecommendations, recommendationId];
    
    setSelectedRecommendations(newSelected);
  };

  const handleApplyRecommendations = async () => {
    if (selectedRecommendations.length === 0) {
      toast.error('Please select at least one recommendation');
      return;
    }

    setIsApplying(true);
    
    try {
      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Get selected recommendations
      const selected = recommendations.filter(rec => selectedRecommendations.includes(rec.id));
      
      // Generate updated diagrams based on selected recommendations
      const updatedDiagrams = generateUpdatedDiagrams(selected);
      
      // Generate updated metrics based on applied recommendations
      const updatedMetrics = generateUpdatedMetrics(selected);
      
      // Notify parent component with updated data
      onRecommendationsChange(selectedRecommendations, updatedDiagrams, updatedMetrics);
      
      // Clear selected recommendations (they're now applied)
      setSelectedRecommendations([]);
      
      toast.success(`Applied ${selectedRecommendations.length} recommendations to architecture`);
    } catch (error) {
      console.error('Error applying recommendations:', error);
      toast.error('Failed to apply recommendations');
    } finally {
      setIsApplying(false);
    }
  };

  const generateUpdatedDiagrams = (selectedRecommendations: Recommendation[]) => {
    // This would integrate with AI to generate updated PlantUML diagrams
    // For now, we'll return enhanced versions of the base diagrams
    
    const baseContextDiagram = `@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "User", "End user of the system")
System(system, "E-commerce Platform", "Online shopping platform")

Rel(user, system, "Uses")
@enduml`;

    const baseContainerDiagram = `@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(user, "User", "End user")
System_Boundary(system, "E-commerce Platform") {
  Container(api, "API Gateway", "Kong", "Routes requests")
  Container(userService, "User Service", "Node.js", "User management")
  Container(productService, "Product Service", "Python", "Product catalog")
  ContainerDb(database, "Database", "PostgreSQL", "Data storage")
}

Rel(user, api, "Uses")
Rel(api, userService, "Routes to")
Rel(api, productService, "Routes to")
Rel(userService, database, "Stores data in")
Rel(productService, database, "Stores data in")
@enduml`;

    // Enhance diagrams based on selected recommendations
    let enhancedContainerDiagram = baseContainerDiagram;
    
    selectedRecommendations.forEach(rec => {
      if (rec.title.includes('API Gateway')) {
        enhancedContainerDiagram = enhancedContainerDiagram.replace(
          'Container(api, "API Gateway", "Kong", "Routes requests")',
          'Container(api, "API Gateway", "Kong", "Routes requests, Rate limiting, Authentication")'
        );
      }
      
      if (rec.title.includes('Monitoring')) {
        enhancedContainerDiagram = enhancedContainerDiagram.replace(
          'ContainerDb(database, "Database", "PostgreSQL", "Data storage")',
          `ContainerDb(database, "Database", "PostgreSQL", "Data storage")
  Container(monitoring, "Monitoring", "Prometheus", "System monitoring")
  Container(logging, "Logging", "ELK Stack", "Centralized logging")`
        );
      }
      
      if (rec.title.includes('Caching')) {
        enhancedContainerDiagram = enhancedContainerDiagram.replace(
          'Container(productService, "Product Service", "Python", "Product catalog")',
          `Container(productService, "Product Service", "Python", "Product catalog")
  ContainerDb(cache, "Cache", "Redis", "High-speed data caching")`
        );
      }
    });

    return [
      {
        type: 'C4 Context',
        title: 'System Context',
        description: 'High-level view of the system and its users',
        code: baseContextDiagram
      },
      {
        type: 'C4 Container',
        title: 'Container Diagram',
        description: 'Architecture of the system showing containers',
        code: enhancedContainerDiagram
      }
    ];
  };

  const generateUpdatedMetrics = (selectedRecommendations: Recommendation[]) => {
    // Calculate updated metrics based on applied recommendations
    let complexityIncrease = 0;
    let costIncrease = 0;
    let timeIncrease = 0;
    let maintenanceIncrease = 0;

    selectedRecommendations.forEach(rec => {
      if (rec.title.includes('API Gateway')) {
        complexityIncrease += 1;
        costIncrease += 15000;
        timeIncrease += 1;
        maintenanceIncrease += 0.5;
      }
      
      if (rec.title.includes('Monitoring')) {
        complexityIncrease += 2;
        costIncrease += 10000;
        timeIncrease += 2;
        maintenanceIncrease += 1;
      }
      
      if (rec.title.includes('Caching')) {
        complexityIncrease += 1;
        costIncrease += 5000;
        timeIncrease += 1;
        maintenanceIncrease += 0.5;
      }
    });

    return {
      complexity: complexityIncrease > 2 ? 'High' : complexityIncrease > 0 ? 'Medium' : 'Low',
      estimatedCost: `$${50000 + costIncrease} - $${75000 + costIncrease}`,
      developmentTime: `${7 + timeIncrease}-${10 + timeIncrease} weeks`,
      maintenanceEffort: `${2 + maintenanceIncrease}-${3 + maintenanceIncrease} developers`
    };
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <ZapIcon className="h-4 w-4" />;
      case 'medium': return <ShieldIcon className="h-4 w-4" />;
      case 'low': return <BarChart3Icon className="h-4 w-4" />;
      default: return <BuildingIcon className="h-4 w-4" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <LightbulbIcon className="h-5 w-5 mr-2 text-yellow-600" />
          Select Recommendations to Apply
        </CardTitle>
        <CardDescription>
          Choose which recommendations to integrate into your architecture. 
          Selected recommendations will update the system diagrams automatically.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recommendations.map((rec) => (
            <div 
              key={rec.id}
              className={`border rounded-lg p-4 transition-all ${
                selectedRecommendations.includes(rec.id) 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex items-start space-x-3">
                <Checkbox
                  id={rec.id}
                  checked={selectedRecommendations.includes(rec.id)}
                  onCheckedChange={() => handleRecommendationToggle(rec.id)}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">{rec.title}</h4>
                    <Badge className={getPriorityColor(rec.priority)}>
                      <div className="flex items-center">
                        {getPriorityIcon(rec.priority)}
                        <span className="ml-1">{rec.priority.toUpperCase()}</span>
                      </div>
                    </Badge>
                  </div>
                  <p className="text-sm text-slate-600 mb-2">{rec.description}</p>
                  <p className="text-xs text-slate-500 mb-2">Impact: {rec.impact}</p>
                  {rec.architectureChanges.length > 0 && (
                    <div className="text-xs text-slate-500">
                      <span className="font-medium">Architecture Changes:</span>
                      <ul className="list-disc list-inside mt-1">
                        {rec.architectureChanges.map((change, index) => (
                          <li key={index}>{change}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {selectedRecommendations.length > 0 && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-blue-900">
                  {selectedRecommendations.length} recommendation{selectedRecommendations.length > 1 ? 's' : ''} selected
                </h4>
                <p className="text-sm text-blue-700">
                  These will be integrated into your architecture diagrams
                </p>
              </div>
              <Button 
                onClick={handleApplyRecommendations}
                disabled={isApplying}
                className="min-w-[140px]"
              >
                {isApplying ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Applying...
                  </>
                ) : (
                  <>
                    <CheckCircleIcon className="h-4 w-4 mr-2" />
                    Apply Changes
                    <ArrowRightIcon className="h-4 w-4 ml-2" />
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
