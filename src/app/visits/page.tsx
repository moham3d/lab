"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import NurseCurrentVisits from "@/components/NurseCurrentVisits"

interface Patient {
  ssn: string
  mobileNumber: string
  fullName: string
  dateOfBirth: string
  gender: "MALE" | "FEMALE" | "OTHER"
  address?: string
}

interface User {
  id: string
  username: string
  email: string
  fullName: string
  role: string
  isActive: boolean
}

export default function VisitsPage() {
  const [ssn, setSsn] = useState("")
  const [patient, setPatient] = useState<Patient | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isCreatingVisit, setIsCreatingVisit] = useState(false)
  const [notes, setNotes] = useState("")
  const [user, setUser] = useState<User | null>(null)
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
      setUser(parsedUser)
    } catch (error) {
      console.error("Error parsing user data:", error)
      router.push("/")
    }
  }, [router])

  const searchPatient = async () => {
    if (!ssn.trim()) {
      toast({
        title: "Error",
        description: "Please enter a valid SSN",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    try {
      const token = localStorage.getItem("token")
      const response = await fetch(`/api/patients/${ssn}`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const patientData = await response.json()
        setPatient(patientData)
        toast({
          title: "Patient Found",
          description: `Found patient: ${patientData.fullName}`,
        })
      } else if (response.status === 404) {
        // Patient not found, show create patient form
        setPatient(null)
        toast({
          title: "Patient Not Found",
          description: "Please create a new patient record",
        })
      } else {
        const error = await response.json()
        toast({
          title: "Error",
          description: error.detail || "Failed to search patient",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An error occurred while searching patient",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const createPatient = async (patientData: Omit<Patient, "ssn">) => {
    setIsLoading(true)
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("/api/patients", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          ssn,
          ...patientData,
        }),
      })

      if (response.ok) {
        const newPatient = await response.json()
        setPatient(newPatient)
        toast({
          title: "Patient Created",
          description: `New patient created: ${newPatient.fullName}`,
        })
      } else {
        const error = await response.json()
        toast({
          title: "Error",
          description: error.detail || "Failed to create patient",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An error occurred while creating patient",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const createVisit = async () => {
    if (!patient) {
      toast({
        title: "Error",
        description: "Please select or create a patient first",
        variant: "destructive",
      })
      return
    }

    setIsCreatingVisit(true)
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("/api/visits", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          patientSsn: patient.ssn,
          notes,
        }),
      })

      if (response.ok) {
        const visit = await response.json()
        toast({
          title: "Visit Created",
          description: `New visit created for ${patient.fullName}`,
        })
        
        // Reset form
        setSsn("")
        setPatient(null)
        setNotes("")
        
        // Redirect to visit details
        router.push(`/visits/${visit.id}`)
      } else {
        const error = await response.json()
        toast({
          title: "Error",
          description: error.detail || "Failed to create visit",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An error occurred while creating visit",
        variant: "destructive",
      })
    } finally {
      setIsCreatingVisit(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    router.push("/")
  }

  if (!user) {
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
                Patient Visit Management
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user.fullName} ({user.role})
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
        <div className="px-4 py-6 sm:px-0 space-y-6">
          {/* Nurse's Current Visits - Only shown for nurses */}
          <NurseCurrentVisits userRole={user.role} />
          
          {/* New Visit Form */}
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>New Visit</CardTitle>
              <CardDescription>
                Search for an existing patient or create a new patient record to start a visit
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Patient Search */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="ssn">Patient SSN (14 digits)</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="ssn"
                      placeholder="Enter 14-digit SSN"
                      value={ssn}
                      onChange={(e) => setSsn(e.target.value)}
                      maxLength={14}
                      className="flex-1"
                    />
                    <Button 
                      onClick={searchPatient} 
                      disabled={isLoading || !ssn.trim()}
                    >
                      {isLoading ? "Searching..." : "Search"}
                    </Button>
                  </div>
                </div>
              </div>

              {/* Patient Info */}
              {patient && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-medium text-green-800 mb-2">Patient Found</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Name:</span> {patient.fullName}
                    </div>
                    <div>
                      <span className="font-medium">SSN:</span> {patient.ssn}
                    </div>
                    <div>
                      <span className="font-medium">Mobile:</span> {patient.mobileNumber}
                    </div>
                    <div>
                      <span className="font-medium">DOB:</span> {new Date(patient.dateOfBirth).toLocaleDateString()}
                    </div>
                    <div>
                      <span className="font-medium">Gender:</span> {patient.gender}
                    </div>
                    {patient.address && (
                      <div className="col-span-2">
                        <span className="font-medium">Address:</span> {patient.address}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Create Patient Form (when patient not found) */}
              {!patient && ssn && !isLoading && (
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-medium mb-4">Create New Patient</h3>
                  <NewPatientForm 
                    onSubmit={createPatient} 
                    isLoading={isLoading} 
                  />
                </div>
              )}

              {/* Visit Notes */}
              {patient && (
                <div className="space-y-2">
                  <Label htmlFor="notes">Visit Notes</Label>
                  <textarea
                    id="notes"
                    className="w-full min-h-[100px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter initial visit notes..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                  />
                </div>
              )}

              {/* Create Visit Button */}
              {patient && (
                <Button 
                  onClick={createVisit} 
                  disabled={isCreatingVisit}
                  className="w-full"
                >
                  {isCreatingVisit ? "Creating Visit..." : "Create New Visit"}
                </Button>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

// New Patient Form Component
function NewPatientForm({ onSubmit, isLoading }: { 
  onSubmit: (data: Omit<Patient, "ssn">) => void
  isLoading: boolean 
}) {
  const [formData, setFormData] = useState({
    fullName: "",
    mobileNumber: "",
    dateOfBirth: "",
    gender: "MALE" as "MALE" | "FEMALE" | "OTHER",
    address: "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="fullName">Full Name *</Label>
          <Input
            id="fullName"
            value={formData.fullName}
            onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
            required
          />
        </div>
        <div>
          <Label htmlFor="mobileNumber">Mobile Number *</Label>
          <Input
            id="mobileNumber"
            placeholder="01XXXXXXXXX"
            value={formData.mobileNumber}
            onChange={(e) => setFormData({ ...formData, mobileNumber: e.target.value })}
            required
          />
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="dateOfBirth">Date of Birth *</Label>
          <Input
            id="dateOfBirth"
            type="date"
            value={formData.dateOfBirth}
            onChange={(e) => setFormData({ ...formData, dateOfBirth: e.target.value })}
            required
          />
        </div>
        <div>
          <Label htmlFor="gender">Gender *</Label>
          <Select 
            value={formData.gender} 
            onValueChange={(value: "MALE" | "FEMALE" | "OTHER") => 
              setFormData({ ...formData, gender: value })
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="MALE">Male</SelectItem>
              <SelectItem value="FEMALE">Female</SelectItem>
              <SelectItem value="OTHER">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div>
        <Label htmlFor="address">Address</Label>
        <Input
          id="address"
          value={formData.address}
          onChange={(e) => setFormData({ ...formData, address: e.target.value })}
        />
      </div>

      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? "Creating Patient..." : "Create Patient"}
      </Button>
    </form>
  )
}