'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/src/contexts/AuthContext';
import { 
  BuildingIcon,
  SearchIcon,
  LinkIcon,
  ArrowRightIcon,
  SparklesIcon,
  ClockIcon,
  CheckCircleIcon,
  FileTextIcon,
  GithubIcon,
  ZapIcon,
  ShieldIcon,
  GlobeIcon,
  UsersIcon,
  BrainIcon
} from 'lucide-react';

export default function HomePage() {
  const { isAuthenticated } = useAuth();

  const architectOptions = [
    {
      id: 'new-architecture',
      title: 'Design New Architecture',
      description: 'Create a complete system architecture from requirements',
      icon: <BuildingIcon className="h-8 w-8" />,
      color: 'bg-blue-500',
      gradient: 'from-blue-500 to-blue-600',
      features: [
        'Requirements Analysis',
        'Architecture Design',
        'Technology Stack Selection',
        'C4 Diagrams Generation',
        'Best Practice Recommendations'
      ],
      timeEstimate: '5-15 minutes',
      complexity: 'Medium',
      link: '/architecture/new'
    },
    {
      id: 'evaluate-existing',
      title: 'Evaluate Existing Architecture',
      description: 'Analyze and improve your current system design',
      icon: <SearchIcon className="h-8 w-8" />,
      color: 'bg-purple-500',
      gradient: 'from-purple-500 to-purple-600',
      features: [
        'Architecture Assessment',
        'Issue Identification',
        'Improvement Recommendations',
        'Performance Analysis',
        'Security Review'
      ],
      timeEstimate: '10-20 minutes',
      complexity: 'Medium',
      link: '/architecture/evaluate'
    },
    {
      id: 'integration-planning',
      title: 'Plan System Integration',
      description: 'Design integration strategies for existing systems',
      icon: <LinkIcon className="h-8 w-8" />,
      color: 'bg-green-500',
      gradient: 'from-green-500 to-green-600',
      features: [
        'Integration Analysis',
        'Migration Strategy',
        'API Design',
        'Data Flow Planning',
        'Risk Assessment'
      ],
      timeEstimate: '15-30 minutes',
      complexity: 'High',
      link: '/architecture/integrate'
    }
  ];

  const quickStartSteps = [
    {
      step: 1,
      title: 'Choose Your Task',
      description: 'Select what you need help with - new architecture, evaluation, or integration',
      icon: <BrainIcon className="h-6 w-6" />
    },
    {
      step: 2,
      title: 'Provide Input',
      description: 'Upload documents, describe requirements, or connect to existing systems',
      icon: <FileTextIcon className="h-6 w-6" />
    },
    {
      step: 3,
      title: 'Get AI Guidance',
      description: 'Receive intelligent recommendations, diagrams, and implementation plans',
      icon: <SparklesIcon className="h-6 w-6" />
    },
    {
      step: 4,
      title: 'Export & Share',
      description: 'Download architecture documents, diagrams, and implementation guides',
      icon: <BuildingIcon className="h-6 w-6" />
    }
  ];

  const keyBenefits = [
    {
      icon: <ZapIcon className="h-6 w-6" />,
      title: 'Fast Results',
      description: 'Get architecture guidance in minutes, not hours',
      color: 'text-blue-600'
    },
    {
      icon: <ShieldIcon className="h-6 w-6" />,
      title: 'Best Practices',
      description: 'Built-in patterns and proven architectural approaches',
      color: 'text-green-600'
    },
    {
      icon: <GlobeIcon className="h-6 w-6" />,
      title: 'Multiple Formats',
      description: 'C4 diagrams, sequence diagrams, and comprehensive documentation',
      color: 'text-purple-600'
    },
    {
      icon: <UsersIcon className="h-6 w-6" />,
      title: 'Team Collaboration',
      description: 'Share and collaborate on architecture decisions',
      color: 'text-orange-600'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10"></div>
        <div className="relative container mx-auto px-4 py-20">
          <div className="text-center max-w-4xl mx-auto">
            <div className="flex items-center justify-center mb-6">
              <SparklesIcon className="h-12 w-12 text-blue-600 mr-3" />
              <h1 className="text-5xl font-bold text-slate-900">
                ArchMesh
              </h1>
            </div>
            <p className="text-xl text-slate-600 mb-8 leading-relaxed">
              AI-powered architecture guidance for software architects. Get intelligent recommendations, 
              generate diagrams, and create implementation plans in minutes.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {!isAuthenticated && (
                <>
                  <Link href="/register">
                    <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3">
                      Get Started Free
                      <ArrowRightIcon className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>
                  <Link href="/login">
                    <Button size="lg" variant="outline" className="px-8 py-3">
                      Sign In
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-16">
        {/* Main Options Section */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">What do you need help with?</h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Choose your architecture task and get AI-powered guidance tailored to your needs
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {architectOptions.map((option) => (
              <Card 
                key={option.id} 
                className="group hover:shadow-2xl transition-all duration-300 cursor-pointer border-0 shadow-lg hover:scale-105"
              >
                <CardHeader className="text-center pb-4">
                  <div className={`mx-auto w-16 h-16 ${option.color} rounded-full flex items-center justify-center mb-4 text-white group-hover:scale-110 transition-transform`}>
                    {option.icon}
                  </div>
                  <CardTitle className="text-xl text-slate-900">{option.title}</CardTitle>
                  <CardDescription className="text-slate-600 leading-relaxed">
                    {option.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center text-slate-500">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      {option.timeEstimate}
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {option.complexity}
                    </Badge>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-sm mb-2 text-slate-700">What you'll get:</h4>
                    <ul className="text-sm text-slate-600 space-y-1">
                      {option.features.map((feature, index) => (
                        <li key={index} className="flex items-center">
                          <CheckCircleIcon className="h-3 w-3 text-green-500 mr-2" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <Link href={option.link}>
                    <Button 
                      className={`w-full bg-gradient-to-r ${option.gradient} hover:opacity-90 text-white`}
                      size="lg"
                    >
                      Start {option.title.split(' ')[0]}
                      <ArrowRightIcon className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* How It Works Section */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">How It Works</h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Get architecture guidance in 4 simple steps
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-4">
            {quickStartSteps.map((step, index) => (
              <div key={step.step} className="text-center">
                <div className="relative">
                  <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4 text-blue-600">
                    {step.icon}
                  </div>
                  {index < quickStartSteps.length - 1 && (
                    <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-blue-200 -translate-x-1/2"></div>
                  )}
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">{step.title}</h3>
                <p className="text-slate-600 text-sm">{step.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Key Benefits Section */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Why Choose ArchMesh?</h2>
            <p className="text-xl text-slate-600">Built specifically for software architects</p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {keyBenefits.map((benefit, index) => (
              <Card key={index} className="text-center border-0 shadow-md hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className={`mx-auto w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center mb-3 ${benefit.color}`}>
                    {benefit.icon}
                  </div>
                  <CardTitle className="text-lg">{benefit.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-600">{benefit.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Architecture Patterns Preview */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Built-in Architecture Patterns</h2>
            <p className="text-xl text-slate-600">Access proven patterns and best practices</p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            <Card className="border-0 shadow-md">
              <CardHeader>
                <div className="flex items-center mb-2">
                  <BuildingIcon className="h-6 w-6 text-blue-600 mr-2" />
                  <CardTitle className="text-lg">Microservices</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 mb-3">
                  Service decomposition, API design, and communication patterns
                </p>
                <div className="flex flex-wrap gap-1">
                  <Badge variant="secondary" className="text-xs">Service Mesh</Badge>
                  <Badge variant="secondary" className="text-xs">API Gateway</Badge>
                  <Badge variant="secondary" className="text-xs">Event-Driven</Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-md">
              <CardHeader>
                <div className="flex items-center mb-2">
                  <GlobeIcon className="h-6 w-6 text-green-600 mr-2" />
                  <CardTitle className="text-lg">Cloud Native</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 mb-3">
                  Container orchestration, scalability, and cloud best practices
                </p>
                <div className="flex flex-wrap gap-1">
                  <Badge variant="secondary" className="text-xs">Kubernetes</Badge>
                  <Badge variant="secondary" className="text-xs">Serverless</Badge>
                  <Badge variant="secondary" className="text-xs">CI/CD</Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-md">
              <CardHeader>
                <div className="flex items-center mb-2">
                  <ShieldIcon className="h-6 w-6 text-purple-600 mr-2" />
                  <CardTitle className="text-lg">Enterprise</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 mb-3">
                  Security, compliance, and enterprise integration patterns
                </p>
                <div className="flex flex-wrap gap-1">
                  <Badge variant="secondary" className="text-xs">Security</Badge>
                  <Badge variant="secondary" className="text-xs">Compliance</Badge>
                  <Badge variant="secondary" className="text-xs">Integration</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of architects using AI-powered guidance for better system design
          </p>
          {isAuthenticated ? (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/architecture/new">
                <Button size="lg" variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3">
                  <BuildingIcon className="mr-2 h-5 w-5" />
                  Design New Architecture
                </Button>
              </Link>
              <Link href="/architecture/evaluate">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3">
                  <SearchIcon className="mr-2 h-5 w-5" />
                  Evaluate Existing
                </Button>
              </Link>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/register">
                <Button size="lg" variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3">
                  <SparklesIcon className="mr-2 h-5 w-5" />
                  Start Free Trial
                </Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3">
                  Sign In
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}