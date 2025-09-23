"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/use-toast"

interface Patient {
  fullName: string
  ssn: string
  mobileNumber: string
  dateOfBirth: string
  gender: string
}

interface CheckEvalForm {
  id: string
  createdAt: string
}

interface GeneralSheetForm {
  id: string
  createdAt: string
}

interface Visit {
  id: string
  patientSsn: string
  visitDate: string
  visitStatus: "OPEN" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED"
  notes?: string
  createdAt: string
  updatedAt: string
  patient: Patient
  checkEval?: CheckEvalForm
  generalSheet?: GeneralSheetForm
}

interface NurseCurrentVisitsProps {
  userRole: string
}

export default function NurseCurrentVisits({ userRole }: NurseCurrentVisitsProps) {
  const [visits, setVisits] = useState<Visit[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const { toast } = useToast()

  useEffect(() => {
    if (userRole === "NURSE") {
      fetchCurrentVisits()
    }
  }, [userRole])

  const fetchCurrentVisits = async () => {
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("/api/visits/my-current", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setVisits(data)
      } else if (response.status === 403) {
        // User is not a nurse, don't show the component
        setVisits([])
      } else {
        const error = await response.json()
        toast({
          title: "Error",
          description: error.detail || "Failed to fetch current visits",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An error occurred while fetching current visits",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const getVisitStatusBadge = (status: string) => {
    const variants = {
      OPEN: "secondary",
      IN_PROGRESS: "default",
      COMPLETED: "outline",
      CANCELLED: "destructive",
    } as const

    const labels = {
      OPEN: "Open",
      IN_PROGRESS: "In Progress",
      COMPLETED: "Completed",
      CANCELLED: "Cancelled",
    }

    return (
      <Badge variant={variants[status as keyof typeof variants] || "secondary"}>
        {labels[status as keyof typeof labels] || status}
      </Badge>
    )
  }

  const getFormCompletionStatus = (visit: Visit) => {
    const hasCheckEval = !!visit.checkEval
    const hasGeneralSheet = !!visit.generalSheet

    if (!hasCheckEval && !hasGeneralSheet) {
      return { text: "Not Started", color: "text-gray-500" }
    } else if (hasCheckEval && !hasGeneralSheet) {
      return { text: "Nursing Assessment Complete", color: "text-blue-600" }
    } else if (!hasCheckEval && hasGeneralSheet) {
      return { text: "Physician Assessment Complete", color: "text-green-600" }
    } else {
      return { text: "All Assessments Complete", color: "text-green-600" }
    }
  }

  const handleContinueWork = (visitId: string, visitStatus: string) => {
    // Determine which form to continue working on based on role and completion status
    if (userRole === "NURSE") {
      // Nurses work on check-eval forms
      router.push(`/visits/${visitId}/check-eval`)
    } else if (userRole === "PHYSICIAN") {
      // Physicians work on general-sheet forms
      router.push(`/visits/${visitId}/general-sheet`)
    } else {
      // Admin can view visit details
      router.push(`/visits/${visitId}`)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  if (userRole !== "NURSE") {
    return null
  }

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>My Current Visits</CardTitle>
          <CardDescription>Visits that are currently in progress or open</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, index) => (
              <div key={index} className="border rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <Skeleton className="h-4 w-48 mb-2" />
                    <Skeleton className="h-3 w-32" />
                  </div>
                  <Skeleton className="h-6 w-20" />
                </div>
                <div className="flex justify-between items-center">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-8 w-24" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (visits.length === 0) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>My Current Visits</CardTitle>
          <CardDescription>Visits that are currently in progress or open</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">No current visits found</p>
            <p className="text-sm text-gray-400">Create a new visit to get started</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>My Current Visits</CardTitle>
        <CardDescription>Visits that are currently in progress or open</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {visits.map((visit) => {
            const completionStatus = getFormCompletionStatus(visit)
            return (
              <div key={visit.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-medium text-gray-900">{visit.patient.fullName}</h3>
                    <p className="text-sm text-gray-500">SSN: {visit.patient.ssn}</p>
                  </div>
                  {getVisitStatusBadge(visit.visitStatus)}
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-600 mb-3">
                  <div>
                    <span className="font-medium">Mobile:</span> {visit.patient.mobileNumber}
                  </div>
                  <div>
                    <span className="font-medium">Visit Date:</span> {formatDate(visit.visitDate)}
                  </div>
                  <div>
                    <span className="font-medium">Gender:</span> {visit.patient.gender}
                  </div>
                  <div>
                    <span className="font-medium">Age:</span> {Math.floor((new Date().getTime() - new Date(visit.patient.dateOfBirth).getTime()) / (365.25 * 24 * 60 * 60 * 1000))} years
                  </div>
                </div>

                {visit.notes && (
                  <div className="mb-3">
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Notes:</span> {visit.notes}
                    </p>
                  </div>
                )}

                <div className="flex justify-between items-center">
                  <span className={`text-sm font-medium ${completionStatus.color}`}>
                    {completionStatus.text}
                  </span>
                  <Button 
                    onClick={() => handleContinueWork(visit.id, visit.visitStatus)}
                    size="sm"
                  >
                    Continue Work
                  </Button>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}