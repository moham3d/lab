"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"

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
    mobileNumber: string
    dateOfBirth: string
    gender: "MALE" | "FEMALE" | "OTHER"
    address?: string
  }
  user: {
    fullName: string
    username: string
    role: string
  }
  checkEval?: {
    id: string
    temperatureCelsius: number
    pulseBpm: number
    bloodPressureSystolic: number
    bloodPressureDiastolic: number
    respiratoryRatePerMin: number
    oxygenSaturationPercent: number
    weightKg: number
    heightCm: number
    chiefComplaint?: string
    createdAt: string
  }
  generalSheet?: {
    id: string
    diagnosis?: string
    reasonForStudy?: string
    findings: string
    impression?: string
    recommendations?: string
    modality?: string
    bodyRegion?: string
    createdAt: string
  }
}

interface User {
  id: string
  username: string
  email: string
  fullName: string
  role: string
  isActive: boolean
}

export default function VisitDetailsPage() {
  const [visit, setVisit] = useState<Visit | null>(null)
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState<User | null>(null)
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false)
  const router = useRouter()
  const params = useParams()
  const { toast } = useToast()
  const visitId = params.id as string

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
      fetchVisitData(token, visitId)
    } catch (error) {
      console.error("Error parsing user data:", error)
      router.push("/")
    }
  }, [router, visitId])

  const fetchVisitData = async (token: string, visitId: string) => {
    try {
      const response = await fetch(`/api/visits/${visitId}`, {
        headers: { "Authorization": `Bearer ${token}` }
      })

      if (response.ok) {
        const visitData = await response.json()
        setVisit(visitData)
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch visit details",
          variant: "destructive",
        })
        router.push("/visits")
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An error occurred while fetching visit details",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const updateVisitStatus = async (newStatus: string) => {
    if (!visit) return

    setIsUpdatingStatus(true)
    try {
      const token = localStorage.getItem("token")
      const response = await fetch(`/api/visits/${visitId}/status`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      })

      if (response.ok) {
        const updatedVisit = await response.json()
        setVisit(updatedVisit)
        toast({
          title: "Success",
          description: `Visit status updated to ${newStatus}`,
        })
      } else {
        const error = await response.json()
        toast({
          title: "Error",
          description: error.detail || "Failed to update visit status",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An error occurred while updating visit status",
        variant: "destructive",
      })
    } finally {
      setIsUpdatingStatus(false)
    }
  }

  const canCompleteVisit = () => {
    return visit && visit.checkEval && visit.generalSheet && visit.visitStatus !== "COMPLETED"
  }

  const canCancelVisit = () => {
    return visit && visit.visitStatus !== "CANCELLED" && visit.visitStatus !== "COMPLETED"
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    router.push("/")
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

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case "ADMIN": return "bg-red-100 text-red-800"
      case "PHYSICIAN": return "bg-blue-100 text-blue-800"
      case "NURSE": return "bg-green-100 text-green-800"
      default: return "bg-gray-100 text-gray-800"
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  if (!visit) {
    return <div className="flex items-center justify-center min-h-screen">Visit not found</div>
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
                Visit Details
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user?.fullName} ({user?.role})
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
          {/* Visit Summary */}
          <Card className="mb-6">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    Visit for {visit.patient.fullName}
                    <Badge className={getStatusBadgeColor(visit.visitStatus)}>
                      {visit.visitStatus}
                    </Badge>
                  </CardTitle>
                  <CardDescription>
                    Visit ID: {visit.id} | Created: {new Date(visit.createdAt).toLocaleDateString()}
                  </CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Button 
                    variant="outline" 
                    onClick={() => router.push("/visits")}
                  >
                    Back to Visits
                  </Button>
                  {canCompleteVisit() && (
                    <Button 
                      onClick={() => updateVisitStatus("COMPLETED")}
                      disabled={isUpdatingStatus}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      {isUpdatingStatus ? "Updating..." : "Complete Visit"}
                    </Button>
                  )}
                  {canCancelVisit() && (
                    <Button 
                      variant="destructive"
                      onClick={() => updateVisitStatus("CANCELLED")}
                      disabled={isUpdatingStatus}
                    >
                      {isUpdatingStatus ? "Updating..." : "Cancel Visit"}
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Patient Information */}
                <div>
                  <h3 className="font-medium text-sm text-gray-900 mb-2">Patient Information</h3>
                  <div className="space-y-1 text-sm">
                    <div><span className="font-medium">Name:</span> {visit.patient.fullName}</div>
                    <div><span className="font-medium">SSN:</span> {visit.patient.ssn}</div>
                    <div><span className="font-medium">Mobile:</span> {visit.patient.mobileNumber}</div>
                    <div><span className="font-medium">DOB:</span> {new Date(visit.patient.dateOfBirth).toLocaleDateString()}</div>
                    <div><span className="font-medium">Gender:</span> {visit.patient.gender}</div>
                    {visit.patient.address && (
                      <div><span className="font-medium">Address:</span> {visit.patient.address}</div>
                    )}
                  </div>
                </div>

                {/* Visit Information */}
                <div>
                  <h3 className="font-medium text-sm text-gray-900 mb-2">Visit Information</h3>
                  <div className="space-y-1 text-sm">
                    <div><span className="font-medium">Visit Date:</span> {new Date(visit.visitDate).toLocaleDateString()}</div>
                    <div><span className="font-medium">Status:</span> 
                      <Badge className={getStatusBadgeColor(visit.visitStatus)}>
                        {visit.visitStatus}
                      </Badge>
                    </div>
                    <div><span className="font-medium">Created By:</span> {visit.user.fullName}</div>
                    <div><span className="font-medium">Role:</span> 
                      <Badge className={getRoleBadgeColor(visit.user.role)}>
                        {visit.user.role}
                      </Badge>
                    </div>
                    {visit.notes && (
                      <div><span className="font-medium">Notes:</span> {visit.notes}</div>
                    )}
                    {/* Visit Status Management */}
                    <div className="mt-3 pt-3 border-t">
                      <h4 className="font-medium text-sm text-gray-900 mb-2">Update Status</h4>
                      <Select
                        value={visit.visitStatus}
                        onValueChange={updateVisitStatus}
                        disabled={isUpdatingStatus || visit.visitStatus === "COMPLETED" || visit.visitStatus === "CANCELLED"}
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="OPEN">Open</SelectItem>
                          <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
                          <SelectItem value="COMPLETED" disabled={!canCompleteVisit()}>
                            Completed
                          </SelectItem>
                          <SelectItem value="CANCELLED" disabled={!canCancelVisit()}>
                            Cancelled
                          </SelectItem>
                        </SelectContent>
                      </Select>
                      {visit.visitStatus === "COMPLETED" && (
                        <p className="text-xs text-green-600 mt-1">
                          ✓ Visit completed successfully
                        </p>
                      )}
                      {visit.visitStatus === "CANCELLED" && (
                        <p className="text-xs text-red-600 mt-1">
                          ✗ Visit has been cancelled
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Form Status */}
                <div>
                  <h3 className="font-medium text-sm text-gray-900 mb-2">Form Status</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span>Nursing Assessment (Check-Eval)</span>
                      {visit.checkEval ? (
                        <Badge className="bg-green-100 text-green-800">Completed</Badge>
                      ) : (
                        <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>
                      )}
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Physician Assessment (General Sheet)</span>
                      {visit.generalSheet ? (
                        <Badge className="bg-green-100 text-green-800">Completed</Badge>
                      ) : (
                        <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>
                      )}
                    </div>
                    
                    {/* Completion Progress */}
                    <div className="mt-3 pt-3 border-t">
                      <h4 className="font-medium text-sm text-gray-900 mb-2">Completion Progress</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span>Overall Progress</span>
                          <span>
                            {((visit.checkEval ? 50 : 0) + (visit.generalSheet ? 50 : 0))}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${(visit.checkEval ? 50 : 0) + (visit.generalSheet ? 50 : 0)}%` }}
                          ></div>
                        </div>
                        
                        {/* Completion Requirements */}
                        <div className="mt-3 p-2 bg-gray-50 rounded text-xs">
                          <p className="font-medium text-gray-700 mb-1">Requirements for completion:</p>
                          <ul className="space-y-1 text-gray-600">
                            <li className="flex items-center">
                              {visit.checkEval ? (
                                <span className="text-green-600 mr-1">✓</span>
                              ) : (
                                <span className="text-gray-400 mr-1">○</span>
                              )}
                              Nursing assessment completed
                            </li>
                            <li className="flex items-center">
                              {visit.generalSheet ? (
                                <span className="text-green-600 mr-1">✓</span>
                              ) : (
                                <span className="text-gray-400 mr-1">○</span>
                              )}
                              Physician assessment completed
                            </li>
                          </ul>
                          {canCompleteVisit() && (
                            <p className="text-green-600 font-medium mt-2">
                              ✓ Ready to complete visit
                            </p>
                          )}
                          {!canCompleteVisit() && visit.visitStatus !== "COMPLETED" && (
                            <p className="text-yellow-600 font-medium mt-2">
                              ⚠ Complete all required forms first
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Forms Tabs */}
          <Tabs defaultValue="forms" className="space-y-4">
            <TabsList>
              <TabsTrigger value="forms">Assessment Forms</TabsTrigger>
              {visit.checkEval && <TabsTrigger value="check-eval">Nursing Assessment</TabsTrigger>}
              {visit.generalSheet && <TabsTrigger value="general-sheet">Physician Assessment</TabsTrigger>}
            </TabsList>

            <TabsContent value="forms">
              <Card>
                <CardHeader>
                  <CardTitle>Assessment Forms</CardTitle>
                  <CardDescription>
                    Complete the required assessment forms for this visit
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Nursing Assessment Form */}
                    <Card className="border-2 border-dashed border-gray-300">
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          Nursing Assessment
                          {visit.checkEval ? (
                            <Badge className="bg-green-100 text-green-800">Completed</Badge>
                          ) : (
                            <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>
                          )}
                        </CardTitle>
                        <CardDescription>
                          Check-Eval Form (SH.MR.FRM.05) - To be completed by nurses
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {visit.checkEval ? (
                            <div className="space-y-2 text-sm">
                              <div><span className="font-medium">Temperature:</span> {visit.checkEval.temperatureCelsius}°C</div>
                              <div><span className="font-medium">Pulse:</span> {visit.checkEval.pulseBpm} bpm</div>
                              <div><span className="font-medium">Blood Pressure:</span> {visit.checkEval.bloodPressureSystolic}/{visit.checkEval.bloodPressureDiastolic} mmHg</div>
                              <div><span className="font-medium">O2 Saturation:</span> {visit.checkEval.oxygenSaturationPercent}%</div>
                              <div><span className="font-medium">Weight:</span> {visit.checkEval.weightKg} kg</div>
                              <div><span className="font-medium">Height:</span> {visit.checkEval.heightCm} cm</div>
                              {visit.checkEval.chiefComplaint && (
                                <div><span className="font-medium">Chief Complaint:</span> {visit.checkEval.chiefComplaint}</div>
                              )}
                              <div><span className="font-medium">Completed:</span> {new Date(visit.checkEval.createdAt).toLocaleDateString()}</div>
                            </div>
                          ) : (
                            <div className="space-y-4">
                              <p className="text-sm text-gray-600">
                                This form needs to be completed by a nurse. It includes vital signs, 
                                patient assessment, and risk evaluation.
                              </p>
                              {user?.role === "NURSE" ? (
                                <Button 
                                  className="w-full" 
                                  onClick={() => router.push(`/visits/${visitId}/check-eval`)}
                                >
                                  Start Nursing Assessment
                                </Button>
                              ) : (
                                <div className="text-center p-4 bg-gray-50 rounded-lg">
                                  <p className="text-sm text-gray-500">
                                    Only nurses can complete this form
                                  </p>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Physician Assessment Form */}
                    <Card className="border-2 border-dashed border-gray-300">
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          Physician Assessment
                          {visit.generalSheet ? (
                            <Badge className="bg-green-100 text-green-800">Completed</Badge>
                          ) : (
                            <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>
                          )}
                        </CardTitle>
                        <CardDescription>
                          General Sheet Form (SH.MR.FRM.04) - To be completed by physicians
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {visit.generalSheet ? (
                            <div className="space-y-2 text-sm">
                              {visit.generalSheet.diagnosis && (
                                <div><span className="font-medium">Diagnosis:</span> {visit.generalSheet.diagnosis}</div>
                              )}
                              {visit.generalSheet.reasonForStudy && (
                                <div><span className="font-medium">Reason for Study:</span> {visit.generalSheet.reasonForStudy}</div>
                              )}
                              <div><span className="font-medium">Findings:</span> {visit.generalSheet.findings}</div>
                              {visit.generalSheet.impression && (
                                <div><span className="font-medium">Impression:</span> {visit.generalSheet.impression}</div>
                              )}
                              {visit.generalSheet.recommendations && (
                                <div><span className="font-medium">Recommendations:</span> {visit.generalSheet.recommendations}</div>
                              )}
                              {visit.generalSheet.modality && (
                                <div><span className="font-medium">Modality:</span> {visit.generalSheet.modality}</div>
                              )}
                              {visit.generalSheet.bodyRegion && (
                                <div><span className="font-medium">Body Region:</span> {visit.generalSheet.bodyRegion}</div>
                              )}
                              <div><span className="font-medium">Completed:</span> {new Date(visit.generalSheet.createdAt).toLocaleDateString()}</div>
                            </div>
                          ) : (
                            <div className="space-y-4">
                              <p className="text-sm text-gray-600">
                                This form needs to be completed by a physician. It includes diagnosis, 
                                findings, and medical recommendations.
                              </p>
                              {user?.role === "PHYSICIAN" ? (
                                <Button 
                                  className="w-full" 
                                  onClick={() => router.push(`/visits/${visitId}/general-sheet`)}
                                >
                                  Start Physician Assessment
                                </Button>
                              ) : (
                                <div className="text-center p-4 bg-gray-50 rounded-lg">
                                  <p className="text-sm text-gray-500">
                                    Only physicians can complete this form
                                  </p>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {visit.checkEval && (
              <TabsContent value="check-eval">
                <Card>
                  <CardHeader>
                    <CardTitle>Nursing Assessment Details</CardTitle>
                    <CardDescription>
                      Complete nursing assessment form data
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                      <div><span className="font-medium">Temperature:</span> {visit.checkEval.temperatureCelsius}°C</div>
                      <div><span className="font-medium">Pulse:</span> {visit.checkEval.pulseBpm} bpm</div>
                      <div><span className="font-medium">BP Systolic:</span> {visit.checkEval.bloodPressureSystolic} mmHg</div>
                      <div><span className="font-medium">BP Diastolic:</span> {visit.checkEval.bloodPressureDiastolic} mmHg</div>
                      <div><span className="font-medium">Respiratory Rate:</span> {visit.checkEval.respiratoryRatePerMin}/min</div>
                      <div><span className="font-medium">O2 Saturation:</span> {visit.checkEval.oxygenSaturationPercent}%</div>
                      <div><span className="font-medium">Weight:</span> {visit.checkEval.weightKg} kg</div>
                      <div><span className="font-medium">Height:</span> {visit.checkEval.heightCm} cm</div>
                      <div><span className="font-medium">Appetite:</span> {visit.checkEval.appetite}</div>
                      <div><span className="font-medium">Mobility:</span> {visit.checkEval.mobilityStatus}</div>
                      <div><span className="font-medium">Pain Intensity:</span> {visit.checkEval.painIntensity}/10</div>
                      <div><span className="font-medium">Smoker:</span> {visit.checkEval.isSmoker ? "Yes" : "No"}</div>
                    </div>
                    {visit.checkEval.chiefComplaint && (
                      <div className="mt-4">
                        <h4 className="font-medium text-sm mb-2">Chief Complaint:</h4>
                        <p className="text-sm">{visit.checkEval.chiefComplaint}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            )}

            {visit.generalSheet && (
              <TabsContent value="general-sheet">
                <Card>
                  <CardHeader>
                    <CardTitle>Physician Assessment Details</CardTitle>
                    <CardDescription>
                      Complete physician assessment form data
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4 text-sm">
                      {visit.generalSheet.diagnosis && (
                        <div>
                          <span className="font-medium">Diagnosis:</span> {visit.generalSheet.diagnosis}
                        </div>
                      )}
                      {visit.generalSheet.reasonForStudy && (
                        <div>
                          <span className="font-medium">Reason for Study:</span> {visit.generalSheet.reasonForStudy}
                        </div>
                      )}
                      <div>
                        <span className="font-medium">Findings:</span> {visit.generalSheet.findings}
                      </div>
                      {visit.generalSheet.impression && (
                        <div>
                          <span className="font-medium">Impression:</span> {visit.generalSheet.impression}
                        </div>
                      )}
                      {visit.generalSheet.recommendations && (
                        <div>
                          <span className="font-medium">Recommendations:</span> {visit.generalSheet.recommendations}
                        </div>
                      )}
                      {visit.generalSheet.modality && (
                        <div>
                          <span className="font-medium">Modality:</span> {visit.generalSheet.modality}
                        </div>
                      )}
                      {visit.generalSheet.bodyRegion && (
                        <div>
                          <span className="font-medium">Body Region:</span> {visit.generalSheet.bodyRegion}
                        </div>
                      )}
                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div><span className="font-medium">Chronic Disease:</span> {visit.generalSheet.hasChronicDisease ? "Yes" : "No"}</div>
                        <div><span className="font-medium">Pacemaker:</span> {visit.generalSheet.hasPacemaker ? "Yes" : "No"}</div>
                        <div><span className="font-medium">Pregnant:</span> {visit.generalSheet.isPregnant ? "Yes" : "No"}</div>
                        <div><span className="font-medium">Pain/Numbness:</span> {visit.generalSheet.hasPainNumbness ? "Yes" : "No"}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            )}
          </Tabs>
        </div>
      </main>
    </div>
  )
}