"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { useToast } from "@/hooks/use-toast"

interface Visit {
  id: string
  patient: {
    fullName: string
    ssn: string
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

export default function GeneralSheetFormPage() {
  const [visit, setVisit] = useState<Visit | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const visitId = params.id as string

  const [formData, setFormData] = useState({
    // Basic Information
    diagnosis: "",
    reasonForStudy: "",
    findings: "",
    impression: "",
    recommendations: "",
    modality: "",
    bodyRegion: "",
    
    // Medical History
    hasChronicDisease: false,
    hasPacemaker: false,
    isPregnant: false,
    
    // Symptoms & Conditions
    hasPainNumbness: false,
    hasSpinalDeformities: false,
    hasSwelling: false,
    hasHeadache: false,
    hasFever: false,
    hasTumorHistory: false,
    hasDiscSlip: false,
  })

  useEffect(() => {
    const token = localStorage.getItem("token")
    const userData = localStorage.getItem("user")
    
    if (!token || !userData) {
      router.push("/")
      return
    }

    try {
      const parsedUser = JSON.parse(userData)
      if (parsedUser.role !== "PHYSICIAN" && parsedUser.role !== "ADMIN") {
        toast({
          title: "Access Denied",
          description: "Physician access required",
          variant: "destructive",
        })
        router.push("/visits")
        return
      }
      setUser(parsedUser)
      fetchVisitData(token, visitId)
    } catch (error) {
      console.error("Error parsing user data:", error)
      router.push("/")
    }
  }, [router, visitId, toast])

  const fetchVisitData = async (token: string, visitId: string) => {
    try {
      const response = await fetch(`/api/visits/${visitId}`, {
        headers: { "Authorization": `Bearer ${token}` }
      })

      if (response.ok) {
        const visitData = await response.json()
        setVisit(visitData)
        
        // Check if form already exists
        if (visitData.generalSheet) {
          toast({
            title: "Form Already Completed",
            description: "This radiology assessment has already been completed.",
            variant: "destructive",
          })
          router.push(`/visits/${visitId}`)
        }
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch visit data",
          variant: "destructive",
        })
        router.push("/visits")
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An error occurred while fetching visit data",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const token = localStorage.getItem("token")
      const response = await fetch(`/api/forms/general-sheet/${visitId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
        visitId,
        userId: user.id,
        ...formData,
      }),
      })

      if (response.ok) {
        // Update visit status to IN_PROGRESS if it's still OPEN
        if (visit.visitStatus === "OPEN") {
          try {
            const updateResponse = await fetch(`/api/visits/${visitId}/status`, {
              method: "PUT",
              headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
              },
              body: JSON.stringify({ status: "IN_PROGRESS" }),
            })
            if (updateResponse.ok) {
              console.log("Visit status updated to IN_PROGRESS")
            }
          } catch (error) {
            console.error("Failed to update visit status:", error)
          }
        }
        
        toast({
          title: "Success",
          description: "Radiology assessment completed successfully",
        })
        router.push(`/visits/${visitId}`)
      } else {
        const error = await response.json()
        toast({
          title: "Error",
          description: error.detail || "Failed to submit assessment",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An error occurred while submitting the assessment",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    router.push("/")
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  if (!visit || !user) {
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
              <div>
                <h1 className="text-xl font-semibold text-gray-900">Radiology Assessment</h1>
                <p className="text-sm text-gray-600">
                  Patient: {visit.patient.fullName} (SSN: {visit.patient.ssn})
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user.fullName} ({user.role})
              </span>
              <Button variant="outline" onClick={() => router.push(`/visits/${visitId}`)}>
                Back to Visit
              </Button>
              <Button variant="outline" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <Card>
            <CardHeader>
              <CardTitle>Radiology Assessment Form (General Sheet)</CardTitle>
              <CardDescription>
                Complete the radiology assessment for this patient visit
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-8">
                {/* Basic Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Basic Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="diagnosis">Diagnosis</Label>
                      <Input
                        id="diagnosis"
                        value={formData.diagnosis}
                        onChange={(e) => setFormData({ ...formData, diagnosis: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="reasonForStudy">Reason for Study</Label>
                      <Input
                        id="reasonForStudy"
                        value={formData.reasonForStudy}
                        onChange={(e) => setFormData({ ...formData, reasonForStudy: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="modality">Modality</Label>
                      <Select 
                        value={formData.modality} 
                        onValueChange={(value) => setFormData({ ...formData, modality: value })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select modality" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="CT">CT</SelectItem>
                          <SelectItem value="MRI">MRI</SelectItem>
                          <SelectItem value="X-ray">X-ray</SelectItem>
                          <SelectItem value="Ultrasound">Ultrasound</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="bodyRegion">Body Region</Label>
                      <Input
                        id="bodyRegion"
                        value={formData.bodyRegion}
                        onChange={(e) => setFormData({ ...formData, bodyRegion: e.target.value })}
                      />
                    </div>
                  </div>
                </div>

                {/* Findings */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Findings *</h3>
                  <div>
                    <Label htmlFor="findings">Findings</Label>
                    <Textarea
                      id="findings"
                      value={formData.findings}
                      onChange={(e) => setFormData({ ...formData, findings: e.target.value })}
                      rows={4}
                      required
                      placeholder="Describe the radiological findings..."
                    />
                  </div>
                </div>

                {/* Assessment */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Assessment</h3>
                  <div>
                    <Label htmlFor="impression">Impression</Label>
                    <Textarea
                      id="impression"
                      value={formData.impression}
                      onChange={(e) => setFormData({ ...formData, impression: e.target.value })}
                      rows={3}
                      placeholder="Radiological impression and interpretation..."
                    />
                  </div>
                  <div>
                    <Label htmlFor="recommendations">Recommendations</Label>
                    <Textarea
                      id="recommendations"
                      value={formData.recommendations}
                      onChange={(e) => setFormData({ ...formData, recommendations: e.target.value })}
                      rows={3}
                      placeholder="Recommendations for further treatment or follow-up..."
                    />
                  </div>
                </div>

                {/* Medical History */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Medical History</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="chronicDisease"
                        checked={formData.hasChronicDisease}
                        onCheckedChange={(checked) => setFormData({ ...formData, hasChronicDisease: Boolean(checked) })}
                      />
                      <Label htmlFor="chronicDisease">Chronic Disease</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="pacemaker"
                        checked={formData.hasPacemaker}
                        onCheckedChange={(checked) => setFormData({ ...formData, hasPacemaker: Boolean(checked) })}
                      />
                      <Label htmlFor="pacemaker">Pacemaker</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="pregnant"
                        checked={formData.isPregnant}
                        onCheckedChange={(checked) => setFormData({ ...formData, isPregnant: Boolean(checked) })}
                      />
                      <Label htmlFor="pregnant">Pregnant</Label>
                    </div>
                  </div>
                </div>

                {/* Symptoms & Conditions */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Symptoms & Conditions</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="painNumbness"
                        checked={formData.hasPainNumbness}
                        onCheckedChange={(checked) => setFormData({ ...formData, hasPainNumbness: Boolean(checked) })}
                      />
                      <Label htmlFor="painNumbness">Pain/Numbness</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="spinalDeformities"
                        checked={formData.hasSpinalDeformities}
                        onCheckedChange={(checked) => setFormData({ ...formData, hasSpinalDeformities: Boolean(checked) })}
                      />
                      <Label htmlFor="spinalDeformities">Spinal Deformities</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="swelling"
                        checked={formData.hasSwelling}
                        onCheckedChange={(checked) => setFormData({ ...formData, hasSwelling: Boolean(checked) })}
                      />
                      <Label htmlFor="swelling">Swelling</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="headache"
                        checked={formData.hasHeadache}
                        onCheckedChange={(checked) => setFormData({ ...formData, hasHeadache: Boolean(checked) })}
                      />
                      <Label htmlFor="headache">Headache</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="fever"
                        checked={formData.hasFever}
                        onCheckedChange={(checked) => setFormData({ ...formData, hasFever: Boolean(checked) })}
                      />
                      <Label htmlFor="fever">Fever</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="tumorHistory"
                        checked={formData.hasTumorHistory}
                        onCheckedChange={(checked) => setFormData({ ...formData, hasTumorHistory: Boolean(checked) })}
                      />
                      <Label htmlFor="tumorHistory">Tumor History</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="discSlip"
                        checked={formData.hasDiscSlip}
                        onCheckedChange={(checked) => setFormData({ ...formData, hasDiscSlip: Boolean(checked) })}
                      />
                      <Label htmlFor="discSlip">Disc Slip</Label>
                    </div>
                  </div>
                </div>

                {/* Submit Button */}
                <div className="flex space-x-4">
                  <Button type="submit" disabled={isSubmitting} className="flex-1">
                    {isSubmitting ? "Submitting..." : "Submit Assessment"}
                  </Button>
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => router.push(`/visits/${visitId}`)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}