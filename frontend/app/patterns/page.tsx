'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeftIcon,
  SearchIcon,
  BuildingIcon,
  GlobeIcon,
  DatabaseIcon,
  ShieldIcon,
  ZapIcon,
  UsersIcon,
  ClockIcon,
  CheckCircleIcon,
  StarIcon,
  BookOpenIcon,
  CodeIcon,
  EyeIcon,
  CopyIcon
} from 'lucide-react';
import { useRouter } from 'next/navigation';

interface ArchitecturePattern {
  id: string;
  name: string;
  category: string;
  description: string;
  problem: string;
  solution: string;
  benefits: string[];
  tradeoffs: string[];
  useCases: string[];
  complexity: 'Low' | 'Medium' | 'High';
  maturity: 'Established' | 'Emerging' | 'Experimental';
  technologies: string[];
  diagram: string;
  codeExample: string;
  bestPractices: string[];
  antiPatterns: string[];
  relatedPatterns: string[];
}

const patterns: ArchitecturePattern[] = [
  {
    id: 'microservices',
    name: 'Microservices',
    category: 'Decomposition',
    description: 'Decompose application into small, independent services that communicate over well-defined APIs',
    problem: 'Monolithic applications become difficult to maintain, scale, and deploy as they grow',
    solution: 'Break down the application into small, loosely coupled services that can be developed, deployed, and scaled independently',
    benefits: ['Independent deployment', 'Technology diversity', 'Fault isolation', 'Team autonomy', 'Scalability'],
    tradeoffs: ['Increased complexity', 'Network latency', 'Data consistency challenges', 'Operational overhead'],
    useCases: ['Large applications', 'Multiple teams', 'Different technology needs', 'High scalability requirements'],
    complexity: 'High',
    maturity: 'Established',
    technologies: ['Docker', 'Kubernetes', 'Service Mesh', 'API Gateway', 'Event Streaming'],
    diagram: '@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n\nSystem_Boundary(microservices, "Microservices Architecture") {\n  Container(api, "API Gateway", "Kong", "Routes requests")\n  Container(userService, "User Service", "Node.js", "User management")\n  Container(orderService, "Order Service", "Java", "Order processing")\n  Container(paymentService, "Payment Service", "Python", "Payment processing")\n  ContainerDb(database, "Database", "PostgreSQL", "Data storage")\n}\n\nRel(api, userService, "Routes to")\nRel(api, orderService, "Routes to")\nRel(api, paymentService, "Routes to")\nRel(userService, database, "Stores data in")\nRel(orderService, database, "Stores data in")\nRel(paymentService, database, "Stores data in")\n@enduml',
    codeExample: '// User Service API\napp.get(\'/api/users/:id\', async (req, res) => {\n  try {\n    const user = await userService.getUser(req.params.id);\n    res.json(user);\n  } catch (error) {\n    res.status(500).json({ error: \'User service unavailable\' });\n  }\n});\n\n// Order Service API\napp.post(\'/api/orders\', async (req, res) => {\n  try {\n    const order = await orderService.createOrder(req.body);\n    res.json(order);\n  } catch (error) {\n    res.status(500).json({ error: \'Order service unavailable\' });\n  }\n});',
    bestPractices: ['Design for failure', 'Implement circuit breakers', 'Use API versioning', 'Implement distributed tracing', 'Design for observability'],
    antiPatterns: ['Distributed monolith', 'Shared database', 'Tight coupling', 'Synchronous communication everywhere'],
    relatedPatterns: ['API Gateway', 'Event-Driven Architecture', 'Service Mesh', 'CQRS']
  },
  {
    id: 'api-gateway',
    name: 'API Gateway',
    category: 'Integration',
    description: 'Single entry point for all client requests to microservices',
    problem: 'Clients need to know about multiple services and handle different protocols',
    solution: 'Provide a single entry point that routes requests to appropriate services',
    benefits: ['Centralized routing', 'Authentication', 'Rate limiting', 'Request/response transformation'],
    tradeoffs: ['Single point of failure', 'Potential bottleneck', 'Additional complexity'],
    useCases: ['Microservices architecture', 'Multiple client types', 'Cross-cutting concerns'],
    complexity: 'Medium',
    maturity: 'Established',
    technologies: ['Kong', 'NGINX', 'AWS API Gateway', 'Azure API Management', 'Kong'],
    diagram: '@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n\nPerson(client, "Client", "Mobile/Web application")\nSystem_Boundary(gateway, "API Gateway") {\n  Container(gateway, "API Gateway", "Kong", "Routes and manages requests")\n}\nSystem_Boundary(services, "Microservices") {\n  Container(userService, "User Service", "Node.js", "User management")\n  Container(orderService, "Order Service", "Java", "Order processing")\n}\n\nRel(client, gateway, "Makes requests")\nRel(gateway, userService, "Routes to")\nRel(gateway, orderService, "Routes to")\n@enduml',
    codeExample: '// Kong configuration\nservices:\n  - name: user-service\n    url: http://user-service:3000\n    routes:\n      - name: user-route\n        paths:\n          - /api/users\n        plugins:\n          - name: rate-limiting\n            config:\n              minute: 100\n          - name: jwt\n            config:\n              secret: your-secret-key',
    bestPractices: ['Implement rate limiting', 'Use authentication', 'Monitor performance', 'Version APIs', 'Handle failures gracefully'],
    antiPatterns: ['Business logic in gateway', 'No authentication', 'No rate limiting', 'Tight coupling'],
    relatedPatterns: ['Microservices', 'Service Mesh', 'Backend for Frontend', 'Circuit Breaker']
  },
  {
    id: 'event-driven',
    name: 'Event-Driven Architecture',
    category: 'Communication',
    description: 'Services communicate through events rather than direct calls',
    problem: 'Synchronous communication creates tight coupling and scalability issues',
    solution: 'Use events to decouple services and enable asynchronous communication',
    benefits: ['Loose coupling', 'Scalability', 'Resilience', 'Flexibility'],
    tradeoffs: ['Eventual consistency', 'Complex debugging', 'Message ordering challenges'],
    useCases: ['Real-time systems', 'High throughput', 'Distributed systems', 'Integration scenarios'],
    complexity: 'High',
    maturity: 'Established',
    technologies: ['Apache Kafka', 'RabbitMQ', 'AWS SNS/SQS', 'Azure Service Bus', 'Redis Streams'],
    diagram: '@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n\nSystem_Boundary(eventDriven, "Event-Driven Architecture") {\n  Container(orderService, "Order Service", "Java", "Publishes events")\n  Container(inventoryService, "Inventory Service", "Python", "Subscribes to events")\n  Container(notificationService, "Notification Service", "Node.js", "Subscribes to events")\n  ContainerDb(messageBroker, "Message Broker", "Kafka", "Event streaming")\n}\n\nRel(orderService, messageBroker, "Publishes events")\nRel(messageBroker, inventoryService, "Delivers events")\nRel(messageBroker, notificationService, "Delivers events")\n@enduml',
    codeExample: '// Order Service - Event Publisher\nclass OrderService {\n  async createOrder(orderData) {\n    const order = await this.saveOrder(orderData);\n    \n    // Publish event\n    await this.eventBus.publish(\'order.created\', {\n      orderId: order.id,\n      customerId: order.customerId,\n      total: order.total\n    });\n    \n    return order;\n  }\n}\n\n// Inventory Service - Event Subscriber\nclass InventoryService {\n  async handleOrderCreated(event) {\n    await this.reserveInventory(event.orderId, event.items);\n  }\n}',
    bestPractices: ['Design for failure', 'Use idempotent handlers', 'Implement event sourcing', 'Monitor event flow', 'Handle duplicate events'],
    antiPatterns: ['Synchronous event handling', 'No event versioning', 'Tight coupling through events', 'No error handling'],
    relatedPatterns: ['Microservices', 'CQRS', 'Event Sourcing', 'Saga Pattern']
  },
  {
    id: 'cqrs',
    name: 'CQRS (Command Query Responsibility Segregation)',
    category: 'Data',
    description: 'Separate read and write operations into different models',
    problem: 'Single data model creates complexity when read and write requirements differ',
    solution: 'Use separate models for reading and writing data',
    benefits: ['Optimized read/write', 'Scalability', 'Flexibility', 'Performance'],
    tradeoffs: ['Increased complexity', 'Data consistency challenges', 'More moving parts'],
    useCases: ['High read/write ratio', 'Complex queries', 'Different data models needed', 'Performance critical'],
    complexity: 'High',
    maturity: 'Established',
    technologies: ['Event Store', 'Read Models', 'Command Handlers', 'Query Handlers', 'Event Sourcing'],
    diagram: '@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n\nSystem_Boundary(cqrs, "CQRS Architecture") {\n  Container(commandSide, "Command Side", "Java", "Handles writes")\n  Container(querySide, "Query Side", "Node.js", "Handles reads")\n  ContainerDb(writeDb, "Write Database", "PostgreSQL", "Command storage")\n  ContainerDb(readDb, "Read Database", "MongoDB", "Query optimization")\n}\n\nRel(commandSide, writeDb, "Writes to")\nRel(querySide, readDb, "Reads from")\nRel(writeDb, readDb, "Syncs data")\n@enduml',
    codeExample: '// Command Handler\nclass CreateUserCommandHandler {\n  async handle(command) {\n    const user = new User(command.name, command.email);\n    await this.userRepository.save(user);\n    \n    // Publish event for read model\n    await this.eventBus.publish(\'user.created\', user);\n  }\n}\n\n// Query Handler\nclass GetUserQueryHandler {\n  async handle(query) {\n    return await this.userReadModel.find(query.userId);\n  }\n}',
    bestPractices: ['Keep read/write models in sync', 'Use eventual consistency', 'Implement proper error handling', 'Monitor data consistency', 'Use event sourcing'],
    antiPatterns: ['Synchronous read/write sync', 'No event handling', 'Tight coupling between sides', 'No consistency monitoring'],
    relatedPatterns: ['Event Sourcing', 'Event-Driven Architecture', 'Microservices', 'Saga Pattern']
  },
  {
    id: 'saga',
    name: 'Saga Pattern',
    category: 'Transaction',
    description: 'Manage distributed transactions across multiple services',
    problem: 'Distributed transactions are complex and don\'t scale well',
    solution: 'Use a sequence of local transactions with compensating actions',
    benefits: ['Scalability', 'Resilience', 'Flexibility', 'Performance'],
    tradeoffs: ['Complexity', 'Eventual consistency', 'Compensation logic needed'],
    useCases: ['Distributed transactions', 'Long-running processes', 'Microservices coordination', 'Business workflows'],
    complexity: 'High',
    maturity: 'Established',
    technologies: ['Event Sourcing', 'State Machines', 'Message Brokers', 'Workflow Engines'],
    diagram: '@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n\nSystem_Boundary(saga, "Saga Pattern") {\n  Container(sagaOrchestrator, "Saga Orchestrator", "Java", "Coordinates transactions")\n  Container(orderService, "Order Service", "Node.js", "Order management")\n  Container(paymentService, "Payment Service", "Python", "Payment processing")\n  Container(inventoryService, "Inventory Service", "Java", "Inventory management")\n}\n\nRel(sagaOrchestrator, orderService, "Creates order")\nRel(sagaOrchestrator, paymentService, "Processes payment")\nRel(sagaOrchestrator, inventoryService, "Reserves inventory")\n@enduml',
    codeExample: '// Saga Orchestrator\nclass OrderSaga {\n  async execute(orderData) {\n    try {\n      // Step 1: Create order\n      const order = await this.orderService.createOrder(orderData);\n      \n      // Step 2: Process payment\n      const payment = await this.paymentService.processPayment(order.id, orderData.payment);\n      \n      // Step 3: Reserve inventory\n      await this.inventoryService.reserveInventory(order.id, orderData.items);\n      \n      return order;\n    } catch (error) {\n      // Compensate for failures\n      await this.compensate(order.id);\n      throw error;\n    }\n  }\n  \n  async compensate(orderId) {\n    // Reverse all operations\n    await this.inventoryService.releaseInventory(orderId);\n    await this.paymentService.refundPayment(orderId);\n    await this.orderService.cancelOrder(orderId);\n  }\n}',
    bestPractices: ['Design for compensation', 'Use idempotent operations', 'Implement proper error handling', 'Monitor saga execution', 'Use timeouts'],
    antiPatterns: ['No compensation logic', 'Synchronous compensation', 'No error handling', 'Tight coupling'],
    relatedPatterns: ['Event-Driven Architecture', 'CQRS', 'Microservices', 'Event Sourcing']
  },
  {
    id: 'circuit-breaker',
    name: 'Circuit Breaker',
    category: 'Resilience',
    description: 'Prevent cascading failures by stopping calls to failing services',
    problem: 'Failing services can cause cascading failures across the system',
    solution: 'Implement a circuit breaker that stops calls to failing services',
    benefits: ['Fault tolerance', 'Performance', 'Resilience', 'Quick failure detection'],
    tradeoffs: ['Complexity', 'Potential data loss', 'Service unavailability'],
    useCases: ['External service calls', 'Critical system dependencies', 'High availability requirements'],
    complexity: 'Medium',
    maturity: 'Established',
    technologies: ['Hystrix', 'Resilience4j', 'Polly', 'Istio', 'Envoy'],
    diagram: '@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n\nSystem_Boundary(circuitBreaker, "Circuit Breaker Pattern") {\n  Container(client, "Client Service", "Node.js", "Makes requests")\n  Container(circuitBreaker, "Circuit Breaker", "Middleware", "Monitors calls")\n  Container(service, "External Service", "API", "Target service")\n}\n\nRel(client, circuitBreaker, "Calls through")\nRel(circuitBreaker, service, "Monitors and calls")\n@enduml',
    codeExample: '// Circuit Breaker Implementation\nclass CircuitBreaker {\n  constructor(threshold = 5, timeout = 60000) {\n    this.failureThreshold = threshold;\n    this.timeout = timeout;\n    this.failureCount = 0;\n    this.lastFailureTime = null;\n    this.state = \'CLOSED\'; // CLOSED, OPEN, HALF_OPEN\n  }\n  \n  async call(fn) {\n    if (this.state === \'OPEN\') {\n      if (Date.now() - this.lastFailureTime > this.timeout) {\n        this.state = \'HALF_OPEN\';\n      } else {\n        throw new Error(\'Circuit breaker is OPEN\');\n      }\n    }\n    \n    try {\n      const result = await fn();\n      this.onSuccess();\n      return result;\n    } catch (error) {\n      this.onFailure();\n      throw error;\n    }\n  }\n  \n  onSuccess() {\n    this.failureCount = 0;\n    this.state = \'CLOSED\';\n  }\n  \n  onFailure() {\n    this.failureCount++;\n    this.lastFailureTime = Date.now();\n    \n    if (this.failureCount >= this.failureThreshold) {\n      this.state = \'OPEN\';\n    }\n  }\n}',
    bestPractices: ['Set appropriate thresholds', 'Implement fallback mechanisms', 'Monitor circuit state', 'Use timeouts', 'Test failure scenarios'],
    antiPatterns: ['No fallback mechanism', 'Inappropriate thresholds', 'No monitoring', 'Synchronous fallbacks'],
    relatedPatterns: ['Bulkhead', 'Retry Pattern', 'Timeout Pattern', 'Microservices']
  }
];

const categories = [
  { id: 'all', name: 'All Patterns', icon: <BuildingIcon className="h-4 w-4" /> },
  { id: 'Decomposition', name: 'Decomposition', icon: <GlobeIcon className="h-4 w-4" /> },
  { id: 'Integration', name: 'Integration', icon: <ZapIcon className="h-4 w-4" /> },
  { id: 'Communication', name: 'Communication', icon: <UsersIcon className="h-4 w-4" /> },
  { id: 'Data', name: 'Data', icon: <DatabaseIcon className="h-4 w-4" /> },
  { id: 'Transaction', name: 'Transaction', icon: <ShieldIcon className="h-4 w-4" /> },
  { id: 'Resilience', name: 'Resilience', icon: <CheckCircleIcon className="h-4 w-4" /> }
];

export default function PatternsPage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPattern, setSelectedPattern] = useState<ArchitecturePattern | null>(null);

  const filteredPatterns = patterns.filter(pattern => {
    const matchesSearch = pattern.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         pattern.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || pattern.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'Low': return 'bg-green-100 text-green-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'High': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getMaturityColor = (maturity: string) => {
    switch (maturity) {
      case 'Established': return 'bg-blue-100 text-blue-800';
      case 'Emerging': return 'bg-purple-100 text-purple-800';
      case 'Experimental': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Button variant="outline" onClick={() => router.push('/')}>
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center">
            <BookOpenIcon className="h-6 w-6 mr-2 text-blue-600" />
            Architecture Patterns Library
          </h1>
        </div>

        {/* Search and Filters */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search patterns..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <Button
                  key={category.id}
                  variant={selectedCategory === category.id ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(category.id)}
                  className="flex items-center gap-2"
                >
                  {category.icon}
                  {category.name}
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Patterns Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPatterns.map((pattern) => (
            <Card 
              key={pattern.id} 
              className="cursor-pointer hover:shadow-lg transition-all duration-300"
              onClick={() => setSelectedPattern(pattern)}
            >
              <CardHeader>
                <div className="flex items-center justify-between mb-2">
                  <CardTitle className="text-lg">{pattern.name}</CardTitle>
                  <div className="flex gap-2">
                    <Badge className={getComplexityColor(pattern.complexity)}>
                      {pattern.complexity}
                    </Badge>
                    <Badge className={getMaturityColor(pattern.maturity)}>
                      {pattern.maturity}
                    </Badge>
                  </div>
                </div>
                <CardDescription>{pattern.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <h4 className="font-medium text-sm mb-1">Benefits</h4>
                    <div className="flex flex-wrap gap-1">
                      {pattern.benefits.slice(0, 3).map((benefit, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {benefit}
                        </Badge>
                      ))}
                      {pattern.benefits.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{pattern.benefits.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-sm mb-1">Technologies</h4>
                    <div className="flex flex-wrap gap-1">
                      {pattern.technologies.slice(0, 3).map((tech, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {tech}
                        </Badge>
                      ))}
                      {pattern.technologies.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{pattern.technologies.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm text-slate-500">
                    <span>{pattern.category}</span>
                    <Button variant="ghost" size="sm">
                      <EyeIcon className="h-4 w-4 mr-1" />
                      View Details
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Pattern Detail Modal */}
        {selectedPattern && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-slate-900">{selectedPattern.name}</h2>
                  <Button variant="outline" onClick={() => setSelectedPattern(null)}>
                    Close
                  </Button>
                </div>

                <Tabs defaultValue="overview" className="space-y-6">
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="implementation">Implementation</TabsTrigger>
                    <TabsTrigger value="best-practices">Best Practices</TabsTrigger>
                    <TabsTrigger value="examples">Examples</TabsTrigger>
                  </TabsList>

                  <TabsContent value="overview" className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <Card>
                        <CardHeader>
                          <CardTitle>Problem</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-slate-700">{selectedPattern.problem}</p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle>Solution</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-slate-700">{selectedPattern.solution}</p>
                        </CardContent>
                      </Card>
                    </div>

                    <Card>
                      <CardHeader>
                        <CardTitle>Benefits & Tradeoffs</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="font-medium mb-2 text-green-700">Benefits</h4>
                            <ul className="space-y-1">
                              {selectedPattern.benefits.map((benefit, index) => (
                                <li key={index} className="flex items-center text-sm">
                                  <CheckCircleIcon className="h-3 w-3 text-green-500 mr-2" />
                                  {benefit}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <h4 className="font-medium mb-2 text-red-700">Tradeoffs</h4>
                            <ul className="space-y-1">
                              {selectedPattern.tradeoffs.map((tradeoff, index) => (
                                <li key={index} className="flex items-center text-sm">
                                  <AlertTriangleIcon className="h-3 w-3 text-red-500 mr-2" />
                                  {tradeoff}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Use Cases</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2">
                          {selectedPattern.useCases.map((useCase, index) => (
                            <Badge key={index} variant="outline">
                              {useCase}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="implementation" className="space-y-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Architecture Diagram</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="bg-slate-50 p-4 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium">PlantUML Code</span>
                            <Button variant="outline" size="sm">
                              <CopyIcon className="h-4 w-4 mr-1" />
                              Copy
                            </Button>
                          </div>
                          <pre className="text-xs font-mono overflow-x-auto">
                            {selectedPattern.diagram}
                          </pre>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Technologies</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2">
                          {selectedPattern.technologies.map((tech, index) => (
                            <Badge key={index} variant="secondary">
                              {tech}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="best-practices" className="space-y-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Best Practices</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {selectedPattern.bestPractices.map((practice, index) => (
                            <li key={index} className="flex items-start">
                              <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                              <span className="text-sm">{practice}</span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Anti-Patterns to Avoid</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {selectedPattern.antiPatterns.map((antiPattern, index) => (
                            <li key={index} className="flex items-start">
                              <AlertTriangleIcon className="h-4 w-4 text-red-500 mr-2 mt-0.5" />
                              <span className="text-sm">{antiPattern}</span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="examples" className="space-y-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Code Example</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="bg-slate-50 p-4 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium">Implementation Code</span>
                            <Button variant="outline" size="sm">
                              <CopyIcon className="h-4 w-4 mr-1" />
                              Copy
                            </Button>
                          </div>
                          <pre className="text-xs font-mono overflow-x-auto">
                            {selectedPattern.codeExample}
                          </pre>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Related Patterns</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2">
                          {selectedPattern.relatedPatterns.map((pattern, index) => (
                            <Badge key={index} variant="outline">
                              {pattern}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
