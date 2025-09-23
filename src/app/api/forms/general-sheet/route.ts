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

    if (!formData.findings || formData.findings.trim() === "") {
      return NextResponse.json(
        { detail: "Findings are required" },
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
    const existingForm = await db.generalSheetForm.findUnique({
      where: { visitId },
    })

    if (existingForm) {
      return NextResponse.json(
        { detail: "General Sheet form already exists for this visit" },
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

    // Create General Sheet form
    const generalSheetForm = await db.generalSheetForm.create({
      data: {
        visitId,
        userId: formData.userId || userId, // Use provided userId or fallback to token
        diagnosis: formData.diagnosis || null,
        reasonForStudy: formData.reasonForStudy || null,
        findings: formData.findings,
        impression: formData.impression || null,
        recommendations: formData.recommendations || null,
        modality: formData.modality || null,
        bodyRegion: formData.bodyRegion || null,
        hasChronicDisease: formData.hasChronicDisease || false,
        hasPacemaker: formData.hasPacemaker || false,
        isPregnant: formData.isPregnant || false,
        hasPainNumbness: formData.hasPainNumbness || false,
        hasSpinalDeformities: formData.hasSpinalDeformities || false,
        hasSwelling: formData.hasSwelling || false,
        hasHeadache: formData.hasHeadache || false,
        hasFever: formData.hasFever || false,
        hasTumorHistory: formData.hasTumorHistory || false,
        hasDiscSlip: formData.hasDiscSlip || false,
      },
    })

    return NextResponse.json(generalSheetForm, { status: 201 })
  } catch (error) {
    console.error("Error creating General Sheet form:", error)
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

    const generalSheetForm = await db.generalSheetForm.findUnique({
      where: { visitId },
    })

    if (!generalSheetForm) {
      return NextResponse.json(
        { detail: "General Sheet form not found" },
        { status: 404 }
      )
    }

    return NextResponse.json(generalSheetForm)
  } catch (error) {
    console.error("Error fetching General Sheet form:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}