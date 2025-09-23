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

export default function CheckEvalFormPage() {
  const [visit, setVisit] = useState<Visit | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const visitId = params.id as string

  const [formData, setFormData] = useState({
    // Vital Signs
    temperatureCelsius: "",
    pulseBpm: "",
    bloodPressureSystolic: "",
    bloodPressureDiastolic: "",
    respiratoryRatePerMin: "",
    oxygenSaturationPercent: "",
    weightKg: "",
    heightCm: "",
    
    // Assessment
    chiefComplaint: "",
    generalCondition: "",
    consciousnessLevel: "",
    skinCondition: "",
    mobilityStatus: "",
    
    // Habits & History
    isSmoker: false,
    hasAllergies: false,
    
    // Nutrition
    dietType: "regular",
    appetite: "good",
    
    // Functional Status
    feedingStatus: "independent",
    hygieneStatus: "independent",
    toiletingStatus: "independent",
    ambulationStatus: "independent",
    
    // Pain & Risk Assessment
    painIntensity: "0",
    painLocation: "",
    painFrequency: "",
    painDuration: "",
    painCharacter: "",
    painActionTaken: "",
    fallHistory3months: false,
    secondaryDiagnosis: false,
    ivTherapy: false,
    needsMedicationEducation: false,
    dailyActivities: "independent",
    hasSignsOfAbuse: false,
    
    // Educational Needs
    educationalNeeds: [] as string[],
    
    // Fall Assessment - Morse Scale
    morseFallScore: 0,
    fallRiskLevel: "low",
    
    // Elderly Assessment
    elderlyDailyActivities: "independent",
    elderlyCognitiveAssessment: "normal",
    elderlyMoodAssessment: "normal",
    elderlySpeechDisorder: false,
    elderlyHearingDisorder: false,
    elderlyVisionDisorder: false,
    elderlySleepDisorder: false,
    
    // Disabled Assessment
    disabilityType: "",
    hasAssistiveDevices: false,
    
    // Abuse/Neglect
    hasAbuseNeglect: false,
    abuseNeglectDetails: "",
    
    // Signature
    nurseSignature: "",
    assessmentDate: "",
    assessmentTime: "",
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
      if (parsedUser.role !== "NURSE" && parsedUser.role !== "ADMIN") {
        toast({
          title: "Access Denied",
          description: "Nurse access required",
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
        if (visitData.checkEval) {
          toast({
            title: "Form Already Completed",
            description: "This nursing assessment has already been completed.",
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

  const calculateMorseScore = () => {
    let score = 0
    if (formData.fallHistory3months) score += 25
    if (formData.secondaryDiagnosis) score += 15
    if (formData.ivTherapy) score += 20
    // Add ambulation aid score when implemented
    setFormData({ ...formData, morseFallScore: score })
    
    // Update risk level
    let riskLevel = "low"
    if (score >= 25 && score <= 49) riskLevel = "moderate"
    else if (score >= 50) riskLevel = "high"
    setFormData(prev => ({ ...prev, fallRiskLevel: riskLevel }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const token = localStorage.getItem("token")
      const response = await fetch(`/api/forms/check-eval`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          visitId,
          userId: user.id,
          ...formData,
          // Convert string values to numbers
          temperatureCelsius: parseFloat(formData.temperatureCelsius) || 0,
          pulseBpm: parseInt(formData.pulseBpm) || 0,
          bloodPressureSystolic: parseInt(formData.bloodPressureSystolic) || 0,
          bloodPressureDiastolic: parseInt(formData.bloodPressureDiastolic) || 0,
          respiratoryRatePerMin: parseInt(formData.respiratoryRatePerMin) || 0,
          oxygenSaturationPercent: parseFloat(formData.oxygenSaturationPercent) || 0,
          weightKg: parseFloat(formData.weightKg) || 0,
          heightCm: parseInt(formData.heightCm) || 0,
          painIntensity: parseInt(formData.painIntensity) || 0,
          morseFallScore: formData.morseFallScore,
          // Convert arrays to strings for storage
          educationalNeeds: formData.educationalNeeds.join(','),
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
          description: "Nursing assessment completed successfully",
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
                <h1 className="text-xl font-semibold text-gray-900">Nursing Assessment</h1>
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
              <CardTitle>Nursing Assessment Form (Check-Eval)</CardTitle>
              <CardDescription>
                Complete the nursing assessment for this patient visit
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-8">
                {/* Vital Signs */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Vital Signs</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <Label htmlFor="temperature">Temperature (°C) *</Label>
                      <Input
                        id="temperature"
                        type="number"
                        step="0.1"
                        min="30"
                        max="45"
                        value={formData.temperatureCelsius}
                        onChange={(e) => setFormData({ ...formData, temperatureCelsius: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="pulse">Pulse (bpm) *</Label>
                      <Input
                        id="pulse"
                        type="number"
                        min="30"
                        max="200"
                        value={formData.pulseBpm}
                        onChange={(e) => setFormData({ ...formData, pulseBpm: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="bpSystolic">BP Systolic *</Label>
                      <Input
                        id="bpSystolic"
                        type="number"
                        min="70"
                        max="250"
                        value={formData.bloodPressureSystolic}
                        onChange={(e) => setFormData({ ...formData, bloodPressureSystolic: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="bpDiastolic">BP Diastolic *</Label>
                      <Input
                        id="bpDiastolic"
                        type="number"
                        min="40"
                        max="150"
                        value={formData.bloodPressureDiastolic}
                        onChange={(e) => setFormData({ ...formData, bloodPressureDiastolic: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="respiratory">Respiratory Rate (/min) *</Label>
                      <Input
                        id="respiratory"
                        type="number"
                        min="8"
                        max="60"
                        value={formData.respiratoryRatePerMin}
                        onChange={(e) => setFormData({ ...formData, respiratoryRatePerMin: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="oxygen">O2 Saturation (%) *</Label>
                      <Input
                        id="oxygen"
                        type="number"
                        step="0.1"
                        min="70"
                        max="100"
                        value={formData.oxygenSaturationPercent}
                        onChange={(e) => setFormData({ ...formData, oxygenSaturationPercent: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="weight">Weight (kg) *</Label>
                      <Input
                        id="weight"
                        type="number"
                        step="0.1"
                        min="0.1"
                        value={formData.weightKg}
                        onChange={(e) => setFormData({ ...formData, weightKg: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="height">Height (cm) *</Label>
                      <Input
                        id="height"
                        type="number"
                        min="30"
                        value={formData.heightCm}
                        onChange={(e) => setFormData({ ...formData, heightCm: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Assessment */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Assessment</h3>
                  <div>
                    <Label htmlFor="chiefComplaint">Chief Complaint</Label>
                    <Textarea
                      id="chiefComplaint"
                      value={formData.chiefComplaint}
                      onChange={(e) => setFormData({ ...formData, chiefComplaint: e.target.value })}
                      rows={2}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="generalCondition">General Condition</Label>
                      <Input
                        id="generalCondition"
                        value={formData.generalCondition}
                        onChange={(e) => setFormData({ ...formData, generalCondition: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="consciousnessLevel">Consciousness Level</Label>
                      <Input
                        id="consciousnessLevel"
                        value={formData.consciousnessLevel}
                        onChange={(e) => setFormData({ ...formData, consciousnessLevel: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="skinCondition">Skin Condition</Label>
                      <Input
                        id="skinCondition"
                        value={formData.skinCondition}
                        onChange={(e) => setFormData({ ...formData, skinCondition: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="mobilityStatus">Mobility Status</Label>
                      <Input
                        id="mobilityStatus"
                        value={formData.mobilityStatus}
                        onChange={(e) => setFormData({ ...formData, mobilityStatus: e.target.value })}
                      />
                    </div>
                  </div>
                </div>

                {/* Habits & History */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Habits & History</h3>
                  <div className="flex items-center space-x-4">
                    <Checkbox
                      id="smoker"
                      checked={formData.isSmoker}
                      onCheckedChange={(checked) => setFormData({ ...formData, isSmoker: Boolean(checked) })}
                    />
                    <Label htmlFor="smoker">Smoker</Label>
                  </div>
                  <div className="flex items-center space-x-4">
                    <Checkbox
                      id="allergies"
                      checked={formData.hasAllergies}
                      onCheckedChange={(checked) => setFormData({ ...formData, hasAllergies: Boolean(checked) })}
                    />
                    <Label htmlFor="allergies">Has Allergies</Label>
                  </div>
                </div>

                {/* Nutrition */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Nutrition</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="dietType">Diet Type</Label>
                      <Select 
                        value={formData.dietType} 
                        onValueChange={(value) => setFormData({ ...formData, dietType: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="regular">Regular</SelectItem>
                          <SelectItem value="diabetic">Diabetic</SelectItem>
                          <SelectItem value="low-sodium">Low Sodium</SelectItem>
                          <SelectItem value="low-fat">Low Fat</SelectItem>
                          <SelectItem value="vegetarian">Vegetarian</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="appetite">Appetite</Label>
                      <Select 
                        value={formData.appetite} 
                        onValueChange={(value) => setFormData({ ...formData, appetite: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="good">Good</SelectItem>
                          <SelectItem value="fair">Fair</SelectItem>
                          <SelectItem value="poor">Poor</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>

                {/* Functional Status */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Functional Status</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="feedingStatus">Feeding Status</Label>
                      <Select 
                        value={formData.feedingStatus} 
                        onValueChange={(value) => setFormData({ ...formData, feedingStatus: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="independent">Independent</SelectItem>
                          <SelectItem value="assistance">Needs Assistance</SelectItem>
                          <SelectItem value="dependent">Dependent</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="hygieneStatus">Hygiene Status</Label>
                      <Select 
                        value={formData.hygieneStatus} 
                        onValueChange={(value) => setFormData({ ...formData, hygieneStatus: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="independent">Independent</SelectItem>
                          <SelectItem value="assistance">Needs Assistance</SelectItem>
                          <SelectItem value="dependent">Dependent</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="toiletingStatus">Toileting Status</Label>
                      <Select 
                        value={formData.toiletingStatus} 
                        onValueChange={(value) => setFormData({ ...formData, toiletingStatus: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="independent">Independent</SelectItem>
                          <SelectItem value="assistance">Needs Assistance</SelectItem>
                          <SelectItem value="dependent">Dependent</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="ambulationStatus">Ambulation Status</Label>
                      <Select 
                        value={formData.ambulationStatus} 
                        onValueChange={(value) => setFormData({ ...formData, ambulationStatus: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="independent">Independent</SelectItem>
                          <SelectItem value="assistance">Needs Assistance</SelectItem>
                          <SelectItem value="dependent">Dependent</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>

                {/* Pain & Risk Assessment */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Pain & Risk Assessment</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="painIntensity">Pain Intensity (0-10)</Label>
                      <Select 
                        value={formData.painIntensity} 
                        onValueChange={(value) => setFormData({ ...formData, painIntensity: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {[0,1,2,3,4,5,6,7,8,9,10].map(num => (
                            <SelectItem key={num} value={num.toString()}>{num}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="dailyActivities">Daily Activities</Label>
                      <Select 
                        value={formData.dailyActivities} 
                        onValueChange={(value) => setFormData({ ...formData, dailyActivities: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="independent">Independent</SelectItem>
                          <SelectItem value="assistance">Needs Assistance</SelectItem>
                          <SelectItem value="dependent">Dependent</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="fallHistory"
                        checked={formData.fallHistory3months}
                        onCheckedChange={(checked) => setFormData({ ...formData, fallHistory3months: Boolean(checked) })}
                      />
                      <Label htmlFor="fallHistory">Fall History (last 3 months)</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="secondaryDiagnosis"
                        checked={formData.secondaryDiagnosis}
                        onCheckedChange={(checked) => setFormData({ ...formData, secondaryDiagnosis: Boolean(checked) })}
                      />
                      <Label htmlFor="secondaryDiagnosis">Secondary Diagnosis</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="ivTherapy"
                        checked={formData.ivTherapy}
                        onCheckedChange={(checked) => setFormData({ ...formData, ivTherapy: Boolean(checked) })}
                      />
                      <Label htmlFor="ivTherapy">IV Therapy</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="medicationEducation"
                        checked={formData.needsMedicationEducation}
                        onCheckedChange={(checked) => setFormData({ ...formData, needsMedicationEducation: Boolean(checked) })}
                      />
                      <Label htmlFor="medicationEducation">Needs Medication Education</Label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Checkbox
                        id="signsOfAbuse"
                        checked={formData.hasSignsOfAbuse}
                        onCheckedChange={(checked) => setFormData({ ...formData, hasSignsOfAbuse: Boolean(checked) })}
                      />
                      <Label htmlFor="signsOfAbuse">Signs of Abuse</Label>
                    </div>
                  </div>
                </div>

                {/* Educational Need Assessment */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Educational Need Assessment</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {[
                      "No needs identified",
                      "Use of Medication",
                      "Diet and Nutrition",
                      "Use of Medical Equipment",
                      "Rehabilitation Techniques",
                      "Potential Interactions Between Medication",
                      "Pain and Other Symptoms",
                      "Moderate/High Risk for Falling",
                      "Other"
                    ].map((need) => (
                      <div key={need} className="flex items-center space-x-2">
                        <Checkbox
                          id={`edu-${need}`}
                          checked={formData.educationalNeeds.includes(need)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setFormData({
                                ...formData,
                                educationalNeeds: [...formData.educationalNeeds, need]
                              })
                            } else {
                              setFormData({
                                ...formData,
                                educationalNeeds: formData.educationalNeeds.filter(n => n !== need)
                              })
                            }
                          }}
                        />
                        <Label htmlFor={`edu-${need}`} className="text-sm">{need}</Label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Pain Assessment */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Pain Assessment</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="painIntensity">Pain Intensity (0-10)</Label>
                      <Select value={formData.painIntensity} onValueChange={(value) => setFormData({ ...formData, painIntensity: value })}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {Array.from({ length: 11 }, (_, i) => (
                            <SelectItem key={i} value={i.toString()}>{i}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="painLocation">Location</Label>
                      <Input
                        id="painLocation"
                        value={formData.painLocation}
                        onChange={(e) => setFormData({ ...formData, painLocation: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="painFrequency">Frequency</Label>
                      <Input
                        id="painFrequency"
                        value={formData.painFrequency}
                        onChange={(e) => setFormData({ ...formData, painFrequency: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="painDuration">Duration</Label>
                      <Input
                        id="painDuration"
                        value={formData.painDuration}
                        onChange={(e) => setFormData({ ...formData, painDuration: e.target.value })}
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="painCharacter">Character</Label>
                    <Input
                      id="painCharacter"
                      value={formData.painCharacter}
                      onChange={(e) => setFormData({ ...formData, painCharacter: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="painActionTaken">Action Taken</Label>
                    <Textarea
                      id="painActionTaken"
                      value={formData.painActionTaken}
                      onChange={(e) => setFormData({ ...formData, painActionTaken: e.target.value })}
                      rows={2}
                    />
                  </div>
                </div>

                {/* Fall Assessment - Morse Scale */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Fall Assessment (Morse Scale)</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <h4 className="font-medium">Risk Factors:</h4>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Fall history (last 3 months)</span>
                          <div className="flex items-center space-x-2">
                            <Checkbox
                              id="fallHistory"
                              checked={formData.fallHistory3months}
                              onCheckedChange={(checked) => {
                                setFormData({ ...formData, fallHistory3months: Boolean(checked) })
                                calculateMorseScore()
                              }}
                            />
                            <span className="text-sm text-gray-600">25 points</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Secondary diagnosis</span>
                          <div className="flex items-center space-x-2">
                            <Checkbox
                              id="secondaryDiagnosis"
                              checked={formData.secondaryDiagnosis}
                              onCheckedChange={(checked) => {
                                setFormData({ ...formData, secondaryDiagnosis: Boolean(checked) })
                                calculateMorseScore()
                              }}
                            />
                            <span className="text-sm text-gray-600">15 points</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">IV therapy</span>
                          <div className="flex items-center space-x-2">
                            <Checkbox
                              id="ivTherapy"
                              checked={formData.ivTherapy}
                              onCheckedChange={(checked) => {
                                setFormData({ ...formData, ivTherapy: Boolean(checked) })
                                calculateMorseScore()
                              }}
                            />
                            <span className="text-sm text-gray-600">20 points</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Ambulation aid</span>
                          <div className="flex items-center space-x-2">
                            <Select onValueChange={(value) => {
                              // Handle ambulation aid selection
                              calculateMorseScore()
                            }}>
                              <SelectTrigger className="w-32">
                                <SelectValue placeholder="Select" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="none">None (0)</SelectItem>
                                <SelectItem value="crutches">Crutches (30)</SelectItem>
                                <SelectItem value="walker">Walker (30)</SelectItem>
                                <SelectItem value="furniture">Furniture (30)</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <h4 className="font-medium">Total Score: {formData.morseFallScore}</h4>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <div className={`w-3 h-3 rounded-full ${formData.morseFallScore <= 24 ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                          <span className="text-sm">Low Risk (0-24)</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className={`w-3 h-3 rounded-full ${formData.morseFallScore >= 25 && formData.morseFallScore <= 49 ? 'bg-yellow-500' : 'bg-gray-300'}`}></div>
                          <span className="text-sm">Moderate Risk (25-49)</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className={`w-3 h-3 rounded-full ${formData.morseFallScore >= 50 ? 'bg-red-500' : 'bg-gray-300'}`}></div>
                          <span className="text-sm">High Risk (50+)</span>
                        </div>
                      </div>
                      <div className="mt-4 p-3 bg-gray-50 rounded-md">
                        <h5 className="font-medium text-sm mb-2">Prevention Measures:</h5>
                        <ul className="text-xs space-y-1">
                          <li>• Educate patient and family about fall risks</li>
                          <li>• Keep mobile equipment with wheels locked</li>
                          <li>• Patient wears yellow bracelet with "F" during center stay</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Elderly Assessment */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Elderly Assessment</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>Daily Activities</Label>
                      <Select value={formData.elderlyDailyActivities} onValueChange={(value) => setFormData({ ...formData, elderlyDailyActivities: value })}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="independent">Independent</SelectItem>
                          <SelectItem value="needs_help">Needs Help</SelectItem>
                          <SelectItem value="depends_on_others">Depends on Others</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Cognitive Assessment</Label>
                      <Select value={formData.elderlyCognitiveAssessment} onValueChange={(value) => setFormData({ ...formData, elderlyCognitiveAssessment: value })}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="normal">Normal</SelectItem>
                          <SelectItem value="mild_delirium">Mild Delirium</SelectItem>
                          <SelectItem value="moderate_impairment">Moderate Impairment</SelectItem>
                          <SelectItem value="severe_delirium">Severe Delirium</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Mood Assessment</Label>
                      <Select value={formData.elderlyMoodAssessment} onValueChange={(value) => setFormData({ ...formData, elderlyMoodAssessment: value })}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="normal">Normal</SelectItem>
                          <SelectItem value="depressed">Depressed</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      { id: "speech", label: "Speech Disorder", field: "elderlySpeechDisorder" },
                      { id: "hearing", label: "Hearing Disorder", field: "elderlyHearingDisorder" },
                      { id: "vision", label: "Vision Disorder", field: "elderlyVisionDisorder" },
                      { id: "sleep", label: "Sleep Disorder", field: "elderlySleepDisorder" }
                    ].map((item) => (
                      <div key={item.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={item.id}
                          checked={formData[item.field as keyof typeof formData] as boolean}
                          onCheckedChange={(checked) => setFormData({ ...formData, [item.field]: Boolean(checked) })}
                        />
                        <Label htmlFor={item.id} className="text-sm">{item.label}</Label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Disabled Patients Assessment */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Disabled Patients Assessment</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>Disability Type</Label>
                      <Select value={formData.disabilityType} onValueChange={(value) => setFormData({ ...formData, disabilityType: value })}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">Select Type</SelectItem>
                          <SelectItem value="hearing">Hearing</SelectItem>
                          <SelectItem value="vision">Vision</SelectItem>
                          <SelectItem value="mobility">Mobility</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="assistiveDevices"
                        checked={formData.hasAssistiveDevices}
                        onCheckedChange={(checked) => setFormData({ ...formData, hasAssistiveDevices: Boolean(checked) })}
                      />
                      <Label htmlFor="assistiveDevices">Has Assistive Devices</Label>
                    </div>
                  </div>
                </div>

                {/* Abuse/Neglect Assessment */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Abuse/Neglect Assessment</h3>
                  <div className="flex items-center space-x-4">
                    <Checkbox
                      id="abuseNeglect"
                      checked={formData.hasAbuseNeglect}
                      onCheckedChange={(checked) => setFormData({ ...formData, hasAbuseNeglect: Boolean(checked) })}
                    />
                    <Label htmlFor="abuseNeglect">Signs of Abuse/Neglect Identified</Label>
                  </div>
                  {formData.hasAbuseNeglect && (
                    <div>
                      <Label htmlFor="abuseDetails">Details</Label>
                      <Textarea
                        id="abuseDetails"
                        value={formData.abuseNeglectDetails}
                        onChange={(e) => setFormData({ ...formData, abuseNeglectDetails: e.target.value })}
                        rows={3}
                        placeholder="Please describe the signs of abuse/neglect..."
                      />
                    </div>
                  )}
                </div>

                {/* Signature */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium border-b pb-2">Nurse Signature</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="nurseSignature">Nurse Name</Label>
                      <Input
                        id="nurseSignature"
                        value={formData.nurseSignature}
                        onChange={(e) => setFormData({ ...formData, nurseSignature: e.target.value })}
                        placeholder="Enter your full name"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="assessmentDate">Date</Label>
                      <Input
                        id="assessmentDate"
                        type="date"
                        value={formData.assessmentDate}
                        onChange={(e) => setFormData({ ...formData, assessmentDate: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="assessmentTime">Time</Label>
                      <Input
                        id="assessmentTime"
                        type="time"
                        value={formData.assessmentTime}
                        onChange={(e) => setFormData({ ...formData, assessmentTime: e.target.value })}
                        required
                      />
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