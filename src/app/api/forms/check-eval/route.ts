import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { visitId, ...formData } = body

    // Validate required fields
    if (!visitId) {
      return NextResponse.json(
        { detail: "Visit ID is required" },
        { status: 400 }
      )
    }

    // Validate vital signs ranges
    const {
      temperatureCelsius,
      pulseBpm,
      bloodPressureSystolic,
      bloodPressureDiastolic,
      respiratoryRatePerMin,
      oxygenSaturationPercent,
      weightKg,
      heightCm,
    } = formData

    if (temperatureCelsius < 30 || temperatureCelsius > 45) {
      return NextResponse.json(
        { detail: "Temperature must be between 30-45°C" },
        { status: 400 }
      )
    }

    if (pulseBpm < 30 || pulseBpm > 200) {
      return NextResponse.json(
        { detail: "Pulse must be between 30-200 bpm" },
        { status: 400 }
      )
    }

    if (bloodPressureSystolic < 70 || bloodPressureSystolic > 250) {
      return NextResponse.json(
        { detail: "Systolic BP must be between 70-250 mmHg" },
        { status: 400 }
      )
    }

    if (bloodPressureDiastolic < 40 || bloodPressureDiastolic > 150) {
      return NextResponse.json(
        { detail: "Diastolic BP must be between 40-150 mmHg" },
        { status: 400 }
      )
    }

    if (respiratoryRatePerMin < 8 || respiratoryRatePerMin > 60) {
      return NextResponse.json(
        { detail: "Respiratory rate must be between 8-60/min" },
        { status: 400 }
      )
    }

    if (oxygenSaturationPercent < 70 || oxygenSaturationPercent > 100) {
      return NextResponse.json(
        { detail: "O2 saturation must be between 70-100%" },
        { status: 400 }
      )
    }

    if (weightKg <= 0) {
      return NextResponse.json(
        { detail: "Weight must be greater than 0" },
        { status: 400 }
      )
    }

    if (heightCm <= 0) {
      return NextResponse.json(
        { detail: "Height must be greater than 0" },
        { status: 400 }
      )
    }

    // Check if visit exists
    const visit = await db.visit.findUnique({
      where: { id: visitId },
    })

    if (!visit) {
      return NextResponse.json(
        { detail: "Visit not found" },
        { status: 404 }
      )
    }

    // Check if form already exists for this visit
    const existingForm = await db.checkEvalForm.findUnique({
      where: { visitId },
    })

    if (existingForm) {
      return NextResponse.json(
        { detail: "Check-Eval form already exists for this visit" },
        { status: 400 }
      )
    }

    // Get user from token
    const authHeader = request.headers.get("authorization")
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json(
        { detail: "Invalid authentication" },
        { status: 401 }
      )
    }

    const token = authHeader.substring(7)
    const userId = Buffer.from(token, 'base64').toString().split(':')[0]

    // Create Check-Eval form
    const checkEvalForm = await db.checkEvalForm.create({
      data: {
        visitId,
        userId: formData.userId || userId, // Use provided userId or fallback to token
        temperatureCelsius,
        pulseBpm,
        bloodPressureSystolic,
        bloodPressureDiastolic,
        respiratoryRatePerMin,
        oxygenSaturationPercent,
        weightKg,
        heightCm,
        chiefComplaint: formData.chiefComplaint || null,
        generalCondition: formData.generalCondition || null,
        consciousnessLevel: formData.consciousnessLevel || null,
        skinCondition: formData.skinCondition || null,
        mobilityStatus: formData.mobilityStatus || null,
        isSmoker: formData.isSmoker || false,
        hasAllergies: formData.hasAllergies || false,
        dietType: formData.dietType || "regular",
        appetite: formData.appetite || "good",
        feedingStatus: formData.feedingStatus || "independent",
        hygieneStatus: formData.hygieneStatus || "independent",
        toiletingStatus: formData.toiletingStatus || "independent",
        ambulationStatus: formData.ambulationStatus || "independent",
        painIntensity: formData.painIntensity || 0,
        painLocation: formData.painLocation || null,
        painFrequency: formData.painFrequency || null,
        painDuration: formData.painDuration || null,
        painCharacter: formData.painCharacter || null,
        painActionTaken: formData.painActionTaken || null,
        fallHistory3months: formData.fallHistory3months || false,
        secondaryDiagnosis: formData.secondaryDiagnosis || false,
        ivTherapy: formData.ivTherapy || false,
        needsMedicationEducation: formData.needsMedicationEducation || false,
        dailyActivities: formData.dailyActivities || "independent",
        hasSignsOfAbuse: formData.hasSignsOfAbuse || false,
        educationalNeeds: formData.educationalNeeds || null,
        morseFallScore: formData.morseFallScore || 0,
        fallRiskLevel: formData.fallRiskLevel || "low",
        elderlyDailyActivities: formData.elderlyDailyActivities || "independent",
        elderlyCognitiveAssessment: formData.elderlyCognitiveAssessment || "normal",
        elderlyMoodAssessment: formData.elderlyMoodAssessment || "normal",
        elderlySpeechDisorder: formData.elderlySpeechDisorder || false,
        elderlyHearingDisorder: formData.elderlyHearingDisorder || false,
        elderlyVisionDisorder: formData.elderlyVisionDisorder || false,
        elderlySleepDisorder: formData.elderlySleepDisorder || false,
        disabilityType: formData.disabilityType || null,
        hasAssistiveDevices: formData.hasAssistiveDevices || false,
        hasAbuseNeglect: formData.hasAbuseNeglect || false,
        abuseNeglectDetails: formData.abuseNeglectDetails || null,
        nurseSignature: formData.nurseSignature || null,
        assessmentDate: formData.assessmentDate || null,
        assessmentTime: formData.assessmentTime || null,
      },
    })

    return NextResponse.json(checkEvalForm, { status: 201 })
  } catch (error) {
    console.error("Error creating Check-Eval form:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: { visitId: string } }
) {
  try {
    const { searchParams } = new URL(request.url)
    const visitId = searchParams.get("visitId")

    if (!visitId) {
      return NextResponse.json(
        { detail: "Visit ID is required" },
        { status: 400 }
      )
    }

    const checkEvalForm = await db.checkEvalForm.findUnique({
      where: { visitId },
    })

    if (!checkEvalForm) {
      return NextResponse.json(
        { detail: "Check-Eval form not found" },
        { status: 404 }
      )
    }

    return NextResponse.json(checkEvalForm)
  } catch (error) {
    console.error("Error fetching Check-Eval form:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}