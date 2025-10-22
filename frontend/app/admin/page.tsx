"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Clock, 
  Users, 
  BarChart3, 
  Database,
  Settings,
  ArrowRight
} from "lucide-react";
import Link from "next/link";

export default function AdminDashboard() {
  const adminCards = [
    {
      title: "Model Timeouts",
      description: "Configure timeout settings for different LLM models",
      href: "/admin/timeouts",
      icon: Clock,
      color: "bg-blue-100 text-blue-800",
    },
    {
      title: "User Management",
      description: "Manage users, roles, and permissions",
      href: "/admin/users",
      icon: Users,
      color: "bg-green-100 text-green-800",
    },
    {
      title: "Analytics",
      description: "View usage statistics and performance metrics",
      href: "/admin/analytics",
      icon: BarChart3,
      color: "bg-purple-100 text-purple-800",
    },
    {
      title: "System Health",
      description: "Monitor system status and health metrics",
      href: "/admin/health",
      icon: Database,
      color: "bg-orange-100 text-orange-800",
    },
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Manage your ArchMesh application settings and monitor system health
          </p>
        </div>
        <Badge variant="outline" className="flex items-center gap-2">
          <Settings className="h-4 w-4" />
          Admin Panel
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {adminCards.map((card) => (
          <Card key={card.title} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <card.icon className="h-8 w-8 text-muted-foreground" />
                <Badge className={card.color}>
                  {card.title.split(' ')[0]}
                </Badge>
              </div>
              <CardTitle className="text-lg">{card.title}</CardTitle>
              <CardDescription>{card.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <Link href={card.href}>
                <Button variant="outline" className="w-full group">
                  Configure
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common administrative tasks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/admin/timeouts">
              <Button variant="outline" className="w-full justify-start">
                <Clock className="mr-2 h-4 w-4" />
                Adjust Model Timeouts
              </Button>
            </Link>
            <Link href="/admin/analytics">
              <Button variant="outline" className="w-full justify-start">
                <BarChart3 className="mr-2 h-4 w-4" />
                View Usage Analytics
              </Button>
            </Link>
            <Link href="/admin/health">
              <Button variant="outline" className="w-full justify-start">
                <Database className="mr-2 h-4 w-4" />
                Check System Health
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>
              Current system status and health
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">API Status</span>
              <Badge variant="outline" className="bg-green-100 text-green-800">
                Online
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Database</span>
              <Badge variant="outline" className="bg-green-100 text-green-800">
                Connected
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">LLM Services</span>
              <Badge variant="outline" className="bg-green-100 text-green-800">
                Active
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Redis Cache</span>
              <Badge variant="outline" className="bg-green-100 text-green-800">
                Connected
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
