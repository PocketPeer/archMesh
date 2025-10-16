import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <div className="space-y-4">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-6xl">
            Transform Requirements into
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {" "}Architectures
            </span>
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-slate-600">
            ArchMesh uses AI agents to automatically parse business requirements 
            and generate comprehensive system architectures with human review gates.
          </p>
        </div>
        <div className="flex items-center justify-center gap-4">
          <Link href="/projects">
            <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              Get Started
            </Button>
          </Link>
          <Button variant="outline" size="lg">
            Learn More
          </Button>
        </div>
      </div>

      {/* Features Section */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <div className="h-12 w-12 rounded-lg bg-blue-100 flex items-center justify-center mb-4">
              <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <CardTitle>Smart Requirements Parsing</CardTitle>
            <CardDescription>
              AI agents extract structured requirements from business documents, 
              identifying gaps and generating clarifying questions.
            </CardDescription>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <div className="h-12 w-12 rounded-lg bg-purple-100 flex items-center justify-center mb-4">
              <svg className="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <CardTitle>Architecture Design</CardTitle>
            <CardDescription>
              Generate comprehensive system architectures with C4 diagrams, 
              technology stacks, and alternative solutions.
            </CardDescription>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <div className="h-12 w-12 rounded-lg bg-green-100 flex items-center justify-center mb-4">
              <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <CardTitle>Human Review Gates</CardTitle>
            <CardDescription>
              Built-in review points ensure human oversight and approval 
              at critical stages of the architecture process.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* Process Flow */}
      <div className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-slate-900">How It Works</h2>
          <p className="mt-2 text-slate-600">Simple 4-step process to transform your ideas into architectures</p>
        </div>
        
        <div className="grid gap-8 md:grid-cols-4">
          {[
            { step: "1", title: "Upload Document", description: "Upload your business requirements document" },
            { step: "2", title: "AI Analysis", description: "AI agents parse and structure requirements" },
            { step: "3", title: "Review & Approve", description: "Review extracted requirements and provide feedback" },
            { step: "4", title: "Generate Architecture", description: "AI designs comprehensive system architecture" },
          ].map((item, index) => (
            <div key={index} className="text-center space-y-4">
              <div className="mx-auto h-12 w-12 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center text-white font-bold">
                {item.step}
              </div>
              <div>
                <h3 className="font-semibold text-slate-900">{item.title}</h3>
                <p className="text-sm text-slate-600">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Supported Domains */}
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-slate-900">Supported Domains</h2>
          <p className="mt-2 text-slate-600">ArchMesh works across different architectural domains</p>
        </div>
        
        <div className="flex flex-wrap justify-center gap-4">
          <Badge variant="secondary" className="px-4 py-2 text-sm">
            Cloud-Native Applications
          </Badge>
          <Badge variant="secondary" className="px-4 py-2 text-sm">
            Data Platforms
          </Badge>
          <Badge variant="secondary" className="px-4 py-2 text-sm">
            Enterprise Systems
          </Badge>
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center space-y-6 py-12">
        <h2 className="text-3xl font-bold text-slate-900">Ready to Get Started?</h2>
        <p className="text-slate-600">
          Create your first project and upload a requirements document to see ArchMesh in action.
        </p>
        <Link href="/projects">
          <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
            Create Your First Project
          </Button>
        </Link>
      </div>
    </div>
  );
}