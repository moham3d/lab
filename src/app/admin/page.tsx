"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"

interface User {
  id: string
  username: string
  email: string
  fullName: string
  role: "NURSE" | "PHYSICIAN" | "ADMIN"
  isActive: boolean
  createdAt: string
  lastLogin?: string
}

interface Visit {
  id: string
  patientSsn: string
  visitDate: string
  visitStatus: "OPEN" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED"
  notes?: string
  createdBy: string
  createdAt: string
  patient: {
    fullName: string
    ssn: string
  }
  user: {
    fullName: string
    username: string
  }
}

interface Report {
  id: string
  visitId: string
  summary: string
  doctorNotes?: string
  createdBy: string
  createdAt: string
  user: {
    fullName: string
    username: string
  }
}

export default function AdminDashboard() {
  const [users, setUsers] = useState<User[]>([])
  const [visits, setVisits] = useState<Visit[]>([])
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState<any>(null)
  const router = useRouter()
  const { toast } = useToast()

  useEffect(() => {
    const token = localStorage.getItem("token")
    const userData = localStorage.getItem("user")
    
    if (!token || !userData) {
      router.push("/")
      return
    }

    try {
      const parsedUser = JSON.parse(userData)
      if (parsedUser.role !== "ADMIN") {
        toast({
          title: "Access Denied",
          description: "Admin access required",
          variant: "destructive",
        })
        router.push("/")
        return
      }
      setUser(parsedUser)
      fetchData()
    } catch (error) {
      console.error("Error parsing user data:", error)
      router.push("/")
    }
  }, [router, toast])

  const fetchData = async () => {
    try {
      const token = localStorage.getItem("token")
      const [usersRes, visitsRes, reportsRes] = await Promise.all([
        fetch("/api/users", {
          headers: { "Authorization": `Bearer ${token}` }
        }),
        fetch("/api/visits", {
          headers: { "Authorization": `Bearer ${token}` }
        }),
        fetch("/api/reports", {
          headers: { "Authorization": `Bearer ${token}` }
        })
      ])

      if (usersRes.ok) {
        const usersData = await usersRes.json()
        setUsers(usersData)
      }

      if (visitsRes.ok) {
        const visitsData = await visitsRes.json()
        setVisits(visitsData)
      }

      if (reportsRes.ok) {
        const reportsData = await reportsRes.json()
        setReports(reportsData)
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch dashboard data",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    router.push("/")
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case "ADMIN": return "bg-red-100 text-red-800"
      case "PHYSICIAN": return "bg-blue-100 text-blue-800"
      case "NURSE": return "bg-green-100 text-green-800"
      default: return "bg-gray-100 text-gray-800"
    }
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case "COMPLETED": return "bg-green-100 text-green-800"
      case "IN_PROGRESS": return "bg-yellow-100 text-yellow-800"
      case "OPEN": return "bg-blue-100 text-blue-800"
      case "CANCELLED": return "bg-red-100 text-red-800"
      default: return "bg-gray-100 text-gray-800"
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="relative w-10 h-10 mr-3">
                <img
                  src="/logo.svg"
                  alt="Patient Visit Management System"
                  className="w-full h-full object-contain"
                />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">
                Admin Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user?.fullName} (Admin)
              </span>
              <Button variant="outline" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{users.length}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Visits</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{visits.length}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Visits</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {visits.filter(v => v.visitStatus !== 'COMPLETED' && v.visitStatus !== 'CANCELLED').length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Reports</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reports.length}</div>
              </CardContent>
            </Card>
          </div>

          {/* Tabs */}
          <Tabs defaultValue="users" className="space-y-4">
            <TabsList>
              <TabsTrigger value="users">Users Management</TabsTrigger>
              <TabsTrigger value="visits">Visits Reports</TabsTrigger>
            </TabsList>

            <TabsContent value="users">
              <Card>
                <CardHeader>
                  <CardTitle>Users Management</CardTitle>
                  <CardDescription>
                    Manage system users, roles, and permissions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="text-lg font-medium">System Users</h3>
                      <Button onClick={() => router.push("/admin/users/new")}>
                        Add New User
                      </Button>
                    </div>
                    
                    <div className="border rounded-lg">
                      <div className="grid grid-cols-6 gap-4 p-4 border-b bg-gray-50 font-medium text-sm">
                        <div>Username</div>
                        <div>Full Name</div>
                        <div>Email</div>
                        <div>Role</div>
                        <div>Status</div>
                        <div>Actions</div>
                      </div>
                      
                      {users.map((user) => (
                        <div key={user.id} className="grid grid-cols-6 gap-4 p-4 border-b text-sm">
                          <div className="font-medium">{user.username}</div>
                          <div>{user.fullName}</div>
                          <div>{user.email}</div>
                          <div>
                            <Badge className={getRoleBadgeColor(user.role)}>
                              {user.role}
                            </Badge>
                          </div>
                          <div>
                            <Badge variant={user.isActive ? "default" : "secondary"}>
                              {user.isActive ? "Active" : "Inactive"}
                            </Badge>
                          </div>
                          <div className="flex space-x-2">
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => router.push(`/admin/users/${user.id}`)}
                            >
                              Edit
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => router.push(`/admin/users/${user.id}/toggle`)}
                            >
                              {user.isActive ? "Disable" : "Enable"}
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="visits">
              <Card>
                <CardHeader>
                  <CardTitle>Visits Reports</CardTitle>
                  <CardDescription>
                    View and analyze patient visits and reports
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Recent Visits */}
                    <div>
                      <h3 className="text-lg font-medium mb-4">Recent Visits</h3>
                      <div className="border rounded-lg">
                        <div className="grid grid-cols-6 gap-4 p-4 border-b bg-gray-50 font-medium text-sm">
                          <div>Patient</div>
                          <div>Created By</div>
                          <div>Date</div>
                          <div>Status</div>
                          <div>Notes</div>
                          <div>Actions</div>
                        </div>
                        
                        {visits.slice(0, 10).map((visit) => (
                          <div key={visit.id} className="grid grid-cols-6 gap-4 p-4 border-b text-sm">
                            <div>
                              <div className="font-medium">{visit.patient.fullName}</div>
                              <div className="text-gray-500">{visit.patient.ssn}</div>
                            </div>
                            <div>
                              <div className="font-medium">{visit.user.fullName}</div>
                              <div className="text-gray-500">{visit.user.username}</div>
                            </div>
                            <div>
                              {new Date(visit.visitDate).toLocaleDateString()}
                            </div>
                            <div>
                              <Badge className={getStatusBadgeColor(visit.visitStatus)}>
                                {visit.visitStatus}
                              </Badge>
                            </div>
                            <div className="truncate max-w-xs">
                              {visit.notes || "No notes"}
                            </div>
                            <div>
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => router.push(`/visits/${visit.id}`)}
                              >
                                View
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Reports Summary */}
                    <div>
                      <h3 className="text-lg font-medium mb-4">Reports Summary</h3>
                      <div className="border rounded-lg">
                        <div className="grid grid-cols-4 gap-4 p-4 border-b bg-gray-50 font-medium text-sm">
                          <div>Created By</div>
                          <div>Visit ID</div>
                          <div>Summary</div>
                          <div>Created At</div>
                        </div>
                        
                        {reports.slice(0, 10).map((report) => (
                          <div key={report.id} className="grid grid-cols-4 gap-4 p-4 border-b text-sm">
                            <div>
                              <div className="font-medium">{report.user.fullName}</div>
                              <div className="text-gray-500">{report.user.username}</div>
                            </div>
                            <div className="font-mono text-xs">{report.visitId}</div>
                            <div className="truncate max-w-xs">
                              {report.summary}
                            </div>
                            <div>
                              {new Date(report.createdAt).toLocaleDateString()}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  )
}